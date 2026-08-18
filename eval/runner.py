"""
AtmosCoder-Bench: Evaluate LLMs on atmospheric science computational problems.

The LLM sees ONLY the problem text (no textbook formulas, no expected answers).
Three answer protocols, graded identically (see ``eval.protocols``):
  --mode code    (default) the model writes a solve() function; we execute it.
  --mode direct  the model reasons in prose and reports its final \\boxed{} number(s).
  --mode agent   the model iterates in a code interpreter (runs code, sees output,
                 refines) and calls submit() with the final answer.
`num_attempts` counts only CONTENT-generation tries — for code/direct, the model's own
output being ungradable (code won't run / no code; direct produced no \\boxed{}),
fed back so the model can fix it (self-repair) up to a per-protocol limit (code 5,
direct 5); for agent, the number of interpreter turns used (cap 10). Still
ungradable after the budget -> FAIL. API/infra errors are not the model's fault:
blindly retried, uncounted, and an excluded error only if they never clear.

Usage (run as a module from the repo root; runs the full set unless --n samples):
    uv run python -m eval.runner --model gemini --set core
    uv run python -m eval.runner --model gemini --set core --mode direct --exp-id g_direct
    uv run python -m eval.runner --model gemini --set variants_numeric --exp-id exp1
    uv run python -m eval.runner --model gemini --set core --n 200
"""

import copy
import json
import random
import argparse
import concurrent.futures
from datetime import datetime
from pathlib import Path

from eval.engine import verify_solver
from eval.store import ExperimentStore
from eval.datasets import SETS, dataset_path
from eval.protocols import PROTOCOLS, Protocol, SYSTEM_PRESETS, PROMPT_PRESETS
from eval.models import Model, load_config, build_model, ModelError, PromptTooLongError


def evaluate_one(problem: dict, model: Model, protocol: Protocol,
                 tolerance: float = 0.05, budget: int | None = None) -> dict:
    """Evaluate the model on a single problem under one answer protocol.

    The protocol's ``run_episode`` owns the full interaction (a single generate for
    code/direct; a multi-turn code-interpreter loop for agent) and absorbs transient
    API errors internally. What it returns is graded here:
      - gradable answer        -> pass, or a definitive wrong-but-runnable fail.
      - content failure        -> the model never produced a gradable answer within
                                  its budget -> FAIL (a real failure to deliver).
      - PromptTooLong / stuck API error -> excluded error (not the model's fault).
    `num_attempts` is content-generation tries (code/direct) or turns used (agent);
    ``attempts`` logs each stateless call (prompt, response, outcome, per-call ``usage``)
    for review — not a chat transcript (repair re-prompts single-turn)."""
    try:
        episode = protocol.run_episode(model, problem, budget)
    except PromptTooLongError as exc:   # deterministic — retrying cannot help
        error = f"prompt too long: {exc}"
    except ModelError as exc:           # transient API/infra error that never cleared
        error = str(exc)
    else:
        outcome = episode.attempt
        if outcome.error:               # ungradable content -> the model failed to deliver
            record = {"id": problem["id"], "passed": False,
                      "num_attempts": len(episode.attempts), "failed_reason": outcome.error}
        else:
            passed, details = verify_solver(outcome.results, problem["sub_answers"], tolerance)
            record = {"id": problem["id"], "passed": passed, "details": details,
                      "num_attempts": len(episode.attempts)}
        if episode.note:
            record["note"] = episode.note
        # ``attempts`` is a per-call log (each a stateless single-turn request), not a
        # chat history. ``system`` is constant across calls and stored once in the
        # experiment metrics, so it is not repeated per record.
        record.update({"usage": episode.usage, "attempts": episode.attempts})
        return record
    # API/infra failure before any gradable content attempt completed.
    return {"id": problem["id"], "passed": False, "num_attempts": 0, "error": error[:200],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "reasoning_tokens": 0},
            "attempts": []}


