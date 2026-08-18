"""De-coarsen solver outputs for VARIANT ground truth.

Many solvers end with presentation rounding (`round(drop)`, `round(x, 1)`,
`int(n)`) so their base output matches the textbook's rounded answer. At the
BASE point that is correct (stored answer = textbook). At a PERTURBED point the
rounding error (up to 10%+ for small values) exceeds the 5% grading tolerance:
a model solving the variant correctly would be graded WRONG. (Found by the
k>=2 gate on 1.1: true 5.34 vs coarsened GT 5.0.)

Policy: base problems keep their textbook-aligned stored answers; VARIANTS get
full-precision GT. This script builds a de-rounded twin of every affected
solver, validated dynamically:

  - all `round(x)` / `round(x, 0)` / `round(x, 1)` calls are unwrapped;
  - each `int(...)` call is unwrapped one at a time, kept only if the solver
    still executes (int may be semantic, e.g. range(int(n)));
  - the de-rounded solver must run and its base output stay within 15% of the
    stored answers (sanity: de-rounding must not change the physics).

Output: pipeline/reports/derounded_solvers.json  {id: derounded_code}

Usage:
    uv run python -m pipeline.deround
"""

import json
import re
import argparse

from eval.engine import run_solver, verify_solver


def _call_spans(code: str, fname: str):
    """Spans (start, end_exclusive, inner) of fname(...) calls, paren-matched."""
    spans = []
    for m in re.finditer(r"\b" + fname + r"\(", code):
        j = m.end()
        depth, k = 1, j
        while depth and k < len(code):
            ch = code[k]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            k += 1
        if depth == 0:
            spans.append((m.start(), k, code[j:k - 1]))
    return spans


def _top_level_split(s: str):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def deround_round(code: str) -> str:
    """Unwrap round(x) and round(x, 0|1); keep round(x, 2+)."""
    while True:
        for st, en, inner in _call_spans(code, "round"):
            args = _top_level_split(inner)
            if len(args) == 1 or (len(args) == 2 and args[1].strip() in ("0", "1")):
                code = code[:st] + "(" + args[0].strip() + ")" + code[en:]
                break  # restart scan, offsets changed
        else:
            return code


def deround_int(code: str) -> str:
    """Unwrap int(...) occurrences one at a time, keeping only changes that still run."""
    changed = True
    while changed:
        changed = False
        for st, en, inner in _call_spans(code, "int"):
            trial = code[:st] + "(" + inner + ")" + code[en:]
            ok, _, _ = run_solver(trial)
            if ok:
                code = trial
                changed = True
                break
    return code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="pipeline/reports/problems_final.json")
    ap.add_argument("--out", default="pipeline/reports/derounded_solvers.json")
    args = ap.parse_args()

    problems = json.load(open(args.input))
    out, skipped = {}, []
    for p in problems:
        code = p["code"]
        if not (re.search(r"\bround\(", code) or re.search(r"\bint\(", code)):
            continue
        new = deround_int(deround_round(code))
        if new == code:
            continue
        ok, res, _ = run_solver(new)
        if not ok:
            skipped.append((p["id"], "exec"))
            continue
        sane, _ = verify_solver(res, p["sub_answers"], tolerance=0.15)
        if not sane:
            skipped.append((p["id"], "deviates>15%"))
            continue
        out[p["id"]] = new
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"derounded solvers: {len(out)} | skipped: {skipped}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
