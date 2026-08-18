"""Robustness analysis: core set (core_code) vs numeric / paraphrase variants.

Answers, with paired statistics on matched parent subsets:
  1. Contamination / memorization resistance (core vs numeric variants)
     - per-model paired Δ accuracy, exact McNemar test, analytic + bootstrap CI
     - "parent-echo" smoking gun: failed variant answers that equal the PARENT's
       textbook answer (direct evidence of memorized answers)
  2. Linguistic robustness (core vs paraphrase variants)
     - paired Δ, per-parent 0..5 consistency spectrum vs run-to-run noise
  3. Leaderboard stability: Spearman/Kendall rank correlation of model accuracy
     across core / numeric / paraphrase
  4. Reasoning-twin comparison: does thinking reduce the contamination gap?
  5. Strata: Δ by difficulty and category
  6. Failure-mode shift (ungradable vs wrong-value) and self-repair cost

Rigor rules baked in:
  * Only COMPLETE configs are analyzed: all 3 runs present, id set exactly equals
    the benchmark id set, zero infra-error records. Everything else is excluded
    and listed in the report header.
  * Core-set accuracy is always recomputed on the MATCHED parent subset (numeric
    variants only cover numeric-variantable parents).
  * Problem-level outcome = majority of 3 runs (>=2/3). Parent-level variant
    outcome = majority of its 5 variants (>=3/5). Instance-level (per-run,
    per-variant) accuracies are reported alongside.
  * McNemar: exact two-sided binomial on discordant parent pairs.
  * CI on Δ: analytic paired SE always; optional seeded bootstrap (--boot).
  * Parent-echo: counted only on discriminative subs (parent and variant expected
    answers differ by > tol), so an unchanged sub can never produce a false echo.

Usage:
  uv run python -m eval.analysis.robustness                # full report
  uv run python -m eval.analysis.robustness --boot 2000 --json report.json
"""
import argparse
import glob
import json
import math
import os
import random
from collections import defaultdict

BASE_DIR = "experiments/core_code"
NUM_DIR = "experiments/variants_numeric_code"
PARA_DIR = "experiments/variants_paraphrase_code"
CORE_BM = "benchmark/core.json"
NUM_BM = "benchmark/variants_numeric.json"
PARA_BM = "benchmark/variants_paraphrase.json"

TWINS = [  # (backbone label, non-reasoning model, reasoning model)
    ("gpt-5.5", "gpt55", "gpt55-reasoning"),
    ("DeepSeek-V4-flash", "deepseek-v4-flash", "deepseek-v4-flash-reasoning"),
    ("DeepSeek-V4-pro", "deepseek-v4-pro", "deepseek-v4-pro-reasoning"),
    ("Kimi K2.6", "kimi-k2.6", "kimi-k2.6-reasoning"),
    ("Qwen-3.5-9B", "qwen3.5-9b", "qwen3.5-9b-reasoning"),
    ("Qwen-3.5-397B", "qwen3.5-397b", "qwen3.5-397b-reasoning"),
    ("Qwen-3.6-27B", "qwen3.6-27b", "qwen3.6-27b-reasoning"),
]


