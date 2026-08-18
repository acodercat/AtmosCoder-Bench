"""Audit imported problems for quality/difficulty with a judge model (default opus48).

Reads a problems json (e.g. benchmark/external/atmossci_mcq.json), dedups to one
representative per template (parent_id) so the model audits each distinct problem
once, then asks the judge — via models.toml, i.e. the user's own API — to rate
difficulty and flag concrete defects. Output: a per-problem verdict + summary.

Usage:
    uv run python -m pipeline.audit_mcq --input benchmark/external/atmossci_mcq.json \
        --model opus48 --out pipeline/reports/mcq_audit.json
"""

import os
import re
import json
import argparse
import threading
import concurrent.futures
from collections import Counter, defaultdict

from eval.models import load_config, build_model, ModelError

PROMPT = """You are auditing an atmospheric-science computational benchmark problem (originally
multiple-choice, options removed; the answer is a reference value). Be rigorous and
skeptical — the goal is to find real defects, not to rubber-stamp. Reason through the
physics; sanity-check the reference answer's magnitude/sign/units.

## Problem
{problem}

## Reference answer(s)
{answer}

## Assess and reply with ONLY a JSON object:
{{"difficulty": "trivial|easy|medium|hard",
  "self_contained": true|false,   // solvable from the text alone (all data/standard constants present)
  "well_posed": true|false,       // unambiguous, single correct interpretation
  "answer_plausible": true|false, // reference answer physically reasonable (flag clearly-wrong magnitude/sign/units)
  "issues": ["short concrete defect", ...]}}   // empty list if none"""


def _extract_verdict(text):
    """Return the last brace-balanced JSON object mentioning "difficulty". A
    balanced scan (not a flat regex) tolerates braces inside strings — e.g. LaTeX
    like \\frac{a}{b} in an issue note — both in the reasoning and in the verdict."""
    candidates = []
    for start in (i for i, ch in enumerate(text) if ch == "{"):
        depth = 0
        for end in range(start, len(text)):
            depth += (text[end] == "{") - (text[end] == "}")
            if depth == 0:
                candidates.append(text[start:end + 1])
                break
    for candidate in reversed(candidates):
        if "difficulty" in candidate:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
    return None


def audit(model, problem):
    text = PROMPT.format(problem=problem["problem"],
                         answer="; ".join(f"{s['value']} {s['unit']}".strip() for s in problem["sub_answers"]))
    try:
        raw = model.generate(text, "You are a meticulous scientific reviewer. Reply with only JSON.").text
    except ModelError as exc:
        return {"id": problem["id"], "error": str(exc)[:120]}
    verdict = _extract_verdict(raw)
    if verdict is None:
        return {"id": problem["id"], "error": "no parsable json", "raw": raw[-300:]}
    verdict["id"] = problem["id"]
    verdict["category"] = problem.get("category", "")
    return verdict


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default="opus48")
    parser.add_argument("--out", default="pipeline/reports/mcq_audit.json")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--all", action="store_true", help="audit every instance, not one per template")
    parser.add_argument("--ids", nargs="+", default=None, help="audit only these ids, merging into --out")
    parser.add_argument("--max-tokens", type=int, default=16384, help="judge max output tokens")
    args = parser.parse_args()

    problems = json.load(open(args.input))
    if not args.all:  # one representative per template
        by_template = defaultdict(list)
        for problem in problems:
            by_template[problem.get("parent_id", problem["id"])].append(problem)
        problems = [sorted(group, key=lambda p: p.get("variant", 0))[0] for group in by_template.values()]
    if args.ids:
        problems = [p for p in problems if p["id"] in set(args.ids)]

    cfg = load_config(args.model)
    cfg["max_tokens"] = args.max_tokens
    model = build_model(cfg)
    print(f"auditing {len(problems)} problems with {args.model} ...")
    results, lock, done = [], threading.Lock(), [0]

    def work(problem):
        verdict = audit(model, problem)
        with lock:
            results.append(verdict)
            done[0] += 1
            if done[0] % 10 == 0:
                print(f"  {done[0]}/{len(problems)}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        list(executor.map(work, problems))

    if args.ids and os.path.exists(args.out):  # merge re-audited ids into the existing report
        merged = {r["id"]: r for r in json.load(open(args.out))}
        merged.update({r["id"]: r for r in results})
        results = list(merged.values())

    json.dump(results, open(args.out, "w"), indent=2, ensure_ascii=False)
    graded = [r for r in results if "difficulty" in r]
    flagged = [r for r in graded if r.get("issues") or not r.get("self_contained", True)
               or not r.get("well_posed", True) or not r.get("answer_plausible", True)]
    print("\n=== difficulty ===", dict(Counter(r["difficulty"] for r in graded)))
    print(f"=== flagged (any issue / not self-contained / ill-posed / implausible answer): {len(flagged)}/{len(graded)} ===")
    bad_answer = [r for r in graded if not r.get("answer_plausible", True)]
    print(f"=== implausible reference answer: {len(bad_answer)} ===")
    for r in bad_answer:
        print(f"  {r['id']}: {'; '.join(r.get('issues', []))[:130]}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
