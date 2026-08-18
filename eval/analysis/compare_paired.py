"""Paired base-vs-variant comparison report for a single model.

Merges the main run with its error-fix run (error reruns only; original fails
are preserved), then reports:
  - overall base vs variant accuracy (errors excluded), with Wilson 95% CIs;
  - per-parent pairing: base correctness vs its variants' pass-rate, ranked to
    surface "base correct but variants collapse" (the contamination signal);
  - McNemar test on the base-result vs mean-variant-result pairing;
  - slices by k2 certification tier.

Usage:
    uv run python -m eval.analysis.compare_paired \
        --base-exp kimi_paired_base --base-errfix kimi_base_errfix \
        --var-exp kimi_paired_variants --var-errfix kimi_var_errfix \
        --model-file kimi-k2.6.json
"""

import json
import argparse
from collections import defaultdict

from eval.analysis.confidence import wilson_interval


def load_merged(run, errfix, model_file):
    """Results of `run`, with errored ids overridden by their non-error rerun."""
    merged = {record["id"]: record
              for record in json.load(open(f"experiments/{run}/{model_file}"))["results"]}
    try:
        fixes = {record["id"]: record
                 for record in json.load(open(f"experiments/{errfix}/{model_file}"))["results"]}
    except FileNotFoundError:
        fixes = {}
    for problem_id, fixed in fixes.items():
        if merged.get(problem_id, {}).get("error") and not fixed.get("error"):
            merged[problem_id] = fixed
    return merged


def accuracy_breakdown(records):
    """(passed, failed, errors, accuracy) — accuracy excludes errors."""
    passed = sum(1 for record in records if record.get("passed"))
    failed = sum(1 for record in records if record.get("passed") is False and not record.get("error"))
    errors = sum(1 for record in records if record.get("error"))
    return passed, failed, errors, (passed / (passed + failed) if (passed + failed) else 0.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-exp", dest="base_run", default="kimi_paired_base")
    parser.add_argument("--base-errfix", default="kimi_base_errfix")
    parser.add_argument("--var-exp", dest="var_run", default="kimi_paired_variants")
    parser.add_argument("--var-errfix", default="kimi_var_errfix")
    parser.add_argument("--model-file", default="kimi-k2.6.json")
    parser.add_argument("--out", default="experiments/paired_comparison.json")
    args = parser.parse_args()

    base_results = load_merged(args.base_run, args.base_errfix, args.model_file)
    variant_results = load_merged(args.var_run, args.var_errfix, args.model_file)
    problems = {problem["id"]: problem for problem in json.load(open("benchmark/core.json"))}
    variants = json.load(open("benchmark/variants_numeric.json"))
    k2_by_id = {variant["id"]: variant.get("k2", "?") for variant in variants}
    category_by_id = {pid: problem.get("category", "?") for pid, problem in problems.items()}

    base_passed, base_failed, base_errors, base_accuracy = accuracy_breakdown(base_results.values())
    var_passed, var_failed, var_errors, var_accuracy = accuracy_breakdown(variant_results.values())
    base_ci_low, base_ci_high = wilson_interval(base_passed, base_passed + base_failed)
    var_ci_low, var_ci_high = wilson_interval(var_passed, var_passed + var_failed)

    print("=" * 64)
    print("OVERALL  (errors excluded from denominator)")
    print(f"  BASE     {base_passed}/{base_passed+base_failed} = {base_accuracy*100:.2f}%  "
          f"95%CI[{base_ci_low*100:.1f},{base_ci_high*100:.1f}]  (err {base_errors})")
    print(f"  VARIANTS {var_passed}/{var_passed+var_failed} = {var_accuracy*100:.2f}%  "
          f"95%CI[{var_ci_low*100:.1f},{var_ci_high*100:.1f}]  (err {var_errors})")
    print(f"  gap (base - variant) = {(base_accuracy-var_accuracy)*100:.2f} pp")

    # per-parent pairing: base correctness vs its variants' pass-rate
    variant_flags_by_parent = defaultdict(list)
    for variant in variants:
        result = variant_results.get(variant["id"])
        if result and not result.get("error"):
            variant_flags_by_parent[variant["parent_id"]].append(1 if result.get("passed") else 0)
    per_parent = []  # (parent_id, base_correct, variant_passrate, n_variants, category)
    for parent_id in problems:
        base_record = base_results.get(parent_id)
        if not base_record or base_record.get("error"):
            continue
        flags = variant_flags_by_parent.get(parent_id, [])
        if not flags:
            continue
        per_parent.append((parent_id, 1 if base_record.get("passed") else 0,
                           sum(flags) / len(flags), len(flags), category_by_id.get(parent_id, "?")))

    # contamination signal: base correct, variants low
    suspicious = sorted([row for row in per_parent if row[1] == 1], key=lambda row: row[2])
    print("\n" + "=" * 64)
    print("CONTAMINATION SIGNAL — base CORRECT but variants weak (lowest first)")
    print(f"{'parent':10s} {'base':4s} {'var_passrate':12s} {'n':3s} category")
    for parent_id, _base_correct, variant_passrate, n_variants, category in suspicious[:20]:
        flag = " <== " if variant_passrate <= 0.5 else ""
        print(f"{parent_id:10s}  ✓   {variant_passrate*100:6.1f}%       {n_variants:2d}  {category}{flag}")

    # McNemar: base correct & mean-variant wrong  vs  base wrong & mean-variant right
    base_only = sum(1 for _, base_correct, passrate, _, _ in per_parent
                    if base_correct == 1 and passrate < 0.5)
    variant_only = sum(1 for _, base_correct, passrate, _, _ in per_parent
                       if base_correct == 0 and passrate >= 0.5)
    n_discordant = base_only + variant_only
    mcnemar_chi2 = ((abs(base_only - variant_only) - 1) ** 2 / n_discordant) if n_discordant else 0.0
    print("\n" + "=" * 64)
    print("McNEMAR (base vs majority-variant, per parent)")
    print(f"  base✓/var✗ = {base_only} | base✗/var✓ = {variant_only} | "
          f"chi2(cc) = {mcnemar_chi2:.2f}  (>3.84 => p<0.05)")

    # slice by k2 tier
    print("\n" + "=" * 64)
    print("VARIANT ACCURACY BY k2 CERTIFICATION TIER")
    by_tier = defaultdict(lambda: [0, 0])  # tier -> [passed, failed]
    for variant in variants:
        result = variant_results.get(variant["id"])
        if not result or result.get("error"):
            continue
        by_tier[k2_by_id[variant["id"]]][0 if result.get("passed") else 1] += 1
    for tier_name, (passed, failed) in sorted(by_tier.items(), key=lambda item: -sum(item[1])):
        print(f"  {tier_name:20s} {passed}/{passed+failed} = {passed/(passed+failed)*100:.1f}%")

    json.dump({"base": {"passed": base_passed, "failed": base_failed,
                        "errors": base_errors, "accuracy": base_accuracy},
               "variant": {"passed": var_passed, "failed": var_failed,
                           "errors": var_errors, "accuracy": var_accuracy},
               "mcnemar": {"base_only": base_only, "var_only": variant_only, "chi2_cc": mcnemar_chi2},
               "per_parent": [{"id": row[0], "base": row[1], "var_passrate": row[2], "n": row[3]}
                              for row in per_parent]},
              open(args.out, "w"), indent=1)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