# ---------------------------------------------------------------- helpers
def fnum(x):
    """Parse a stored answer value to float; None if unparseable."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip().replace("×10^", "e").replace("x10^", "e").replace("×", "e").replace(",", "")
        try:
            return float(s)
        except ValueError:
            return None
    return None


def expected_values(sub_answers):
    """{sub_id: [acceptable float values]} from a benchmark sub_answers list."""
    out = {}
    for sa in sub_answers or []:
        v = sa.get("value")
        vals = v if isinstance(v, list) else [v]
        fl = [f for f in (fnum(u) for u in vals) if f is not None]
        if fl:
            out[str(sa.get("sub"))] = fl
    return out


def close(a, e, tol):
    return abs(a - e) <= tol * max(abs(e), 1e-12)


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p on discordant counts (b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n * 2
    return min(1.0, p)


def paired_se(b, c, n):
    """Analytic SE of the paired accuracy difference (b-c)/n."""
    if n == 0:
        return float("nan")
    d = b - c
    var = (b + c) / n ** 2 - d ** 2 / n ** 3
    return math.sqrt(max(var, 0.0))


def rankdata(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    ranks = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((a - my) ** 2 for a in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))


def kendall(x, y):
    n = len(x)
    conc = disc = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = x[i] - x[j], y[i] - y[j]
            if a == 0 and b == 0:
                tx += 1; ty += 1
            elif a == 0:
                tx += 1
            elif b == 0:
                ty += 1
            elif a * b > 0:
                conc += 1
            else:
                disc += 1
    n0 = n * (n - 1) / 2
    den = math.sqrt((n0 - tx) * (n0 - ty))
    return (conc - disc) / den if den else float("nan")


# ---------------------------------------------------------------- loading
def discover_complete(exp_dir, want_ids):
    """{model: [run files x3]} for configs whose 3 runs each carry exactly
    want_ids with zero error records."""
    bym = defaultdict(dict)
    for f in glob.glob(os.path.join(exp_dir, "*.run*.json")):
        base = os.path.basename(f)[:-5]
        m, r = base.rsplit(".run", 1)
        bym[m][r] = f
    ok, bad = {}, []
    for m, runs in sorted(bym.items()):
        if set(runs) != {"1", "2", "3"}:
            bad.append(m); continue
        good = True
        for r in ("1", "2", "3"):
            res = json.load(open(runs[r]))["results"]
            ids = {x["id"] for x in res}
            if ids != want_ids or any(x.get("error") or "passed" not in x for x in res):
                good = False; break
        if good:
            ok[m] = [runs[r] for r in ("1", "2", "3")]
        else:
            bad.append(m)
    return ok, bad


def load_runs(files, keep_details):
    """[{id: rec}] per run. rec = (passed, ungradable, num_attempts, fail_details)
    fail_details = {sub: actual_float} only for failed gradable records."""
    out = []
    for f in files:
        res = json.load(open(f))["results"]
        d = {}
        for x in res:
            p = bool(x.get("passed"))
            det = x.get("details") or []
            ung = (not p) and not det
            fd = None
            if keep_details and not p and det:
                fd = {}
                for s in det:
                    a = fnum(s.get("actual"))
                    if a is not None:
                        fd[str(s.get("sub"))] = a
            d[x["id"]] = (p, ung, x.get("num_attempts") or 1, fd)
        out.append(d)
    return out


def maj(runs, pid):
    return sum(1 for r in runs if r[pid][0]) >= 2


# ---------------------------------------------------------------- analyses
def paired_block(models, base_runs, var_runs, parents, kids_of, boot, seed):
    """Per-model paired contamination/robustness numbers on matched parents."""
    rows = {}
    rng = random.Random(seed)
    boot_idx = [[rng.randrange(len(parents)) for _ in parents] for _ in range(boot)] if boot else None
    for m in models:
        br, vr = base_runs[m], var_runs[m]
        bpass = {p: maj(br, p) for p in parents}
        vsolve = {}
        for p in parents:
            ks = kids_of[p]
            vsolve[p] = sum(1 for k in ks if maj(vr, k)) >= (len(ks) // 2 + 1)
        b = sum(1 for p in parents if bpass[p] and not vsolve[p])   # base-only
        c = sum(1 for p in parents if vsolve[p] and not bpass[p])   # variant-only
        n = len(parents)
        acc_b = sum(bpass.values()) / n
        acc_v = sum(vsolve.values()) / n
        delta = acc_b - acc_v
        se = paired_se(b, c, n)
        ci = (delta - 1.96 * se, delta + 1.96 * se)
        bci = None
        if boot:
            pb = [1 if bpass[p] else 0 for p in parents]
            pv = [1 if vsolve[p] else 0 for p in parents]
            ds = sorted((sum(pb[i] for i in idx) - sum(pv[i] for i in idx)) / n for idx in boot_idx)
            bci = (ds[int(0.025 * boot)], ds[min(boot - 1, int(0.975 * boot))])
        # instance-level accuracies (mean over runs)
        inst_b = [sum(1 for p in parents if r[p][0]) / n for r in br]
        all_kids = [k for p in parents for k in kids_of[p]]
        inst_v = [sum(1 for k in all_kids if r[k][0]) / len(all_kids) for r in vr]
        rows[m] = dict(
            n_parents=n, acc_base_maj=acc_b, acc_var_parent=acc_v, delta=delta,
            discordant_base_only=b, discordant_var_only=c,
            mcnemar_p=mcnemar_exact(b, c), se=se, ci95=ci, boot_ci95=bci,
            inst_base_mean=sum(inst_b) / 3, inst_base_sd=(sum((x - sum(inst_b) / 3) ** 2 for x in inst_b) / 2) ** 0.5 if len(inst_b) == 3 else 0,
            inst_var_mean=sum(inst_v) / 3, inst_var_sd=(sum((x - sum(inst_v) / 3) ** 2 for x in inst_v) / 2) ** 0.5 if len(inst_v) == 3 else 0,
        )
    return rows


def parent_echo(models, base_runs, var_runs, parents, kids_of, core_exp, var_exp, tol):
    """Memorization smoking gun. For parents the model solves at base but whose
    variant instances fail: does the failed answer equal the PARENT's answer on
    the subs where parent and variant answers genuinely differ (> tol)?"""
    out = {}
    parent_hits = defaultdict(int)
    for m in models:
        br, vr = base_runs[m], var_runs[m]
        echo_runs = examined = 0
        echo_pairs, echo_parents = set(), set()
        for p in parents:
            if not maj(br, p):
                continue
            pexp = core_exp.get(p, {})
            for k in kids_of[p]:
                vexp = var_exp.get(k, {})
                disc = []
                for sub, pvals in pexp.items():
                    vvals = vexp.get(sub)
                    if not vvals:
                        continue
                    if all(not close(vv, pv, tol) for pv in pvals for vv in vvals):
                        disc.append(sub)
                if not disc:
                    continue
                for r in vr:
                    passed, _, _, fd = r[k]
                    if passed or not fd:
                        continue
                    got = [s for s in disc if s in fd]
                    if not got:
                        continue
                    examined += 1
                    if all(any(close(fd[s], pv, tol) for pv in pexp[s]) for s in got):
                        echo_runs += 1
                        echo_pairs.add(k)
                        echo_parents.add(p)
        for p in echo_parents:
            parent_hits[p] += 1
        out[m] = dict(echo_fail_runs=echo_runs, examined_fail_runs=examined,
                      echo_rate=echo_runs / examined if examined else 0.0,
                      echo_variants=len(echo_pairs), echo_parents=len(echo_parents))
    conv = sorted(parent_hits.items(), key=lambda kv: -kv[1])
    return out, [(p, c) for p, c in conv if c >= 2][:20]


def para_spectrum(models, base_runs, var_runs, parents, kids_of):
    out = {}
    for m in models:
        br, vr = base_runs[m], var_runs[m]
        dist = [0] * 6
        flip = full = none = 0
        for p in parents:
            k = sum(1 for kid in kids_of[p] if maj(vr, kid))
            dist[k] += 1
            if k == 5:
                full += 1
            elif k == 0:
                none += 1
            else:
                flip += 1
        n = len(parents)
        # run-to-run noise on base for contrast: parents solved in >=1 run but not all 3
        run_flip = sum(1 for p in parents
                       if 0 < sum(1 for r in br if r[p][0]) < 3) / n
        out[m] = dict(dist=dist, full5=full / n, none0=none / n, flip=flip / n,
                      base_run_flip=run_flip)
    return out


def failure_shift(models, base_runs, var_runs, parents, kids_of):
    out = {}
    for m in models:
        def stats(runs, ids):
            fails = ung = 0
            att_sum = att_n = 0
            for r in runs:
                for i in ids:
                    p, u, na, _ = r[i]
                    att_sum += na; att_n += 1
                    if not p:
                        fails += 1
                        ung += 1 if u else 0
            return (ung / fails if fails else 0.0), att_sum / att_n
        ids_b = parents
        ids_v = [k for p in parents for k in kids_of[p]]
        ub, ab = stats(base_runs[m], ids_b)
        uv, av = stats(var_runs[m], ids_v)
        out[m] = dict(ungradable_share_base=ub, ungradable_share_var=uv,
                      attempts_base=ab, attempts_var=av)
    return out


def strata(models, base_runs, var_runs, parents, kids_of, meta, key, min_n):
    groups = defaultdict(list)
    for p in parents:
        groups[meta[p][key]].append(p)
    out = {}
    for g, ps in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(ps) < min_n:
            continue
        deltas = []
        for m in models:
            br, vr = base_runs[m], var_runs[m]
            ab = sum(1 for p in ps if maj(br, p)) / len(ps)
            av = sum(1 for p in ps
                     if sum(1 for k in kids_of[p] if maj(vr, k)) >= (len(kids_of[p]) // 2 + 1)) / len(ps)
            deltas.append(ab - av)
        out[g] = dict(n=len(ps), mean_delta=sum(deltas) / len(deltas),
                      max_delta=max(deltas), min_delta=min(deltas))
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tol", type=float, default=0.05, help="relative tolerance (grading + echo)")
    ap.add_argument("--boot", type=int, default=0, help="bootstrap resamples for Δ CI (0=analytic only)")
    ap.add_argument("--seed", type=int, default=20260706)
    ap.add_argument("--min-stratum", type=int, default=10)
    ap.add_argument("--json", help="write full report JSON here")
    args = ap.parse_args()

    core = json.load(open(CORE_BM))
    vnum = json.load(open(NUM_BM))
    vpar = json.load(open(PARA_BM))
    meta = {p["id"]: {"difficulty": p.get("difficulty"), "category": p.get("category")} for p in core}
    core_exp = {p["id"]: expected_values(p.get("sub_answers")) for p in core}
    vnum_exp = {v["id"]: expected_values(v.get("sub_answers")) for v in vnum}
    kids_num, kids_par = defaultdict(list), defaultdict(list)
    for v in vnum:
        kids_num[v["parent_id"]].append(v["id"])
    for v in vpar:
        kids_par[v["parent_id"]].append(v["id"])

    base_ids = {p["id"] for p in core}
    num_ids = {v["id"] for v in vnum}
    par_ids = {v["id"] for v in vpar}

    base_ok, base_bad = discover_complete(BASE_DIR, base_ids)
    num_ok, num_bad = discover_complete(NUM_DIR, num_ids)
    par_ok, par_bad = discover_complete(PARA_DIR, par_ids)
    m_num = sorted(set(base_ok) & set(num_ok))
    m_par = sorted(set(base_ok) & set(par_ok))

    print("=" * 100)
    print("ROBUSTNESS REPORT  (majority-of-3 per problem; parent = majority of its 5 variants; tol=%.2f)" % args.tol)
    print("=" * 100)
    print("complete base configs : %d   excluded: %s" % (len(base_ok), ",".join(base_bad) or "-"))
    print("numeric analysis on   : %d models   excluded (incomplete variants): %s" % (len(m_num), ",".join(sorted(set(base_ok) - set(m_num))) or "-"))
    print("paraphrase analysis on: %d models   excluded: %s" % (len(m_par), ",".join(sorted(set(base_ok) - set(m_par))) or "-"))

    print("loading runs ...")
    base_runs = {m: load_runs(base_ok[m], keep_details=False) for m in set(m_num) | set(m_par)}
    num_runs = {m: load_runs(num_ok[m], keep_details=True) for m in m_num}
    par_runs = {m: load_runs(par_ok[m], keep_details=False) for m in m_par}

    parents_num = sorted(set(kids_num) & base_ids)
    parents_par = sorted(set(kids_par) & base_ids)
    report = {"config": vars(args), "rules": "maj3 problem; parent >=3/5 variants; matched parents",
              "parents_numeric": len(parents_num), "parents_paraphrase": len(parents_par),
              "models_numeric": m_num, "models_paraphrase": m_par}

    # ---- 1. contamination ----
    con = paired_block(m_num, base_runs, num_runs, parents_num, kids_num, args.boot, args.seed)
    print("\n--- 1. CONTAMINATION (core vs numeric variants, %d matched parents) ---" % len(parents_num))
    print("%-28s %8s %8s %7s %13s %9s %10s" % ("model", "core%", "variant%", "Δpt", "95%CI(Δpt)", "McNemar", "disc(b/c)"))
    for m in sorted(m_num, key=lambda x: -con[x]["delta"]):
        r = con[m]
        print("%-28s %8.1f %8.1f %+7.1f [%+5.1f,%+5.1f] %9.2g %6d/%d" % (
            m, 100 * r["acc_base_maj"], 100 * r["acc_var_parent"], 100 * r["delta"],
            100 * r["ci95"][0], 100 * r["ci95"][1], r["mcnemar_p"],
            r["discordant_base_only"], r["discordant_var_only"]))
    report["contamination"] = con

    echo, conv = parent_echo(m_num, base_runs, num_runs, parents_num, kids_num,
                             core_exp, vnum_exp, args.tol)
    print("\n--- 1b. PARENT-ECHO smoking gun (failed variant answers == parent's answer on discriminative subs) ---")
    print("%-28s %12s %12s %9s %9s" % ("model", "echo runs", "examined", "rate", "parents"))
    for m in sorted(m_num, key=lambda x: -echo[x]["echo_rate"]):
        e = echo[m]
        print("%-28s %12d %12d %8.1f%% %9d" % (m, e["echo_fail_runs"], e["examined_fail_runs"],
                                               100 * e["echo_rate"], e["echo_parents"]))
    if conv:
        print("  convergent echo parents (echoed by >=2 models):",
              ", ".join("%s(%d)" % pc for pc in conv))
    report["parent_echo"] = echo
    report["convergent_echo_parents"] = conv

    # ---- 2. paraphrase ----
    par = paired_block(m_par, base_runs, par_runs, parents_par, kids_par, args.boot, args.seed + 1)
    spec = para_spectrum(m_par, base_runs, par_runs, parents_par, kids_par)
    print("\n--- 2. PARAPHRASE robustness (core vs 5 rewordings, %d parents) ---" % len(parents_par))
    print("%-28s %8s %8s %7s %9s | %7s %7s %9s" % ("model", "core%", "para%", "Δpt", "McNemar", "5/5", "0/5", "runflip"))
    for m in sorted(m_par, key=lambda x: -par[x]["delta"]):
        r, s = par[m], spec[m]
        print("%-28s %8.1f %8.1f %+7.1f %9.2g | %6.1f%% %6.1f%% %8.1f%%" % (
            m, 100 * r["acc_base_maj"], 100 * r["acc_var_parent"], 100 * r["delta"],
            r["mcnemar_p"], 100 * s["full5"], 100 * s["none0"], 100 * s["base_run_flip"]))
    report["paraphrase"] = par
    report["paraphrase_spectrum"] = spec

    # ---- 3. ranking stability ----
    both = sorted(set(m_num) & set(m_par))
    accs = {"base": [con[m]["acc_base_maj"] for m in both],
            "numeric": [con[m]["acc_var_parent"] for m in both],
            "paraphrase": [par[m]["acc_var_parent"] for m in both]}
    print("\n--- 3. LEADERBOARD STABILITY (%d models) ---" % len(both))
    pairs = [("base", "numeric"), ("base", "paraphrase"), ("numeric", "paraphrase")]
    stab = {}
    for a, b in pairs:
        sp, kt = spearman(accs[a], accs[b]), kendall(accs[a], accs[b])
        stab["%s~%s" % (a, b)] = {"spearman": sp, "kendall": kt}
        print("  %-22s Spearman ρ=%.3f   Kendall τ=%.3f" % ("%s vs %s" % (a, b), sp, kt))
    report["rank_stability"] = stab

    # ---- 4. reasoning twins ----
    print("\n--- 4. REASONING TWINS: contamination gap Δ (numeric) ---")
    tw = []
    print("%-18s %14s %14s %10s" % ("backbone", "Δ non-reason", "Δ reasoning", "shrink"))
    for lab, nm, rm in TWINS:
        if nm in con and rm in con:
            d0, d1 = con[nm]["delta"], con[rm]["delta"]
            tw.append({"backbone": lab, "delta_nonreason": d0, "delta_reason": d1})
            print("%-18s %+14.1f %+14.1f %+10.1f" % (lab, 100 * d0, 100 * d1, 100 * (d0 - d1)))
        else:
            print("%-18s (skipped — twin incomplete)" % lab)
    report["twins_numeric"] = tw

    # ---- 5. strata ----
    print("\n--- 5. Δ BY DIFFICULTY (numeric; mean over models, min n=%d) ---" % args.min_stratum)
    sd = strata(m_num, base_runs, num_runs, parents_num, kids_num, meta, "difficulty", args.min_stratum)
    for g, r in sd.items():
        print("  %-10s n=%-4d meanΔ=%+6.1f  [min %+5.1f, max %+5.1f]" % (
            g, r["n"], 100 * r["mean_delta"], 100 * r["min_delta"], 100 * r["max_delta"]))
    sc = strata(m_num, base_runs, num_runs, parents_num, kids_num, meta, "category", args.min_stratum)
    print("--- Δ BY CATEGORY (numeric) ---")
    for g, r in sc.items():
        print("  %-28s n=%-4d meanΔ=%+6.1f" % (g, r["n"], 100 * r["mean_delta"]))
    report["strata_difficulty"] = sd
    report["strata_category"] = sc

    # ---- 6. failure-mode shift ----
    fs = failure_shift(m_num, base_runs, num_runs, parents_num, kids_num)
    print("\n--- 6. FAILURE MODE (numeric): ungradable share of failures; mean attempts ---")
    print("%-28s %12s %12s %10s %10s" % ("model", "ungr core", "ungr var", "att core", "att var"))
    for m in m_num:
        r = fs[m]
        print("%-28s %11.1f%% %11.1f%% %10.2f %10.2f" % (
            m, 100 * r["ungradable_share_base"], 100 * r["ungradable_share_var"],
            r["attempts_base"], r["attempts_var"]))
    report["failure_shift"] = fs

    if args.json:
        json.dump(report, open(args.json, "w"), indent=2, default=str)
        print("\nsaved -> %s" % args.json)


if __name__ == "__main__":
    main()
