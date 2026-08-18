"""De-scaffold base problems: remove a GIVEN standard formula so the model must recall it.

Targets the STANDARD_FORMULA problems found by ``pipeline.scan_formulas`` (a canonical
textbook relation handed in the statement). For each, opus48 rewrites the text WITHOUT the
formula — keeping the scenario, every input + unit, the disambiguating assumptions, and the
exact quantity asked. The rewrite is accepted only if opus48, shown ONLY the new text, blindly
reproduces the stored ground truth: that proves the correct formula is recoverable from the
scenario, so the problem stays solvable (just harder). Otherwise the original is kept.

opus48 throughout (rewrite + recovery check). solve()/sub_answers are never changed, so the
dataset stays self-consistent; only the problem prose changes. Dry-run by default.

    uv run python -m pipeline.descaffold --ids air_71 air_99 ...      # preview a few
    uv run python -m pipeline.descaffold --limit 10                   # preview first 10
    uv run python -m pipeline.descaffold --apply                      # rewrite all, edit base.json
"""

import json
import argparse
import threading
import concurrent.futures
from collections import Counter

from eval.engine import run_solver, extract_code, verify_solver
from eval.models import load_config, build_model, ModelError

MODEL = "opus48"

REWRITE_PROMPT = """You are editing an atmospheric-science problem to make it harder WITHOUT changing
its answer. The statement currently hands the solver a formula. Rewrite it so the solver must
recall the method itself.

## Keep (do NOT change)
- The physical scenario and every numerical value WITH its units (verbatim numbers).
- The assumptions / regime that make the correct method unambiguous (e.g. "dry adiabatic",
  "geostrophic balance", "hydrostatic", "ideal gas"). If such an assumption was only implied by
  the formula, state it in words so the intended method stays unique.
- The exact quantity(ies) asked and the units the answer must be in.

## Remove
- The given solving equation(s) and any "Use the equation ..." scaffolding.

Do NOT add the formula back in any form. Do NOT add worked steps or hints. Keep it concise and
natural. Output ONLY the rewritten problem statement.

## Current problem
{problem}"""

SOLVE_PROMPT = """You are an expert atmospheric scientist. Write a Python solve() that computes the
numerical answer(s) to the problem below from first principles.

- Compute from the physics; recall any standard formula yourself.
- Every given value is a parameter with its default; standard library only; convert units explicitly.
- Return a dict keyed "1".."N" in the order asked, each {{"value": <number>, "unit": "<unit>"}}.

## Problem
{problem}

Output ONLY the Python code for solve()."""


def rewrite(model, problem_text):
    try:
        return model.generate(REWRITE_PROMPT.format(problem=problem_text)).text.strip()
    except ModelError:
        return None


def blind_solve(model, problem_text, retries=3):
    """opus48 blindly writes+runs solve() from the text; return ordered floats or None."""
    feedback = ""
    for _ in range(retries):
        prompt = SOLVE_PROMPT.format(problem=problem_text)
        if feedback:
            prompt += f"\n\n## Your previous attempt failed: {feedback}\nFix it; output ONLY solve()."
        try:
            code = extract_code(model.generate(prompt).text)
        except ModelError as exc:
            feedback = str(exc)[:100]
            continue
        ran, results, info = run_solver(code)
        if not ran:
            feedback = info[:140]
            continue
        try:
            return [float(results[k]["value"] if isinstance(results[k], dict) else results[k])
                    for k in results]
        except (ValueError, TypeError):
            feedback = "non-numeric value"
    return None


def recovers(values, problem, tol):
    """Grade opus48's blind answer with the SAME grader the benchmark uses, so
    multi-acceptable-value subs (±sign / unit twins under one key) are handled."""
    if not values:
        return False
    results = {str(i + 1): {"value": v, "unit": ""} for i, v in enumerate(values)}
    passed, _ = verify_solver(results, problem["sub_answers"], tol)
    return passed


def descaffold_one(problem, model, tol):
    new_text = rewrite(model, problem["problem"])
    if not new_text:
        return {"id": problem["id"], "status": "REWRITE_FAILED"}
    recovered = blind_solve(model, new_text)
    ok = recovers(recovered, problem, tol)
    return {
        "id": problem["id"], "status": "ACCEPTED" if ok else "REVERTED_UNSOLVABLE",
        "new_problem": new_text, "recovered": recovered,
        "gt": [s["value"] for s in problem["sub_answers"]],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default="benchmark/base.json")
    parser.add_argument("--scan", default="pipeline/reports/formula_scan.json")
    parser.add_argument("--out", default="pipeline/reports/descaffold.json")
    parser.add_argument("--ids", nargs="+", default=None, help="only these ids (default: all strippable)")
    parser.add_argument("--limit", type=int, default=None, help="cap to first N strippable")
    parser.add_argument("--tol", type=float, default=0.05)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--apply", action="store_true", help="write accepted rewrites into base.json")
    args = parser.parse_args()

    base = json.load(open(args.base))
    by_id = {p["id"]: p for p in base}
    scan = json.load(open(args.scan))
    # strippable = STANDARD formula with enough scenario to stay unambiguous after deletion
    strippable = [r["id"] for r in scan
                  if r["verdict"] == "STANDARD_FORMULA" and r["scenario_sufficient"]]
    ids = args.ids or strippable
    ids = [i for i in ids if i in by_id]
    if args.limit:
        ids = ids[:args.limit]
    print(f"de-scaffolding {len(ids)} problems | model: {MODEL} | apply={args.apply}")

    model = build_model(load_config(MODEL))
    report, lock = [], threading.Lock()

    def work(pid):
        row = descaffold_one(by_id[pid], model, args.tol)
        with lock:
            report.append(row)
            print(f"  {row['id']:12s} {row['status']}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        list(executor.map(work, ids))

    report.sort(key=lambda r: (r["status"], r["id"]))
    json.dump(report, open(args.out, "w"), indent=2, ensure_ascii=False)
    print("\nstatus:", dict(Counter(r["status"] for r in report)))

    accepted = [r for r in report if r["status"] == "ACCEPTED"]
    if args.apply and accepted:
        for r in accepted:
            by_id[r["id"]]["problem"] = r["new_problem"]
        json.dump(base, open(args.base, "w"), indent=2, ensure_ascii=False)
        print(f"APPLIED {len(accepted)} rewrites -> {args.base}")
    else:
        print(f"dry-run: {len(accepted)} would be accepted (re-run with --apply to write)")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
