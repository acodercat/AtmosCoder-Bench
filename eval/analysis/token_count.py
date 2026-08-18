"""Uniform token accounting for experiment result dirs.

Counts tokens from the STORED text fields (not model-reported usage), with a single
tokenizer (o200k_base) so counts are comparable across providers. Strict per-field,
summed over ALL attempts (the self-repair loop):

    prompt_tokens     = TOK(system) + TOK(attempt.prompt)     # system is sent every call
    completion_tokens = TOK(attempt.response)
    reasoning_tokens  = TOK(attempt.reasoning) if that field is a non-empty str else 0
    total_tokens      = prompt + completion + reasoning

Notes / disclosures baked into the metric:
  * These are o200k-normalized counts, NOT each provider's billed tokens.
  * `reasoning_tokens` counts the reasoning TEXT that was stored. Completeness varies by
    provider config: models that echo full chain-of-thought store all of it; models with a
    concise-summary setting (e.g. gpt55-reasoning) store only a summary; server-side-only
    reasoning that was never echoed is absent -> counted as 0. `rea_cov` (fraction of
    attempts carrying a non-empty reasoning field) surfaces this per model.

Usage:
    uv run python -m eval.analysis.token_count experiments/core_code experiments/core_direct ...
    uv run python -m eval.analysis.token_count experiments/core_code --json report.json

Read-only. Recurses each dir; files are grouped by sub-path (so e.g.
scaffolding_ablation/original_code vs stripped_code stay separate). Filenames may be
`<model>.run<N>.json` or `<model>.json` (single, no run suffix).
"""
import argparse
import glob
import json
import os

import tiktoken

_ENC = tiktoken.get_encoding("o200k_base")


def ntok(s):
    return len(_ENC.encode_ordinary(s)) if isinstance(s, str) and s else 0


def scan_file(path, root):
    rel = os.path.relpath(path, root)
    base = os.path.basename(path)[:-5]
    if ".run" in base:
        model, run = base.rsplit(".run", 1)
    else:
        model, run = base, "1"
    data = json.load(open(path))
    system = data.get("metrics", {}).get("system", "") or ""
    sys_tok = ntok(system)
    P = C = R = 0
    n_att = rea_present = 0
    for rec in data.get("results", []):
        for a in rec.get("attempts", []) or []:
            n_att += 1
            P += sys_tok + ntok(a.get("prompt"))
            C += ntok(a.get("response"))
            rea = a.get("reasoning")
            if isinstance(rea, str) and rea.strip():
                rea_present += 1
                R += ntok(rea)
    return {
        "group": os.path.dirname(rel), "model": model, "run": run,
        "n_records": len(data.get("results", [])), "n_attempts": n_att,
        "prompt": P, "completion": C, "reasoning": R, "total": P + C + R,
        "rea_cov": (rea_present / n_att) if n_att else 0.0,
    }


def scan_dir(root):
    rows = []
    for f in sorted(glob.glob(os.path.join(root, "**", "*.json"), recursive=True)):
        try:
            rows.append(scan_file(f, root))
        except Exception as e:  # noqa: BLE001 - report and continue
            print("  SKIP %s: %s" % (os.path.relpath(f, root), e))
    return rows


def aggregate(rows):
    agg = {}
    for r in rows:
        d = agg.setdefault((r["group"], r["model"]), {
            "runs": 0, "n_attempts": 0, "prompt": 0, "completion": 0,
            "reasoning": 0, "total": 0, "rea_cov_sum": 0.0})
        d["runs"] += 1
        for k in ("n_attempts", "prompt", "completion", "reasoning", "total"):
            d[k] += r[k]
        d["rea_cov_sum"] += r["rea_cov"]
    return agg


def print_table(name, agg):
    print("\n" + "=" * 108)
    print("### %s   (o200k_base, all attempts, sum over runs)" % name)
    print("=" * 108)
    print("%-20s %-26s %5s %9s %11s %11s %11s %12s %7s" % (
        "group", "model", "runs", "attempts", "prompt", "completion",
        "reasoning", "TOTAL", "rea_cov"))
    print("-" * 108)
    dir_total = 0
    for (grp, m) in sorted(agg):
        d = agg[(grp, m)]
        dir_total += d["total"]
        print("%-20s %-26s %5d %9d %11d %11d %11d %12d %6.0f%%" % (
            grp or "-", m, d["runs"], d["n_attempts"], d["prompt"], d["completion"],
            d["reasoning"], d["total"], 100 * d["rea_cov_sum"] / max(d["runs"], 1)))
    print("-" * 108)
    print("%-53s %54d" % ("DIR TOTAL", dir_total))
    return dir_total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", help="experiment result dirs (recursed)")
    ap.add_argument("--json", help="write full per-file + per-model report to this path")
    args = ap.parse_args()

    out = {"tokenizer": "o200k_base", "scope": "all_attempts", "dirs": {}}
    grand = 0
    for root in args.dirs:
        name = root.rstrip("/").split("experiments/")[-1]
        if not os.path.isdir(root):
            print("\n### %s  -> NOT FOUND" % name)
            continue
        rows = scan_dir(root)
        agg = aggregate(rows)
        grand += print_table(name, agg)
        out["dirs"][name] = {
            "per_file": rows,
            "per_model": {"%s|%s" % (g, m): agg[(g, m)] for (g, m) in agg},
        }
    if len(args.dirs) > 1:
        print("\n" + "=" * 108)
        print("GRAND TOTAL across %d dirs: %d o200k tokens" % (len(out["dirs"]), grand))
        print("=" * 108)
    out["grand_total"] = grand
    if args.json:
        json.dump(out, open(args.json, "w"), indent=2)
        print("\nsaved -> %s" % args.json)


if __name__ == "__main__":
    main()
