"""Re-grade existing runs at one or more tolerances (offline, no model calls).

Each result's `details` already stores, per sub-answer, the expected value(s) and
the model's actual returned value. We re-apply the grading rule (verify_solver
semantics: a sub passes if relative error <= tol vs ANY accepted value; the whole
problem passes iff all subs pass) at each tolerance, and report accuracy with
Wilson 95% CIs. Errors are excluded from the denominator, matching the runner.

Grade a whole run with --exp-id (every result json under experiments/<id>/), or a
single result file with --file:

    uv run python -m eval.analysis.accuracy --exp-id gemini_20260613 --tols 0.05
    uv run python -m eval.analysis.accuracy --file experiments/myrun/kimi-k2.6.json --tols 0.01 0.05 0.10
"""

import json
import argparse
from pathlib import Path

from tabulate import tabulate

from eval.engine import compare_values, _units_reconcile
from eval.analysis.confidence import wilson_interval


def regrade_one(details, tolerance):
    """Whole-problem pass at the given tolerance, from stored expected/actual.

    Replays the runner's full unit-aware rule when the detail record carries
    units (``expected_units`` / ``actual_unit``, stored by verify_solver since
    2026-07-23 and backfilled into earlier runs): a sub passes on a bare numeric
    match OR once both sides are converted via their declared units. Records
    without units fall back to the bare compare, which under-grades answers
    given in a commensurate unit (km vs m) — backfill them first.
    """
    if not details:
        return False
    for detail in details:
        actual = detail.get("actual")
        actual_unit = detail.get("actual_unit", "")
        expected_values = detail.get("expected") or []
        expected_units = detail.get("expected_units") or [""] * len(expected_values)
        matched = False
        for expected_value, expected_unit in zip(expected_values, expected_units):
            try:
                if compare_values(str(expected_value), actual, tolerance) or \
                   _units_reconcile(expected_value, expected_unit, actual, actual_unit, tolerance):
                    matched = True
                    break
            except Exception:
                pass
        if not matched:
            return False
    return True


def regrade_record(record, tolerance):
    """Whole-record pass at the given tolerance — the full runner-faithful rule.

    On top of the per-sub unit-aware compare, this replays the one metric-level
    override present in the corpus: the 2026-07-16 `provable_order_alignment`
    regrade, whose corrected sub->value assignment is stored on the record
    (``regraded.assignment``). Reassigned subs are graded against the assigned
    value (bare compare — the rule only fired on provable value matches).
    """
    details = record.get("details")
    if not details:
        return False
    assignment = (record.get("regraded") or {}).get("assignment") or {}
    remapped = []
    for detail in details:
        sub = str(detail.get("sub", ""))
        if sub in assignment and assignment[sub] != detail.get("actual"):
            detail = dict(detail, actual=assignment[sub], actual_unit="")
        remapped.append(detail)
    return regrade_one(remapped, tolerance)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--exp-id", help="grade every result json under experiments/<id>/")
    source.add_argument("--file", help="grade a single result json")
    parser.add_argument("--tols", nargs="+", type=float, default=[0.01, 0.02, 0.05, 0.10, 0.20])
    args = parser.parse_args()

    if args.file:
        result_files = [Path(args.file)]
    else:
        exp_dir = Path("experiments") / args.exp_id
        result_files = (sorted(path for path in exp_dir.glob("*.json") if path.name != "summary.json")
                        if exp_dir.is_dir() else [])
        if not result_files:
            raise SystemExit(f"no result json under experiments/{args.exp_id}/")

    for result_file in result_files:
        records = json.loads(result_file.read_text())["results"]
        graded = [record for record in records if not record.get("error")]
        n_graded, n_errors = len(graded), len(records) - len(graded)
        label = result_file.relative_to("experiments") if "experiments" in result_file.parts else result_file
        rows = []
        for tolerance in args.tols:
            passed = sum(1 for record in graded if regrade_record(record, tolerance))
            ci_low, ci_high = wilson_interval(passed, n_graded)
            rows.append([f"± {tolerance*100:g}%", f"{passed/n_graded*100:.2f}%",
                         f"{passed} / {n_graded}", f"[{ci_low*100:.1f}, {ci_high*100:.1f}]"])
        print(f"\n{label}   (graded: {n_graded}, errors excluded: {n_errors})")
        print(tabulate(rows, headers=["Tolerance", "Accuracy", "Passed / Graded", "95% CI (Wilson)"],
                       tablefmt="simple_outline", colalign=("right", "right", "right", "center")))


if __name__ == "__main__":
    main()
