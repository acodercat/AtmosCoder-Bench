"""Compare two run modes (code vs direct) on the same problems.

Reads a code-mode experiment dir and a direct-mode experiment dir, pairs them by
model file, and reports — per model — accuracy under each protocol plus the
per-problem four-way cross-tab that makes the methodological point:

  code_only_right  : the model knew the method (solver works) but its hand
                     arithmetic/algebra was wrong under direct reasoning  -> the
                     "arithmetic tax" that direct-answer grading charges.
  direct_only_right: prose reached the answer but the model couldn't formalize
                     it as a runnable solver (or got there by a shortcut).
  both / neither   : agreement.

Across >=2 models it also prints the score *spread* under each protocol — a test
that separates strong from weak models more has higher discriminative power.

Accuracy uses each mode's own graded denominator (passed+failed, errors excluded,
matching the runner). The cross-tab is restricted to problems graded (non-error)
under BOTH modes, so it is apples-to-apples.

Usage:
    uv run python -m eval.analysis.compare_modes --code-exp kimi_code --direct-exp kimi_direct
"""

import json
import argparse
from pathlib import Path
from collections import Counter


def _load(exp_dir: Path) -> dict[str, dict]:
    """model_id -> {id: 'pass'|'fail'|'error'} for every result file in the dir."""
    by_model = {}
    for result_file in sorted(exp_dir.glob("*.json")):
        if result_file.name == "summary.json":
            continue
        records = json.loads(result_file.read_text()).get("results", [])
        verdicts = {}
        for record in records:
            verdicts[record["id"]] = ("error" if record.get("error")
                                      else "pass" if record.get("passed") else "fail")
        by_model[result_file.stem] = verdicts
    return by_model


def _accuracy(verdicts: dict) -> tuple[int, int, float]:
    graded = [verdict for verdict in verdicts.values() if verdict != "error"]
    passed = sum(1 for verdict in graded if verdict == "pass")
    return passed, len(graded), (passed / len(graded) if graded else 0.0)


def compare(code_verdicts: dict, direct_verdicts: dict) -> dict:
    ids = set(code_verdicts) | set(direct_verdicts)
    _, graded_code, accuracy_code = _accuracy(code_verdicts)
    _, graded_direct, accuracy_direct = _accuracy(direct_verdicts)
    both_ids = [pid for pid in ids if code_verdicts.get(pid) in ("pass", "fail")
                and direct_verdicts.get(pid) in ("pass", "fail")]
    bucket = Counter()
    for pid in both_ids:
        bucket[(code_verdicts[pid] == "pass", direct_verdicts[pid] == "pass")] += 1
    n_both = len(both_ids) or 1
    return {
        "acc_C": round(accuracy_code, 4), "acc_D": round(accuracy_direct, 4),
        "graded_C": graded_code, "graded_D": graded_direct, "graded_both": len(both_ids),
        "both_right": bucket[(True, True)], "both_wrong": bucket[(False, False)],
        "code_only_right": bucket[(True, False)], "direct_only_right": bucket[(False, True)],
        "arithmetic_tax": round(bucket[(True, False)] / n_both, 4),
        "code_blindspot": round(bucket[(False, True)] / n_both, 4),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code-exp", required=True, help="experiment dir of the code-mode run")
    parser.add_argument("--direct-exp", required=True, help="experiment dir of the direct-mode run")
    parser.add_argument("--out", default=None, help="optional path to write the comparison JSON")
    args = parser.parse_args()

    code = _load(Path(f"experiments/{args.code_exp}"))
    direct = _load(Path(f"experiments/{args.direct_exp}"))
    models = [model for model in code if model in direct]
    if not models:
        print(f"No shared model files between {args.code_exp} and {args.direct_exp}.")
        print(f"  code: {list(code)}\n  direct: {list(direct)}")
        return

    comparisons = {model: compare(code[model], direct[model]) for model in models}

    print(f"{'model':18s} {'Acc_C':>7s} {'Acc_D':>7s} {'C-D':>7s} "
          f"{'C-only':>7s} {'D-only':>7s} {'算术税':>7s} {'盲区':>6s}  (n_both)")
    for model in models:
        row = comparisons[model]
        print(f"{model:18s} {row['acc_C']:7.1%} {row['acc_D']:7.1%} {row['acc_C']-row['acc_D']:+7.1%} "
              f"{row['code_only_right']:7d} {row['direct_only_right']:7d} "
              f"{row['arithmetic_tax']:7.1%} {row['code_blindspot']:6.1%}  ({row['graded_both']})")

    if len(models) > 1:
        code_accuracies = [comparisons[model]["acc_C"] for model in models]
        direct_accuracies = [comparisons[model]["acc_D"] for model in models]
        print(f"\n区分度(模型分数极差): code={max(code_accuracies)-min(code_accuracies):.1%}  "
              f"direct={max(direct_accuracies)-min(direct_accuracies):.1%}")

    if args.out:
        Path(args.out).write_text(json.dumps(comparisons, indent=2, ensure_ascii=False))
        print(f"\nsaved: {args.out}")


if __name__ == "__main__":
    main()
