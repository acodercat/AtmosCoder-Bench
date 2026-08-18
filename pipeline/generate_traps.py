"""Generate trap-problem CANDIDATES from core problems with an LLM, then gate them
deterministically. gpt55 proposes, the engine filters, a human (Claude) adjudicates.

For each core problem the model is shown the text + its reference solver + answer, and
asked to propose ONE minimal "trap": change a single trigger so the core problem's own
method becomes an incorrect SHORTCUT, while correct physics gives a different number
(>10% apart). The core problem is the built-in CONTROL (its method is correct in its own
regime). The model returns strict JSON; we then RUN both the correct and shortcut solvers
and record the separation, so the output file already flags which candidates clear the
objective gate. Nothing is added to benchmark/ — this only writes a candidates report.

    uv run python -m pipeline.generate_traps --n 40 --workers 6
    uv run python -m pipeline.generate_traps --all --model gpt55-reasoning
    uv run python -m pipeline.generate_traps --ids air_203 air_170 2.14

Output: pipeline/reports/trap_candidates.json  (one record per core problem attempted).
"""

import json
import re
import random
import argparse
import threading
import concurrent.futures
from pathlib import Path
from collections import Counter

from eval.engine import run_solver
from eval.models.registry import load_config, build_model

BASE = Path("benchmark/core.json")
OUT = Path("pipeline/reports/trap_candidates.json")
SEP_MIN = 0.10          # objective gate: correct vs shortcut must differ by > this
DEFAULT_MODEL = "gpt55-reasoning"

SYSTEM = (
    "You are an expert atmospheric-science problem designer building diagnostic 'trap' "
    "problems that reveal whether a model reasons from physics or pattern-matches a "
    "memorized template. You are meticulous, quantitative, and honest: if a problem admits "
    "no clean trap you say so rather than inventing a weak one."
)

# Worked example (few-shot) so the model learns the exact bar and JSON shape.
EXAMPLE = """EXAMPLE (for a base geostrophic-wind problem whose solver computes V_g = (g/f_c)(dz/dx)):
{
  "has_trap": true,
  "trap_type": "formula_selection",
  "trigger": "the flow curves cyclonically around a low with a finite radius of curvature (base assumes straight flow)",
  "problem": "Air flows CYCLONICALLY around a low-pressure center where the geopotential height increases by 50 m per 200 km toward the east, with Coriolis parameter f_c = 0.9e-4 s^-1 and a radius of curvature of 200 km. Find the actual (gradient) wind speed. Express your answer in m/s.",
  "correct_code": "def solve(delta_z=50.0, delta_x_km=200.0, f_c=0.9e-4, R_km=200.0):\\n    import math\\n    g=9.8\\n    Vg=(g/f_c)*(delta_z/(delta_x_km*1000.0)); R=R_km*1000.0\\n    V=(-f_c+math.sqrt(f_c*f_c+4*f_c*Vg/R))*R/2\\n    return {\\"1\\": {\\"value\\": V, \\"unit\\": \\"m/s\\"}}",
  "shortcut_code": "def solve(delta_z=50.0, delta_x_km=200.0, f_c=0.9e-4):\\n    g=9.8\\n    return {\\"1\\": {\\"value\\": (g/f_c)*(delta_z/(delta_x_km*1000.0)), \\"unit\\": \\"m/s\\"}}",
  "shortcut_desc": "geostrophic wind (the base method), which ignores the curvature term",
  "expected_correct": 14.9,
  "expected_shortcut": 27.2,
  "rationale": "Curvature makes the gradient wind subgeostrophic around a low; a template-matcher reports the geostrophic value."
}"""

PROMPT = """Below is a base atmospheric-science problem, its reference solver, and its verified answer.

## Base problem
{problem}

## Reference solver (the CANONICAL method — correct in this problem's regime)
{code}

## Verified answer
{answer}

## Your task
Propose ONE *minimal* trap derived from this core problem, or declare that none is clean.

A trap = change a SINGLE physical trigger (a value pushed across a regime boundary, a stated
condition, a phase, a units/geometry detail) so that the core problem's OWN method becomes an
incorrect SHORTCUT, while the physically-correct method gives a DIFFERENT number. The unchanged
core problem is the control (its method is right in its own regime), so:

- `shortcut_code` MUST be essentially the base's method (it should reproduce the base's style of
  answer); it is what a model on autopilot would do.
- `correct_code` applies the physics the trigger now demands.
- The two must differ by MORE THAN 10% at the trap's inputs (bigger is better). If you cannot
  reach >10%, set "has_trap": false.

Hard requirements:
- MINIMAL edit: keep the base scenario, wording, and all unrelated numbers; change essentially
  one trigger. Do NOT announce that it is a trap; the text must read as an ordinary problem.
- SELF-CONTAINED: every value `correct_code` uses must appear in your `problem` text (physical
  constants excepted). No hidden inputs.
- Both solvers: a Python `def solve(...)` with every given value a defaulted parameter, standard
  library only, explicit unit conversions, returning dict {{"1": {{"value": <number>, "unit": <str>}}}}.
- FAIR, not a gotcha: a careful expert who knows the physics gets `correct_code`'s answer.
- Prefer these trap families: formula_selection, regime_boundary, unit_convention,
  sign_direction, averaging_space, definition_confusion, distractor.
  (For a distractor: add one irrelevant quantity, keep the answer unchanged, set shortcut_code
  to null and expected_shortcut to null.)

{example}

Respond with ONLY the JSON object (same fields as the example: has_trap, trap_type, trigger,
problem, correct_code, shortcut_code, shortcut_desc, expected_correct, expected_shortcut,
rationale). If no clean trap exists, return {{"has_trap": false, "reason": "<why>"}}."""


