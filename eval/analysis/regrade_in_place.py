"""Re-derive stored verdicts from `details` after a grading input changed (no LLM calls).

A result record's `passed` is the verdict the runner reached with the benchmark as it
was AT RUN TIME. When the benchmark is later corrected in a way that changes grading
without changing any answer — the consensus-built sets had no units, so the unit-aware
rule could never credit a right answer given in kPa against a key in Pa — the stored
verdict is stale while the stored `details` (expected, actual, and the units backfilled
by eval.analysis.backfill_detail_units) hold everything needed to grade again.

This re-applies verify_solver's rule to every detail (a sub passes if any accepted value
matches outright or after unit reconciliation; a problem passes iff all subs pass), sets
`details[].passed` and the record's `passed`, and recomputes the file's metrics exactly
as the runner does (accuracy = passed / (passed + failed), errors excluded). Error
records are left untouched. The file then equals what a run against the corrected
benchmark would have produced. Rewrites in place; back the directory up first
(`experiments/` is not under git).

    uv run python -m eval.analysis.regrade_in_place --exp cross_domain --dry-run
    uv run python -m eval.analysis.regrade_in_place --exp cross_domain
"""

import json
import glob
import argparse
from pathlib import Path

from eval.analysis.backfill_detail_units import sub_passes


def regrade_file(path, tolerance, apply):
    data = json.load(open(path))
    results = data.get("results")
    if not isinstance(results, list):
        return None
    before = sum(1 for r in results if r.get("passed"))
    flips = []
    for record in results:
        details = record.get("details")
        if not details or any("sub" not in d for d in details) or "error" in record:
            continue  # ungradable / error record: leave the runner's verdict alone
        sub_verdicts = []
        for detail in details:
            verdict = sub_passes(detail, tolerance)
            if verdict != bool(detail.get("passed")):
                detail["passed"] = verdict
            sub_verdicts.append(verdict)
        verdict = all(sub_verdicts)
        if verdict != bool(record.get("passed")):
            flips.append((record["id"], bool(record.get("passed")), verdict))
            record["passed"] = verdict
    after = sum(1 for r in results if r.get("passed"))
    errors = sum(1 for r in results if "error" in r or r.get("passed") is None)
    failed = len(results) - after - errors
    denom = after + failed
    metrics = data.setdefault("metrics", {})
    old_acc = metrics.get("accuracy")
    metrics.update({"total": len(results), "passed": after, "failed": failed, "errors": errors,
                    "accuracy": after / denom if denom else 0.0})
    if apply and (flips or old_acc != metrics["accuracy"]):
        json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    return before, after, len(results), flips


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exp", nargs="+", required=True, help="experiment dir(s) under experiments/")
    ap.add_argument("--tolerance", type=float, default=0.05)
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    args = ap.parse_args()
    total_flips = 0
    for exp in args.exp:
        for path in sorted(glob.glob(f"experiments/{exp}/**/*.json", recursive=True)):
            out = regrade_file(Path(path), args.tolerance, apply=not args.dry_run)
            if out is None:
                continue
            before, after, n, flips = out
            total_flips += len(flips)
            tag = "" if not flips else "  " + ", ".join(f"{i}:{'P' if v else 'F'}" for i, _, v in flips)
            print(f"{path}: {before}/{n} -> {after}/{n}{tag}")
    print(f"{'would flip' if args.dry_run else 'flipped'} {total_flips} record verdict(s)")


if __name__ == "__main__":
    main()