def main():
    parser = argparse.ArgumentParser(
        description="AtmosCoder-Bench: evaluate LLMs on atmospheric science problems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", required=True, help="Model name from models.toml")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--set", dest="dataset", choices=list(SETS),
                        help="Which benchmark set to evaluate "
                             "(base / variants_numeric / variants_paraphrase)")
    source.add_argument("--input", help="Path to an external problems json "
                                        "({id, problem, sub_answers}); for sets outside benchmark/")
    parser.add_argument("--mode", choices=list(PROTOCOLS), default="code",
                        help="Answer protocol: 'code' (write & execute solve()) or "
                             "'direct' (reason in prose, report \\boxed{} numbers). Default: code")
    parser.add_argument("--system", default=None,
                        help="Override the system prompt for this run: a preset name from "
                             "protocols.SYSTEM_PRESETS (e.g. 'expert', 'coder') or a literal "
                             "string. Default keeps the protocol's own system. Recorded in metrics.")
    parser.add_argument("--prompt", default=None,
                        help="Override the code user-prompt template for this run: a preset name "
                             "from protocols.PROMPT_PRESETS ('original' or 'restrictive') or a literal "
                             "string. For prompt-segment ablation (code mode). Recorded in metrics.")
    parser.add_argument("--exp-id", default=None, help="Experiment identifier (default: {model}_{mode}_{date})")
    parser.add_argument("--out-name", default=None,
                        help="Override the output file's model name (default: --model). Lets two "
                             "configs that are the SAME logical model on different endpoints "
                             "(e.g. kimi-k2.6-reasoning vs kimi-k2.6-reasoning-internal) write to and "
                             "resume the SAME result file. Grading/records are unchanged.")
    parser.add_argument("--n", type=int, default=None,
                        help="Sample N random problems (default: run all)")
    parser.add_argument("--ids", nargs="+", default=None,
                        help="Re-run ONLY these problem ids and MERGE them into the existing "
                             "result file (creating it if absent): each target id's prior record "
                             "is dropped and replaced by a fresh run, all other results are kept, "
                             "and the aggregate metrics (counts/accuracy/tokens) are recomputed so "
                             "the file is identical to having run that final id set. Ignores --n.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run", type=int, default=None,
                        help="Repetition index for repeated runs of the same model+exp-id. "
                             "Writes to {model_id}.run{N}.json (default {model_id}.json) and "
                             "offsets the sample seed by N so each rep is independent. Use to "
                             "measure run-to-run variance / pass@k.")
    parser.add_argument("--tolerance", type=float, default=0.05)
    parser.add_argument("--no-skip", action="store_true", help="Re-run even if results exist")
    parser.add_argument("--max-attempts", type=int, default=None,
                        help="Override the per-protocol budget: content tries for code/direct "
                             "(default 5 each), or interpreter turns for agent (default 10)")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers")
    parser.add_argument("--thinking", choices=["on", "off"], default="on",
                        help="Thinking toggle for configs that define one (default: on)")
    args = parser.parse_args()

    cfg = load_config(args.model)
    model_id = cfg.get("model_id") or cfg.get("api_model")
    model = build_model(cfg, thinking_mode=args.thinking)
    protocol = PROTOCOLS[args.mode]
    if args.system or args.prompt:  # optional prompt overrides for controlled ablations
        protocol = copy.copy(protocol)  # shallow copy so the shared singleton is untouched
        if args.system:
            protocol.system = SYSTEM_PRESETS.get(args.system, args.system)
        if args.prompt:
            protocol.prompt_template = PROMPT_PRESETS.get(args.prompt, args.prompt)

    # Load problems
    source_path = dataset_path(args.dataset) if args.dataset else Path(args.input)
    problems = json.loads(source_path.read_text())
    if args.ids:  # selective re-run: restrict to exactly these ids (merge-replace into the file)
        wanted = list(dict.fromkeys(args.ids))  # dedupe, preserve order
        by_id = {p["id"]: p for p in problems}
        missing = [i for i in wanted if i not in by_id]
        if missing:
            print(f"WARNING: {len(missing)} id(s) not in {args.dataset or args.input}: {missing}")
        problems = [by_id[i] for i in wanted if i in by_id]
        if not problems:
            print("No matching ids to run.")
            return
    elif args.n:  # optional random subsample; default is the full set
        random.seed(args.seed + (args.run or 0))  # per-rep seed so repeated runs sample differently
        problems = random.sample(problems, min(args.n, len(problems)))

    # Output store: streams every result to disk (real-time), resumes by skipping
    # already-PASSED items, and writes atomically so a kill never corrupts the file.
    exp_id = args.exp_id or f"{args.model}_{args.mode}_{datetime.now().strftime('%Y%m%d')}"
    out_dir = Path(f"experiments/{exp_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    # Name the file by the TOML key (args.model): it's the unique, user-chosen id.
    # model_id can be shared by several configs (e.g. gpt54 and gpt54-reasoning both
    # map to "gpt-5.4"), so naming by model_id would collide; the key never does.
    safe_id = (args.out_name or args.model).replace("/", "--")
    out_path = out_dir / (f"{safe_id}.run{args.run}.json" if args.run is not None
                          else f"{safe_id}.json")
    meta = {"model": args.out_name or args.model, "model_id": model_id, "exp_id": exp_id,
            "mode": args.mode, "tolerance": args.tolerance, "system": protocol.system}
    if args.run is not None:  # only stamp the rep index for actual repeated runs
        meta["run"] = args.run
    # --ids -> selective merge-replace (preserve other results, drop+rerun the targets);
    # otherwise normal resume (keep passes) unless --no-skip.
    store = ExperimentStore(out_path, resume=not args.no_skip, meta=meta,
                            replace_ids={p["id"] for p in problems} if args.ids else None)

    remaining = [problem for problem in problems if problem.get("id") not in store.done_ids]
    if not remaining:
        print(f"All {len(problems)} problems complete. Use --no-skip to re-run.")
        return

    print(f"Model:    {model_id} {'(reasoning)' if cfg.get('reasoning') else ''}")
    print(f"Exp ID:   {exp_id}{f' (run {args.run})' if args.run is not None else ''}")
    print(f"Mode:     {args.mode}")
    print(f"Workers:  {args.workers}")
    print(f"Problems: {len(remaining)} remaining / {len(problems)} total")
    print(f"Output:   {out_path}\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(evaluate_one, problem, model, protocol, args.tolerance, args.max_attempts)
                   for problem in remaining]  # args.max_attempts -> per-episode budget
        for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            store.add(result)  # appends, flushes atomically (recomputes all metrics)
            status = ("PASS" if result["passed"] else
                      f"ERROR: {result['error'][:50]}" if result.get("error") else "FAIL")
            tries = f" (x{result['num_attempts']})" if result.get("num_attempts", 1) > 1 else ""
            print(f"[{done}/{len(remaining)}] {result['id']}... {status}{tries}")  # progress over this session's work

    counts = store.counts()
    denominator = counts["passed"] + counts["failed"]
    accuracy = counts["passed"] / denominator if denominator else 0
    print(f"\n{'='*50}")
    print(f"Accuracy: {counts['passed']}/{denominator} ({accuracy:.1%}) "
          f"[errors excluded: {counts['errors']}]")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