def _parse(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"has_trap": False, "reason": "PARSE_ERROR", "raw": text[:300]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"has_trap": False, "reason": "PARSE_ERROR", "raw": text[:300]}


def _num(res):
    """First numeric value from a solver result dict, else None."""
    if not isinstance(res, dict):
        return None
    for v in res.values():
        if isinstance(v, dict) and isinstance(v.get("value"), (int, float)):
            return v["value"]
    return None


def _vals(res):
    """{sub: numeric value} for every sub of a solver result dict."""
    if not isinstance(res, dict):
        return {}
    return {k: v["value"] for k, v in res.items()
            if isinstance(v, dict) and isinstance(v.get("value"), (int, float))}


def _first_sub(res):
    """The sub key `_num` reads, so the scalar is self-describing."""
    return next(iter(_vals(res)), None)


def gate(cand):
    """Deterministically run correct + shortcut solvers and score separation.

    Returns a verdict dict merged into the candidate. `separation` is the relative gap on
    the first sub-answer; `shortcut_values` / `correct_values` carry every sub, which is
    what a capture test must compare against."""
    if not cand.get("has_trap"):
        return {"gate": "no_trap"}
    cc = cand.get("correct_code") or ""
    ok_c, res_c, err_c = run_solver(cc)
    corr = _num(res_c) if ok_c else None
    if corr is None:
        return {"gate": "CORRECT_SOLVER_FAILED", "gate_detail": (err_c or "no numeric")[:200]}
    if cand.get("trap_type") == "distractor" or not cand.get("shortcut_code"):
        return {"gate": "PASS_DISTRACTOR", "correct_val": corr, "separation": None}
    ok_s, res_s, err_s = run_solver(cand["shortcut_code"])
    short = _num(res_s) if ok_s else None
    if short is None:
        return {"gate": "SHORTCUT_SOLVER_FAILED", "gate_detail": (err_s or "no numeric")[:200], "correct_val": corr}
    sep = abs(corr - short) / max(abs(corr), 1e-15)
    # `separation` is the FIRST sub-answer's relative gap (that is what `_num` reads), not a
    # max over subs. For multi-sub traps the two differ, so the full vectors are emitted too
    # and downstream capture tests must use `shortcut_values` rather than the scalar --
    # see docs/results/TRAP_RESULTS.md Table 4.
    return {"gate": "PASS" if sep > SEP_MIN else "SEP_TOO_SMALL",
            "correct_val": corr, "shortcut_val": short, "separation": round(sep, 4),
            "shortcut_sub": _first_sub(res_s),
            "shortcut_values": _vals(res_s), "correct_values": _vals(res_c)}


def process(problem, model):
    prompt = PROMPT.format(problem=problem["problem"], code=problem["code"],
                           answer=json.dumps(problem["sub_answers"], ensure_ascii=False),
                           example=EXAMPLE)
    try:
        cand = _parse(model.generate(prompt, SYSTEM).text)
    except Exception as e:
        cand = {"has_trap": False, "reason": "MODEL_ERROR", "raw": str(e)[:200]}
    rec = {"parent_id": problem["id"], "parent_category": problem.get("category"), **cand}
    rec.update(gate(cand))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40, help="random sample size (ignored with --all/--ids)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ids", nargs="+")
    ap.add_argument("--seed", type=int, default=20260704)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    base = json.load(open(BASE))
    by_id = {p["id"]: p for p in base}
    if args.ids:
        sample = [by_id[i] for i in args.ids if i in by_id]
    elif args.all:
        sample = base
    else:
        sample = random.Random(args.seed).sample(base, min(args.n, len(base)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = {r["parent_id"]: r for r in json.load(open(OUT))} if OUT.exists() else {}
    todo = [p for p in sample if p["id"] not in done]
    print(f"generate_traps: {len(sample)} sampled, {len(done)} cached, {len(todo)} to run | model={args.model}")

    model = build_model(load_config(args.model))
    results = dict(done)
    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process, p, model): p["id"] for p in todo}
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            r = fut.result()
            with lock:
                results[r["parent_id"]] = r
                json.dump(list(results.values()), open(OUT, "w"), ensure_ascii=False, indent=1)
            if i % 10 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}")

    sub = [results[p["id"]] for p in sample if p["id"] in results]
    g = Counter(r.get("gate") for r in sub)
    print(f"\n=== gate summary over {len(sub)} ===")
    for k in ("PASS", "PASS_DISTRACTOR", "SEP_TOO_SMALL", "CORRECT_SOLVER_FAILED",
              "SHORTCUT_SOLVER_FAILED", "no_trap"):
        if g.get(k):
            print(f"  {k:<24} {g[k]}")
    passed = [r for r in sub if r.get("gate") in ("PASS", "PASS_DISTRACTOR")]
    print(f"\n=== {len(passed)} candidates cleared the objective gate (review these) ===")
    for r in sorted(passed, key=lambda x: -(x.get("separation") or 0)):
        sep = f"{r['separation']*100:.0f}%" if r.get("separation") else "distractor"
        print(f"  {r['parent_id']:<10} {r.get('trap_type',''):<18} sep={sep:<10} {str(r.get('trigger',''))[:70]}")
    print(f"\nwritten: {OUT}")


if __name__ == "__main__":
    main()
