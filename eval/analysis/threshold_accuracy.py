"""Robustness spectrum (Table 2b of VARIANT_RESULTS.md): parent-level threshold
accuracy over the two variant families.

The denominator stays at the number of core parents (346 numeric / 436
paraphrase); a parent counts as solved at threshold K iff the model solves at
least K of its five variants, K in {3,4,5}. A variant is solved iff >=2 of the
model's 3 runs pass it (majority-of-3, the outcome rule used throughout the
variant analysis). Also prints the Spearman rank agreement between the core
ordering and each threshold ordering.

NOTE (aggregation caveat, stated in the doc): the strict columns aggregate up
to 15 measurements per parent versus 3 for a core solve, so core-minus-5/5 is
NOT a fragility measure and is intentionally not printed. The aggregation-fair
robustness/contamination statistics are the paired tests in
eval.analysis.robustness (Table 1).

    uv run python -m eval.analysis.threshold_accuracy
"""

import json
import collections

MODELS = [
    'gpt55-reasoning', 'gemini-3.1-pro', 'deepseek-v4-pro-reasoning',
    'kimi-k2.6-reasoning', 'qwen3.5-397b-reasoning', 'deepseek-v4-flash-reasoning',
    'gpt55', 'qwen3.5-397b', 'kimi-k2.6', 'qwen3.6-27b-reasoning',
    'deepseek-v4-pro', 'qwen3.6-27b', 'deepseek-v4-flash',
    'qwen3.5-9b-reasoning', 'qwen3.5-9b', 'qwen-2.5-72b',
]

FAMILIES = [
    ('numeric', 'benchmark/variants_numeric.json', 'experiments/variants_numeric_code'),
    ('paraphrase', 'benchmark/variants_paraphrase.json', 'experiments/variants_paraphrase_code'),
]


def majority(exp_dir, model):
    runs = [{x['id']: x for x in json.load(open(f'{exp_dir}/{model}.run{r}.json'))['results']}
            for r in (1, 2, 3)]
    return {i: sum(1 for r in runs if r[i].get('passed')) >= 2 for i in runs[0]}


def spearman(a, b, keys):
    n = len(keys)
    ra = {m: i for i, m in enumerate(sorted(keys, key=lambda x: -a[x]))}
    rb = {m: i for i, m in enumerate(sorted(keys, key=lambda x: -b[x]))}
    d2 = sum((ra[m] - rb[m]) ** 2 for m in keys)
    return 1 - 6 * d2 / (n * (n * n - 1))


def main():
    for fam, bench_path, exp_dir in FAMILIES:
        parents = collections.defaultdict(list)
        for v in json.load(open(bench_path)):
            parents[v['parent_id']].append(v['id'])
        assert all(len(vs) == 5 for vs in parents.values())

        rows = {}
        print(f"\n### {fam} ({len(parents)} parents)   core | >=3/5 | >=4/5 | 5/5")
        for m in MODELS:
            core_ok = majority('experiments/core_code', m)
            mv = majority(exp_dir, m)
            plist = list(parents)
            core_acc = sum(1 for p in plist if core_ok[p]) / len(plist) * 100
            counts = {p: sum(1 for v in parents[p] if mv[v]) for p in plist}
            ks = {k: sum(1 for p in plist if counts[p] >= k) / len(plist) * 100 for k in (3, 4, 5)}
            rows[m] = {'core': core_acc, **{f'k{k}': ks[k] for k in (3, 4, 5)}}
            print(f"  {m:28s} {core_acc:5.1f}  {ks[3]:5.1f}  {ks[4]:5.1f}  {ks[5]:5.1f}")

        c = {m: rows[m]['core'] for m in MODELS}
        for k in ('k3', 'k4', 'k5'):
            v = {m: rows[m][k] for m in MODELS}
            print(f"  Spearman(core, {k}) = {spearman(c, v, MODELS):.3f}")


if __name__ == '__main__':
    main()
