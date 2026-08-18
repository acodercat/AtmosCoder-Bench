"""Assign each base problem an INTRINSIC difficulty level (low / medium / high).

A single strong reasoning model (gpt55-reasoning) scores every problem against an
EXPLICIT, countable rubric — distinct knowledge points, number of solution steps,
mathematical machinery, recall burden, unit/setup complexity, multi-concept
synthesis — then maps the dimension scores to one level. The model is shown the
problem, its curated knowledge_points, its sub-answer count, and the reference
solver code (an objective signal of solution-path length / iteration / root-finding),
but NOT told to optimise for any target distribution, so the labels are grounded in
the rubric rather than balanced by fiat.

Output: pipeline/reports/difficulty.json  ({id: {level, scores, rationale}}).
Merge into base.json with pipeline/_merge stub or a one-off (adds `difficulty`).

    uv run python -m pipeline.classify_difficulty --limit 8        # pilot
    uv run python -m pipeline.classify_difficulty --workers 8      # full run
"""

import os
import re
import json
import argparse
import threading
import concurrent.futures
from collections import Counter

from eval.models import load_config, build_model

SYSTEM = ("You are a meticulous atmospheric-science exam assessor. You rate the INTRINSIC "
          "difficulty of computational problems strictly by the given rubric, not by gut feel. "
          "You reason about the solution a competent solver must produce, then score each "
          "dimension objectively. Reply with ONLY the requested JSON.")

PROMPT = """Rate the difficulty of this atmospheric-science computational problem for an LLM/competent
graduate solver who sees ONLY the problem text (no formulas or answer are given to them).

Score these SIX dimensions objectively, each an integer 1-3 (1 = low, 2 = moderate, 3 = high):

1. knowledge_breadth — number of DISTINCT physical concepts/principles needed.
   1 = one concept; 2 = two or three; 3 = four or more synthesised together.
2. solution_steps — number of distinct derivation/computation steps to the final answer.
   1 = 1-2 steps (direct plug-in); 2 = 3-6 steps (a short chain); 3 = >6 steps / many intermediates.
3. math_machinery — heaviest mathematical tool required.
   1 = arithmetic / one explicit formula; 2 = multi-step algebra, logs/exponentials, one nonlinear relation;
   3 = calculus/integration, iteration, transcendental or implicit root-finding, systems of equations.
4. recall_burden — how much non-given standard knowledge (constants, formulas, definitions) must be recalled.
   1 = almost none / all given; 2 = a few standard constants or one standard formula; 3 = several formulas/constants
   or a non-obvious relation the solver must know.
5. setup_complexity — difficulty of correctly setting up the problem: unit conversions, sign/geometry conventions,
   choosing the right regime/assumption. 1 = trivial; 2 = moderate care; 3 = many conversions or an easy-to-miss setup.
6. error_proneness — how easy it is for a careful solver to still get a wrong number.
   1 = hard to get wrong; 2 = a couple of traps; 3 = many traps / coupled quantities.

Then assign ONE overall level using the SUM of the six scores (range 6-18):
- "low"     : sum 6-9    (direct, single-concept, short)
- "medium"  : sum 10-13  (multi-step or multi-concept, standard machinery)
- "high"    : sum 14-18  (long/iterative derivation, broad synthesis, high recall or trap density)
Use judgement only at the boundaries; if a single dimension is a clear 3 on math_machinery
(iteration/calculus/root-finding) the problem is at least "medium".

## Problem
{problem}

## Curated knowledge points ({n_kp})
{kp}

## Number of sub-questions: {n_sub}

## Reference solution (for gauging solution-path length / iteration only — do not copy numbers)
```python
{code}
```

Reply with ONLY this JSON:
{{"scores":{{"knowledge_breadth":n,"solution_steps":n,"math_machinery":n,"recall_burden":n,"setup_complexity":n,"error_proneness":n}},"sum":n,"level":"low|medium|high","rationale":"<=25 words on the decisive factors"}}"""


def parse(t):
    m = re.search(r"\{.*\}", t, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def classify(model, p, retries=3):
    kp = p.get("knowledge_points") or []
    prompt = PROMPT.format(
        problem=p["problem"],
        n_kp=len(kp),
        kp="\n".join(f"- {k}" for k in kp) or "- (none listed)",
        n_sub=len(p.get("sub_answers") or []),
        code=p.get("code", ""))
    for _ in range(retries):
        try:
            out = parse(model.generate(prompt, SYSTEM).text)
        except Exception:
            continue
        if out and out.get("level") in ("low", "medium", "high") and isinstance(out.get("scores"), dict):
            return out
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="benchmark/base.json")
    ap.add_argument("--out", default="pipeline/reports/difficulty.json")
    ap.add_argument("--model", default="gpt55-reasoning")
    ap.add_argument("--ids", nargs="+", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    problems = json.load(open(args.input))
    if args.ids:
        problems = [p for p in problems if p["id"] in set(args.ids)]
    if args.limit:
        problems = problems[: args.limit]

    out = json.load(open(args.out)) if os.path.exists(args.out) else {}
    todo = [p for p in problems if p["id"] not in out]
    print(f"problems: {len(problems)} | done: {len(out)} | todo: {len(todo)}")

    model = build_model(load_config(args.model))
    lock = threading.Lock()
    n = [0]
    fail = []

    def work(p):
        r = classify(model, p)
        with lock:
            if r:
                out[p["id"]] = {"level": r["level"], "sum": r.get("sum"),
                                "scores": r["scores"], "rationale": r.get("rationale", "")}
            else:
                fail.append(p["id"])
            n[0] += 1
            if n[0] % 25 == 0:
                json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)
                print(f"  {n[0]}/{len(todo)} {dict(Counter(v['level'] for v in out.values()))}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))

    json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)
    print("\nlevels:", dict(Counter(v["level"] for v in out.values())))
    print("failed:", fail)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
