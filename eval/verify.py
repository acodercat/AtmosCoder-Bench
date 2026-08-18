"""Re-verify a benchmark set: re-execute every committed solve() and check it
still reproduces its stored answer (no LLM calls). The dataset correctness check.

Usage:
    uv run python -m eval.verify --set core -t 0.05
    uv run python -m eval.verify --input pipeline/reports/problems_final.json
"""

import json
import argparse
from pathlib import Path

from eval.engine import run_solver, verify_solver
from eval.datasets import SETS, dataset_path


def main():
    parser = argparse.ArgumentParser(description="Re-verify committed solvers")
    parser.add_argument("--set", dest="dataset", default="core", choices=list(SETS),
                        help="Which benchmark set to verify (default: core)")
    parser.add_argument("--input", default=None,
                        help="Verify an explicit json file instead of a --set")
    parser.add_argument("--tolerance", "-t", type=float, default=0.05, help="Numeric tolerance (default 0.05 = 5%%)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show each problem result")
    args = parser.parse_args()

    source = Path(args.input) if args.input else dataset_path(args.dataset)
    problems = json.loads(source.read_text())

    passed, failed, errors = 0, 0, 0
    failures = []

    for problem in problems:
        problem_id = problem["id"]
        ran, results, error_info = run_solver(problem["code"])

        if not ran:
            errors += 1
            failures.append((problem_id, f"exec error: {error_info[:100]}"))
            if args.verbose:
                print(f"  {problem_id}: ERROR")
            continue

        reproduced, details = verify_solver(results, problem["sub_answers"], tolerance=args.tolerance)
        if reproduced:
            passed += 1
            if args.verbose:
                print(f"  {problem_id}: PASS")
        else:
            failed += 1
            failures.append((problem_id, details))
            if args.verbose:
                print(f"  {problem_id}: FAIL")

    print(f"\n=== Results (tolerance={args.tolerance:.1%}) ===")
    print(f"Total:  {len(problems)}")
    print(f"Passed: {passed} ({passed/len(problems):.1%})")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")

    if failures:
        print("\n=== Failures ===")
        for problem_id, reason in failures:
            print(f"  {problem_id}: {reason}")


if __name__ == "__main__":
    main()
