"""Extract the figure-data CSVs that need live recomputation from experiments/.

    uv run python supplement/extract_figure_data.py            # all
    uv run python supplement/extract_figure_data.py forest mcq # a subset

Everything is recomputed from the stored runs (never copied from docs/), so a
re-run after any experiment refresh keeps the CSVs honest. The static CSVs
(F1, F2/F3, F4, F5, F6_3 …) come from the earlier extraction pass and are not
touched here; this script owns the four tables that either carry statistics
(forest CIs) or were found stale/missing in the 2026-08 review:

  forest       -> F6_2_forest.csv            Δ + 95% CI + Holm, both variant families
  mcq          -> F7_mcq_inflation.csv       option vs code, all-670 and clean-480, rescue rates
  trap_capture -> F6_1c_shortcut_capture.csv full-vector shortcut-capture counts per trap
  trap_family  -> F6_1b_trap_family.csv      per-family pooled solve rate (recheck/refresh)
"""
import csv
import glob
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "supplement", "figure_data")

# runner config name -> display name used across all figure CSVs
DISPLAY = {
    "gpt55-reasoning": "gpt-5.5 (reasoning)", "gemini-3.1-pro": "Gemini-3.1-Pro (reasoning)",
    "kimi-k2.6-reasoning": "Kimi K2.6 (reasoning)", "deepseek-v4-pro-reasoning": "DeepSeek-V4-pro (reasoning)",
    "qwen3.5-397b-reasoning": "Qwen-3.5-397B (reasoning)", "deepseek-v4-flash-reasoning": "DeepSeek-V4-flash (reasoning)",
    "gpt55": "gpt-5.5", "qwen3.5-397b": "Qwen-3.5-397B", "kimi-k2.6": "Kimi K2.6",
    "qwen3.6-27b-reasoning": "Qwen-3.6-27B (reasoning)", "deepseek-v4-pro": "DeepSeek-V4-pro",
    "deepseek-v4-flash": "DeepSeek-V4-flash", "qwen3.6-27b": "Qwen-3.6-27B",
    "qwen3.5-9b-reasoning": "Qwen-3.5-9B (reasoning)", "qwen3.5-9b": "Qwen-3.5-9B",
    "qwen-2.5-72b": "Qwen-2.5-72B",
}


def write(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  figure_data/{name}  ({len(rows)} rows)")


def holm(pvals):
    """Holm step-down adjusted p-values, order-preserving."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    adj, running = [0.0] * n, 0.0
    for rank, i in enumerate(order):
        running = max(running, (n - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


# ---------------------------------------------------------------- forest
def forest():
    """F6_2_forest.csv — per-model Δ(core − variant) with 95% CI and Holm p, both families.

    Runs eval.analysis.robustness (the module that owns these statistics) and reads its
    JSON report, so the figure can never drift from the analysis."""
    tmp = os.path.join(tempfile.gettempdir(), "robustness_report.json")
    subprocess.run([sys.executable, "-m", "eval.analysis.robustness", "--json", tmp],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    rep = json.load(open(tmp))
    n_parents = {"numeric": rep["parents_numeric"], "paraphrase": rep["parents_paraphrase"]}
    rows = []
    for family, block in (("numeric", rep["contamination"]), ("paraphrase", rep["paraphrase"])):
        models = [m for m in block if m in DISPLAY]
        ps = holm([float(block[m]["mcnemar_p"]) for m in models])
        for m, ph in zip(models, ps):
            r = block[m]
            lo, hi = (float(x) for x in r["ci95"])
            rows.append([DISPLAY[m], family, n_parents[family],
                         round(100 * float(r["acc_base_maj"]), 1), round(100 * float(r["acc_var_parent"]), 1),
                         round(100 * float(r["delta"]), 2), round(100 * lo, 2), round(100 * hi, 2),
                         float(r["mcnemar_p"]), round(ph, 4)])
    write("F6_2_forest.csv",
          ["model", "family", "n_parents", "core_pct", "variant_pct", "delta_pt", "ci_lo_pt",
           "ci_hi_pt", "mcnemar_p", "p_holm"], rows)


# ---------------------------------------------------------------- mcq
# Published option-mode accuracies for the three models we did not run in option mode:
# Chen et al., AtmosSci-Bench (arXiv:2502.01159), Table 2, MCQ10 (N=670).
PAPER_OPTION = {"deepseek-r1": 88.51, "deepseek-v3": 63.28, "qwen-2.5-72b": 57.01}
OPTION_DIRS = {"gemini-3.1-pro": "gemini-3.1-pro", "gpt55": "gpt-5.5", "deepseek-v4-flash": "deepseek-v4-flash"}
MCQ_NAMES = {"gemini-3.1-pro": "Gemini-3.1-Pro", "deepseek-r1": "DeepSeek-R1", "gpt55": "gpt-5.5",
             "deepseek-v4-flash": "DeepSeek-V4-flash", "deepseek-v3": "DeepSeek-V3", "qwen-2.5-72b": "Qwen-2.5-72B"}


def defective_ids():
    """The 190 problems on the 19 genuinely defective templates (21 intersection-flagged
    minus the two commensurate-unit false positives)."""
    inter = json.load(open(os.path.join(ROOT, "pipeline/reports/mcq_remove_intersection.json")))
    mcq = json.load(open(os.path.join(ROOT, "benchmark/external/atmossci_mcq.json")))
    templates = {p.get("parent_id") for p in mcq}
    bad = {p["parent_id"] for p in inter["parents"] if p["parent_id"] in templates} - {"MCQ_12", "MCQ_69"}
    return {p["id"] for p in mcq if p.get("parent_id") in bad}


def mcq():
    """F7_mcq_inflation.csv — option vs code accuracy (all-670 / clean-480) + rescue rates."""
    bad = defective_ids()

    def acc(recs, ok):
        return 100 * sum(map(ok, recs)) / len(recs)   # unrounded; round once at write time

    rows = []
    for key in ["gemini-3.1-pro", "deepseek-r1", "gpt55", "deepseek-v4-flash", "deepseek-v3", "qwen-2.5-72b"]:
        code = {r["id"]: bool(r.get("passed"))
                for r in json.load(open(os.path.join(ROOT, f"experiments/mcq_code/{key}.json")))["results"]
                if r.get("status") != "error"}
        code_all = acc(list(code), lambda i: code[i])
        clean = [i for i in code if i not in bad]
        code_clean = acc(clean, lambda i: code[i])
        if key in OPTION_DIRS:
            ev = [json.loads(l) for l in
                  open(os.path.join(ROOT, f"experiments/mcq_option/{OPTION_DIRS[key]}/evaluation.jsonl"))]
            opt = {r["id"]: r["score"] == 1.0 for r in ev}
            opt_all = acc(list(opt), lambda i: opt[i])
            opt_clean = acc([i for i in opt if i not in bad], lambda i: opt[i])
            src = "in-house"
            # rescue: of the problems the model cannot compute, how often is the letter right?
            fails = [i for i in code if not code[i] and i in opt]
            resc_n, resc_d = sum(1 for i in fails if opt[i]), len(fails)
        else:
            opt_all, opt_clean, src, resc_n, resc_d = PAPER_OPTION[key], "", "paper", "", ""
        rows.append([MCQ_NAMES[key], src, round(opt_all, 1),
                     round(opt_clean, 1) if opt_clean != "" else "",
                     round(code_all, 1), round(code_clean, 1),
                     round(opt_all - code_all, 1),
                     round(opt_clean - code_clean, 1) if opt_clean != "" else "",
                     resc_n, resc_d,
                     round(100 * resc_n / resc_d, 1) if resc_d else ""])
    write("F7_mcq_inflation.csv",
          ["model", "option_source", "option_all670", "option_clean480", "code_all670", "code_clean480",
           "delta_all670", "delta_clean480", "rescue_correct", "rescue_total", "rescue_pct"], rows)


# ---------------------------------------------------------------- traps
def load_trap_runs():
    runs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "experiments/trap/*.json"))):
        b = os.path.basename(f)
        runs.setdefault(b.split(".run")[0], {})[b.split(".run")[1][0]] = {
            r["id"]: r for r in json.load(open(f))["results"]}
    return runs


def trap_capture():
    """F6_1c_shortcut_capture.csv — runs whose whole answer vector equals the trap's
    shortcut_code output (the TRAP_RESULTS Table 4 rule: fail + every sub within 2%)."""
    traps = {t["id"]: t for t in json.load(open(os.path.join(ROOT, "benchmark/traps.json")))}
    runs = load_trap_runs()
    frontier = {"gemini-3.1-pro", "gpt55-reasoning"}
    rows = []
    for tid, t in traps.items():
        exp = [float(v) for v in t["shortcut_values"].values()]
        n, configs = 0, set()
        for m in runs:
            for r in runs[m].values():
                rec = r.get(tid)
                if not rec or rec.get("passed"):
                    continue
                act = [d.get("actual") for d in (rec.get("details") or []) if isinstance(d, dict)]
                if len(act) != len(exp):
                    continue
                try:
                    hit = all(a is not None and
                              (abs(float(a) - e) <= 0.02 * abs(e) if e else abs(float(a)) < 1e-9)
                              for a, e in zip(act, exp))
                except (TypeError, ValueError):
                    continue
                if hit:
                    n += 1
                    configs.add(m)
        if n:
            rows.append([tid.replace("trap_", "").replace("_gen", ""), t["trap_type"], n,
                         3 * len(runs), len(configs), len(runs),
                         "yes" if configs & frontier else "no"])
    rows.sort(key=lambda r: -r[2])
    write("F6_1c_shortcut_capture.csv",
          ["trap", "family", "capture_runs", "total_runs", "capture_configs", "total_configs",
           "includes_frontier"], rows)


def trap_family():
    """F6_1b_trap_family.csv — pooled per-family solve rate over all trap runs (refresh)."""
    traps = {t["id"]: t["trap_type"] for t in json.load(open(os.path.join(ROOT, "benchmark/traps.json")))}
    runs = load_trap_runs()
    agg = {}
    for m in runs:
        for r in runs[m].values():
            for tid, rec in r.items():
                fam = agg.setdefault(traps[tid], [0, 0])
                fam[0] += bool(rec.get("passed"))
                fam[1] += 1
    rows = [[f, s, n, round(100 * s / n, 1)] for f, (s, n) in
            sorted(agg.items(), key=lambda kv: kv[1][0] / kv[1][1])]
    write("F6_1b_trap_family.csv", ["family", "solved", "total", "solve_rate_pct"], rows)




# ---------------------------------------------------------------- N-series (2026-08-03)
def _acc(recs):
    p = sum(1 for r in recs if r.get("passed"))
    e = sum(1 for r in recs if r.get("status") == "error")
    return 100 * p / (len(recs) - e)


def _runs(pattern):
    """model -> run -> {id: passed} for every {model}.run{N}.json matching pattern."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, pattern))):
        b = os.path.basename(f)
        m = b.split(".run")[0].replace(".json", "")
        run = b.split(".run")[1][0] if ".run" in b else "1"
        out.setdefault(m, {})[run] = {r["id"]: bool(r.get("passed"))
                                      for r in json.load(open(f))["results"]
                                      if r.get("status") != "error"}
    return out


def scaffold():
    """F9_scaffolding.csv — accuracy with vs without handed-over knowledge (169 paired
    problems, 4 models, 3 runs) + majority-of-3 lost/gained counts."""
    orig = _runs("experiments/scaffolding_ablation/original_code/*.json")
    strp = _runs("experiments/scaffolding_ablation/stripped_code/*.json")
    order = ["gpt55", "deepseek-v4-pro", "deepseek-v4-flash", "qwen3.5-9b"]  # largest → smallest
    disp = {"gpt55": "gpt-5.5", "deepseek-v4-pro": "DeepSeek-V4-pro",
            "deepseek-v4-flash": "DeepSeek-V4-flash", "qwen3.5-9b": "Qwen-3.5-9B"}
    rows = []
    for m in order:
        oa = [100 * sum(r.values()) / len(r) for r in orig[m].values()]
        sa = [100 * sum(r.values()) / len(r) for r in strp[m].values()]
        om = sum(oa) / len(oa); sm = sum(sa) / len(sa)
        osd = (sum((x - om) ** 2 for x in oa) / (len(oa) - 1)) ** 0.5
        ssd = (sum((x - sm) ** 2 for x in sa) / (len(sa) - 1)) ** 0.5
        ids = set.intersection(*[set(r) for r in orig[m].values()],
                               *[set(r) for r in strp[m].values()])
        maj = lambda runs, i: sum(runs[k][i] for k in runs) >= 2
        lost = sum(1 for i in ids if maj(orig[m], i) and not maj(strp[m], i))
        gained = sum(1 for i in ids if not maj(orig[m], i) and maj(strp[m], i))
        rows.append([disp[m], round(om, 1), round(osd, 1), round(sm, 1), round(ssd, 1),
                     round(sm - om, 1), lost, gained, len(ids)])
    write("F9_scaffolding.csv",
          ["model", "with_acc", "with_sd", "stripped_acc", "stripped_sd", "delta",
           "lost_maj3", "gained_maj3", "n_problems"], rows)


def crossdomain():
    """F10_cross_domain.csv — per model: overall + per-domain cross-domain accuracy
    (single run, 131 problems); core accuracy joined at plot time from F4 CSV."""
    disp = {"gpt55": "gpt-5.5", "kimi-k2.6": "Kimi K2.6", "qwen3.6-27b": "Qwen-3.6-27B",
            "deepseek-v4-flash": "DeepSeek-V4-flash", "qwen-2.5-72b": "Qwen-2.5-72B"}
    strong = ["gpt55", "kimi-k2.6", "qwen3.6-27b", "deepseek-v4-flash"]
    domains = ["hydrology", "environmental_chemistry", "ecology", "soil"]
    acc = {m: {} for m in disp}
    for d in domains:
        for m in disp:
            recs = json.load(open(os.path.join(ROOT, f"experiments/cross_domain/{d}/{m}.json")))["results"]
            acc[m][d] = (sum(1 for r in recs if r.get("passed")), len(recs))
    rows = []
    for m in disp:
        tot_p = sum(acc[m][d][0] for d in domains); tot_n = sum(acc[m][d][1] for d in domains)
        rows.append([disp[m], round(100 * tot_p / tot_n, 1)] +
                    [round(100 * acc[m][d][0] / acc[m][d][1], 1) for d in domains])
    write("F10_cross_domain.csv", ["model", "overall"] + domains, rows)
    gaps = []
    for d in domains:
        s = sum(100 * acc[m][d][0] / acc[m][d][1] for m in strong) / len(strong)
        w = 100 * acc["qwen-2.5-72b"][d][0] / acc["qwen-2.5-72b"][d][1]
        gaps.append([d, round(s, 1), round(w, 1), round(s - w, 1), acc["qwen-2.5-72b"][d][1]])
    write("F10b_domain_gaps.csv", ["domain", "strong4_mean", "weak", "gap", "n"], gaps)


FRONTIER16 = [m for m in DISPLAY]  # the 16 leaderboard configs (raw names)


def discrimination():
    """F11_discrimination.csv — per core problem: how many of the 16 frontier configs
    solve it (majority-of-3) + its difficulty label."""
    core = {p["id"]: p["difficulty"] for p in
            json.load(open(os.path.join(ROOT, "benchmark/core.json")))}
    runs = _runs("experiments/core_code/*.json")
    rows = []
    for pid, diff in core.items():
        n = sum(1 for m in FRONTIER16
                if sum(runs[m][k].get(pid, False) for k in runs[m]) >= 2)
        rows.append([pid, diff, n])
    rows.sort(key=lambda r: r[2])
    write("F11_discrimination.csv", ["id", "difficulty", "solved_by_n_of_16"], rows)


def echo_funnel():
    """F12_echo_funnel.csv — the contamination evidence chain, each stage recomputed
    by the module that owns it (echo_forensics) + the released verdict file."""
    tmp = os.path.join(tempfile.gettempdir(), "echo_report.json")
    subprocess.run([sys.executable, "-m", "eval.analysis.echo_forensics", "--json", tmp],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    rep = json.load(open(tmp))["global"]
    tot, fails, echo, strict = rep["total"], rep["fails"], rep["echo"], rep["echo_strict"]
    verdict = json.load(open(os.path.join(ROOT, "pipeline/reports/contamination_final.json")))["counts"]
    rows = [["variant instance-runs", tot, "1730 variants × 16 configs × 3 runs"],
            ["failed runs", fails, "gradable-or-not, all failure kinds"],
            ["parent-echo runs", echo, "answer == parent's on every discriminative sub (>5% apart)"],
            ["strict-memorisation runs", strict, "echo AND the model solves the parent on the core set"],
            ["problems confirmed leaked", verdict["confirmed_leaked"], "≥2 independent models show strict memorisation"]]
    write("F12_echo_funnel.csv", ["stage", "count", "criterion"], rows)


# ---------------------------------------------------------------- F13-F16 (2026-08-03)
TWINS = [("gpt-5.5", "gpt55", "gpt55-reasoning"),
         ("DeepSeek-V4-pro", "deepseek-v4-pro", "deepseek-v4-pro-reasoning"),
         ("DeepSeek-V4-flash", "deepseek-v4-flash", "deepseek-v4-flash-reasoning"),
         ("Qwen-3.6-27B", "qwen3.6-27b", "qwen3.6-27b-reasoning"),
         ("Qwen-3.5-9B", "qwen3.5-9b", "qwen3.5-9b-reasoning"),
         ("Qwen-3.5-397B", "qwen3.5-397b", "qwen3.5-397b-reasoning"),
         ("Kimi K2.6", "kimi-k2.6", "kimi-k2.6-reasoning")]


def _core_runs_full():
    """model -> run -> {id: record} over the 16 frontier configs."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "experiments/core_code/*.json"))):
        b = os.path.basename(f)
        m = b.split(".run")[0]
        if m not in DISPLAY:
            continue
        out.setdefault(m, {})[b.split(".run")[1][0]] = {
            r["id"]: r for r in json.load(open(f))["results"] if r.get("status") != "error"}
    return out


def _setting(display_name):
    return "reasoning" if "(reasoning)" in display_name else "non-reasoning"


def repair():
    """F13_repair_budget.csv — cumulative accuracy at attempt budget k (a record passes
    at budget k iff it passed and its passing code arrived within the first k content
    attempts; wrong-but-gradable answers are never retried, so this is exact)."""
    runs = _core_runs_full()
    rows = []
    for m, byrun in runs.items():
        accs = {k: [] for k in range(1, 6)}
        share = []
        for r in byrun.values():
            n = len(r)
            for k in range(1, 6):
                accs[k].append(100 * sum(1 for x in r.values()
                                         if x.get("passed") and x.get("num_attempts", 1) <= k) / n)
            tot = sum(1 for x in r.values() if x.get("passed"))
            rep = sum(1 for x in r.values() if x.get("passed") and x.get("num_attempts", 1) > 1)
            share.append(100 * rep / tot if tot else 0)
        rows.append([DISPLAY[m], _setting(DISPLAY[m])] +
                    [round(sum(accs[k]) / 3, 1) for k in range(1, 6)] +
                    [round(sum(share) / 3, 1)])
    rows.sort(key=lambda r: -(r[6] - r[2]))
    write("F13_repair_budget.csv",
          ["model", "setting", "acc_k1", "acc_k2", "acc_k3", "acc_k4", "acc_k5",
           "repair_share_of_passes_pct"], rows)


def lift():
    """F14_reasoning_lift.csv — Δ accuracy (reasoning − non-reasoning) per difficulty
    stratum, per twin backbone (3-run mean per side)."""
    core = {p["id"]: p["difficulty"] for p in
            json.load(open(os.path.join(ROOT, "benchmark/core.json")))}
    strata = {d: [i for i, dd in core.items() if dd == d] for d in ("low", "medium", "high")}
    runs = _core_runs_full()

    def acc(m, ids):
        return sum(100 * sum(1 for i in ids if r[i].get("passed")) / len(ids)
                   for r in runs[m].values()) / 3

    rows = []
    for label, nr, rr in TWINS:
        d = {k: round(acc(rr, ids) - acc(nr, ids), 1) for k, ids in strata.items()}
        overall = round(acc(rr, list(core)) - acc(nr, list(core)), 1)
        rows.append([label, d["low"], d["medium"], d["high"], overall])
    write("F14_reasoning_lift.csv", ["backbone", "low", "medium", "high", "overall"], rows)


def tolerance():
    """F15_core_tolerance.csv — offline re-grade of every core_code record at
    1/2/5/10% via eval.analysis.accuracy.regrade_record (the module verified to
    reproduce the runner's 5% pass counts exactly)."""
    sys.path.insert(0, ROOT)
    from eval.analysis.accuracy import regrade_record
    tols = (0.01, 0.02, 0.05, 0.10)
    runs = _core_runs_full()
    rows = []
    for m, byrun in runs.items():
        acc = {t: [] for t in tols}
        for r in byrun.values():
            for t in tols:
                acc[t].append(100 * sum(1 for x in r.values() if regrade_record(x, t)) / len(r))
        rows.append([DISPLAY[m], _setting(DISPLAY[m])] +
                    [round(sum(acc[t]) / 3, 1) for t in tols])
    rows.sort(key=lambda r: -r[4])
    write("F15_core_tolerance.csv",
          ["model", "setting", "acc_1pct", "acc_2pct", "acc_5pct", "acc_10pct"], rows)


def arity():
    """F16_arity.csv — mean per-problem pass rate (16 configs x 3 runs = 48
    measurements per problem) by difficulty x number of distinct sub-answers."""
    core = {p["id"]: p for p in json.load(open(os.path.join(ROOT, "benchmark/core.json")))}
    runs = _core_runs_full()
    hit = {i: [0, 0] for i in core}
    for m in runs:
        for r in runs[m].values():
            for i, x in r.items():
                hit[i][0] += bool(x.get("passed"))
                hit[i][1] += 1
    rate = {i: 100 * p / n for i, (p, n) in hit.items()}

    def bucket(i):
        k = len({s["sub"] for s in core[i]["sub_answers"]})
        return "1" if k == 1 else "2" if k == 2 else "3+"

    rows = []
    for d in ("low", "medium", "high"):
        for a in ("1", "2", "3+"):
            ids = [i for i in core if core[i]["difficulty"] == d and bucket(i) == a]
            if ids:
                rows.append([d, a, len(ids), round(sum(rate[i] for i in ids) / len(ids), 1)])
    write("F16_arity.csv", ["difficulty", "subs", "n_problems", "mean_pass_pct"], rows)


# ---------------------------------------------------------------- F17-F19 (atlas figures)
def solve_matrix():
    """F17_solve_matrix.csv — the whole benchmark as one binary matrix: 436 problems x
    16 configurations, solved = majority-of-3 runs."""
    core = {p["id"]: p["difficulty"] for p in
            json.load(open(os.path.join(ROOT, "benchmark/core.json")))}
    runs = _core_runs_full()
    order = [m for m in runs]
    maj = {m: {i: int(sum(r.get(i, {}).get("passed", False) for r in runs[m].values()) >= 2)
               for i in core} for m in order}
    rows = []
    for i in core:
        rows.append([i, core[i], sum(maj[m][i] for m in order)] + [maj[m][i] for m in order])
    rows.sort(key=lambda r: (-r[2], {"low": 0, "medium": 1, "high": 2}[r[1]]))
    write("F17_solve_matrix.csv", ["id", "difficulty", "solved_by"] +
          [DISPLAY[m] for m in order], rows)


def trap_matrix():
    """F18_trap_matrix.csv — per (trap, model, run) verdict: pass / fail / captured,
    captured = the full-vector shortcut rule of TRAP_RESULTS Table 4."""
    traps = {t["id"]: t for t in json.load(open(os.path.join(ROOT, "benchmark/traps.json")))}
    runs = load_trap_runs()
    rows = []
    for tid, t in traps.items():
        exp = [float(v) for v in t["shortcut_values"].values()]
        for m in runs:
            for run, rec_by_id in runs[m].items():
                rec = rec_by_id.get(tid)
                state = "pass" if rec.get("passed") else "fail"
                if state == "fail":
                    act = [d.get("actual") for d in (rec.get("details") or [])
                           if isinstance(d, dict)]
                    try:
                        if len(act) == len(exp) and all(
                                a is not None and
                                (abs(float(a) - e) <= 0.02 * abs(e) if e else abs(float(a)) < 1e-9)
                                for a, e in zip(act, exp)):
                            state = "captured"
                    except (TypeError, ValueError):
                        pass
                rows.append([tid.replace("trap_", "").replace("_gen", ""), t["trap_type"],
                             m, run, state])
    write("F18_trap_matrix.csv", ["trap", "family", "model", "run", "state"], rows)


ANATOMY = {"4.5": 1, "ry_7.7": 0}   # problem -> index of the diagnostic sub-answer


def answer_space():
    """F19_answer_space.csv — every run's actual answer on two hand-verified case
    problems (FAILURE_CASES.md): the diagnostic sub of `4.5` and `ry_7.7`."""
    core = {p["id"]: p for p in json.load(open(os.path.join(ROOT, "benchmark/core.json")))}
    runs = _core_runs_full()
    rows = []
    for pid, sub_ix in ANATOMY.items():
        expected = core[pid]["sub_answers"][sub_ix]["value"]
        for m in runs:
            for run, r in runs[m].items():
                rec = r.get(pid)
                det = [d for d in (rec.get("details") or []) if isinstance(d, dict)]
                if len(det) > sub_ix and isinstance(det[sub_ix].get("actual"), (int, float)):
                    val, sp = det[sub_ix]["actual"], int(bool(det[sub_ix].get("passed")))
                else:
                    val, sp = "", ""   # ungradable / missing sub
                rows.append([pid, expected, DISPLAY[m], run, val, sp])
    write("F19_answer_space.csv",
          ["problem", "expected", "model", "run", "actual", "sub_passed"], rows)


# ---------------------------------------------------------------- F20-F22
def mcq_verdicts():
    """F20_mcq_verdicts.csv — per problem x dual-mode model: both / option-only /
    code-only / neither, plus whether the problem sits on a defective template."""
    bad = defective_ids()
    out = []
    for ck, od in OPTION_DIRS.items():
        code = {r["id"]: bool(r.get("passed"))
                for r in json.load(open(os.path.join(ROOT, f"experiments/mcq_code/{ck}.json")))["results"]
                if r.get("status") != "error"}
        opt = {r["id"]: r["score"] == 1.0 for r in
               (json.loads(l) for l in
                open(os.path.join(ROOT, f"experiments/mcq_option/{od}/evaluation.jsonl")))}
        for i in code:
            state = ("both" if code[i] and opt[i] else "option-only" if opt[i]
                     else "code-only" if code[i] else "neither")
            out.append([i, "yes" if i in bad else "no", MCQ_NAMES[ck], state])
    write("F20_mcq_verdicts.csv", ["id", "defective", "model", "state"], out)


_DIMLESS = {"", "dimensionless", "fraction", "unitless", "1", "-", "none"}


def unit_rescue():
    """F21_unit_rescue.csv — passing core sub-answers that FAIL the bare numeric
    compare and pass only through the engine's unit reconciliation (exact replay of
    eval.engine.compare_values on the stored details)."""
    sys.path.insert(0, ROOT)
    from eval.engine import compare_values
    pairs, per_model, tot_pass, tot_resc = {}, {}, 0, 0
    for f in sorted(glob.glob(os.path.join(ROOT, "experiments/core_code/*.json"))):
        m = os.path.basename(f).split(".run")[0]
        if m not in DISPLAY:
            continue
        for r in json.load(open(f))["results"]:
            for d in (r.get("details") or []):
                if not isinstance(d, dict) or not d.get("passed"):
                    continue
                a = d.get("actual")
                if not isinstance(a, (int, float)):
                    continue
                tot_pass += 1
                if any(compare_values(str(e), a, 0.05) for e in (d.get("expected") or [])):
                    continue
                tot_resc += 1
                per_model[DISPLAY[m]] = per_model.get(DISPLAY[m], 0) + 1
                eu = str((d.get("expected_units") or [""])[0]).strip()
                au = str(d.get("actual_unit", "")).strip()
                au_c = "dimensionless" if au.lower() in _DIMLESS else au
                pairs[(eu, au_c)] = pairs.get((eu, au_c), 0) + 1
    rows = sorted(([eu, au, n] for (eu, au), n in pairs.items()), key=lambda r: -r[2])
    write("F21_unit_rescue.csv", ["expected_unit", "answered_unit", "count"], rows)
    write("F21b_unit_totals.csv", ["model", "rescued"],
          sorted(per_model.items(), key=lambda kv: -kv[1]) +
          [["__total_passing__", tot_pass], ["__total_rescued__", tot_resc]])
    print(f"  rescued {tot_resc} / {tot_pass} passing sub-answers "
          f"({100 * tot_resc / tot_pass:.2f}%)")


def fragility():
    """F22_fragility.csv — parent x model outcome over the numeric-variant family:
    both / fragile (core solved, variants lost) / gained / neither."""
    par = {}
    for v in json.load(open(os.path.join(ROOT, "benchmark/variants_numeric.json"))):
        par.setdefault(v["parent_id"], []).append(v["id"])
    leaked = set(json.load(open(os.path.join(ROOT,
                 "pipeline/reports/contamination_final.json")))["confirmed_leaked"])
    cruns = _core_runs_full()
    vruns = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "experiments/variants_numeric_code/*.json"))):
        m = os.path.basename(f).split(".run")[0]
        if m not in DISPLAY:
            continue
        vruns.setdefault(m, {})[os.path.basename(f).split(".run")[1][0]] = {
            r["id"]: bool(r.get("passed")) for r in json.load(open(f))["results"]}
    maj = lambda runs, i: sum(r.get(i, {}).get("passed", False) if isinstance(r.get(i), dict)
                              else r.get(i, False) for r in runs.values()) >= 2
    rows = []
    for m in cruns:
        for p, kids in par.items():
            c = maj(cruns[m], p)
            v = sum(1 for k in kids if maj(vruns[m], k)) >= 3
            state = "both" if c and v else "fragile" if c else "gained" if v else "neither"
            rows.append([p, "yes" if p in leaked else "no", DISPLAY[m], state])
    write("F22_fragility.csv", ["parent", "leaked", "model", "state"], rows)


def trap_family_matrix():
    """F6_1b_matrix.csv — solve rate per configuration x trap family (all three runs
    pooled per cell), with the per-family pooled row and per-configuration overall."""
    traps = {t["id"]: t["trap_type"] for t in
             json.load(open(os.path.join(ROOT, "benchmark/traps.json")))}
    fams = ["regime_boundary", "geometry_detail", "sign_direction",
            "formula_selection", "definition_confusion", "averaging_space"]
    ids_of = {f: [i for i, t in traps.items() if t == f] for f in fams}
    runs = load_trap_runs()
    # configurations ordered by their own overall trap accuracy, strongest first
    overall = {m: sum(1 for r in runs[m].values() for i in traps
                      if r[i].get("passed")) / (len(traps) * len(runs[m]))
               for m in runs}
    order = sorted(runs, key=lambda m: -overall[m])
    rows = []
    for m in order:
        cells = []
        for f in fams:
            n = len(ids_of[f]) * len(runs[m])
            p = sum(1 for r in runs[m].values() for i in ids_of[f] if r[i].get("passed"))
            cells.append(round(100 * p / n, 1))
        rows.append([m, round(100 * overall[m], 1)] + cells)
    pooled = []
    for f in fams:
        n = sum(len(ids_of[f]) * len(runs[m]) for m in runs)
        p = sum(1 for m in runs for r in runs[m].values() for i in ids_of[f] if r[i].get("passed"))
        pooled.append(round(100 * p / n, 1))
    rows.append(["__pooled__", round(100 * sum(overall.values()) / len(overall), 1)] + pooled)
    write("F6_1b_matrix.csv", ["model", "overall"] + fams, rows)
    write("F6_1b_family_sizes.csv", ["family", "n_traps"],
          [[f, len(ids_of[f])] for f in fams])


# ---------------------------------------------------------------- tokens (single source)
# Every token number in this supplement is read from `result.usage`, which since the 2026-08-09
# migration holds the repo's own uniform o200k recount of the stored text for every record in
# every experiment directory (eval/store.py._o200k_usage, cross-checked field by field against
# eval.analysis.token_count: 18/18 configurations on core_code). That is the same accounting the
# result docs use, so a figure and a table can no longer disagree about what a token is.
#
# History worth keeping, because it is why the closing check in the README exists: before the
# migration `result.usage` meant different things in different directories -- store.py rewrites
# a record's usage only when it writes that record, so resumed files kept the provider's own
# numbers. core_code/trap/variants_*/scaffolding_ablation carried provider counts while
# core_direct/cross_domain/mcq_code carried o200k recounts, and reading the field across
# directories silently mixed the two: it flipped the direct/code token ratio for gpt-5.5
# (reasoning) from 1.20 to 0.60 and would have overturned "direct never costs fewer tokens".
#
# The cost of counting ourselves is that we can only count text a provider echoes. Two
# configurations return a summary of the chain of thought rather than the whole of it, so their
# totals are lower bounds; `tokens_understated_dagger` marks them from measurement rather than
# from a hard-coded list (see DAGGER_RATIO).
#
#   cost figures  (F2b / F4 / F4b) -> total_tokens      = prompt + completion + reasoning
#   output length (F4c)            -> completion_tokens = the visible answer text
BACKBONE = {"gpt-5.5": "gpt55", "Qwen-3.5-397B": "qwen3.5-397b", "Kimi K2.6": "kimi-k2.6",
            "DeepSeek-V4-pro": "deepseek-v4-pro", "DeepSeek-V4-flash": "deepseek-v4-flash",
            "Qwen-3.6-27B": "qwen3.6-27b", "Qwen-3.5-9B": "qwen3.5-9b"}

# A configuration is flagged as understated when the provider's own total exceeds our recount by
# this factor. Measured on core_code the two summary-only endpoints sit at 2.03x (gpt-5.5
# reasoning, /v1/responses concise summary) and 1.81x (Gemini-3.1-Pro, native thought summary)
# while every other reasoning configuration lands in 0.68-1.06x, so the gap is wide and 1.25 is
# nowhere near either side of it.
DAGGER_RATIO = 1.25


def _run_files(exp, key):
    return sorted(glob.glob(os.path.join(ROOT, "experiments", exp, f"{key}.run*.json")))


def rec_tokens(record, field="total_tokens"):
    """The repo's own o200k count for one problem, summed over the self-repair attempts."""
    return (record.get("usage") or {}).get(field) or 0


def provider_tokens(record, field="total_tokens"):
    """The provider's own count for the same problem, kept per attempt as raw data. Used only
    to decide whether our recount is a lower bound, never as a reported number."""
    return sum((a.get("usage") or {}).get(field) or 0 for a in record.get("attempts") or [])


def _run_stats(path, field):
    """(our token total, provider token total, accuracy%) for one run file."""
    res = json.load(open(path))["results"]
    graded = [r for r in res if r.get("outcome") != "error" and r.get("status") != "error"]
    acc = 100 * sum(1 for r in graded if r.get("passed")) / len(graded) if graded else float("nan")
    return (sum(rec_tokens(r, field) for r in res),
            sum(provider_tokens(r, field) for r in res), acc)


def _mean_sd(v):
    m = sum(v) / len(v)
    sd = (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5 if len(v) > 1 else 0.0
    return m, sd


def _dagger(ours, theirs):
    return "yes" if ours and theirs / ours >= DAGGER_RATIO else "no"


def tokens():
    """F4_token_accuracy.csv — per-configuration cost and accuracy, both live from the runs."""
    rows = []
    for key, disp in DISPLAY.items():
        fs = _run_files("core_code", key)
        if not fs:
            continue
        stats = [_run_stats(f, "total_tokens") for f in fs]
        tm, _ = _mean_sd([t for t, _p, _a in stats])
        pm, _ = _mean_sd([p for _t, p, _a in stats])
        am, asd = _mean_sd([a for _t, _p, a in stats])
        rows.append([disp, round(tm / 1e6, 3), round(am, 1), round(asd, 1),
                     "reasoning" if "(reasoning)" in disp else "non-reasoning",
                     BACKBONE.get(disp.replace(" (reasoning)", ""), ""), _dagger(tm, pm)])
    write("F4_token_accuracy.csv",
          ["model", "tokens_M_per_run", "accuracy", "sd", "setting", "backbone_pair",
           "tokens_understated_dagger"], rows)


def protocol_tokens():
    """F2_F3_direct_vs_code.csv — the six configurations run under both protocols."""
    rows = []
    for key, disp in DISPLAY.items():
        if not (_run_files("core_code", key) and _run_files("core_direct", key)):
            continue
        c = [_run_stats(f, "total_tokens") for f in _run_files("core_code", key)]
        d = [_run_stats(f, "total_tokens") for f in _run_files("core_direct", key)]
        ct, _ = _mean_sd([t for t, _p, _a in c]); ca, csd = _mean_sd([a for _t, _p, a in c])
        dt, _ = _mean_sd([t for t, _p, _a in d]); da, dsd = _mean_sd([a for _t, _p, a in d])
        cp, _ = _mean_sd([p for _t, p, _a in c]); dp, _ = _mean_sd([p for _t, p, _a in d])
        flag = "yes" if "yes" in (_dagger(ct, cp), _dagger(dt, dp)) else "no"
        rows.append([disp, round(ca, 1), round(csd, 1), round(da, 1), round(dsd, 1),
                     f"{ca - da:+.1f}", round(ct / 1e6, 3), round(dt / 1e6, 3),
                     round(dt / ct, 2), flag])
    rows.sort(key=lambda r: -r[6])
    write("F2_F3_direct_vs_code.csv",
          ["model", "code_acc", "code_sd", "direct_acc", "direct_sd", "delta_code_minus_direct",
           "code_tokens_M", "direct_tokens_M", "token_ratio_direct_over_code",
           "tokens_understated_dagger"], rows)


def spend_dist():
    """F4d_spend_hist.csv / F4d_spend_quantiles.csv — the distribution of output tokens a
    configuration spends on a single problem, not just its mean.

    Every token figure so far reports a per-run mean, which is a poor summary for a
    heavy-tailed spender: Kimi K2.6's mean is over three times its median. The unit here is one
    problem-run (436 problems x 3 runs); output tokens are completion + reasoning from
    `result.usage`, the repo's own o200k count. The histogram is stored in log10 space so a
    ridgeline can be drawn without shipping 23,000 raw values.
    """
    import math
    LO, HI, W = 1.7, 5.6, 0.1          # 50 tokens to ~400k, decade split into ten bins
    nb = int(round((HI - LO) / W))
    hist, quant = [], []
    for exp, (key, disp) in ((e, kv) for e in ("core_code", "core_direct")
                             for kv in DISPLAY.items()):
        vals = []
        for f in _run_files(exp, key):
            for r in json.load(open(f))["results"]:
                u = r.get("usage") or {}
                t = (u.get("completion_tokens") or 0) + (u.get("reasoning_tokens") or 0)
                if t > 0:
                    vals.append(t)
        if len(vals) < 50:
            continue
        vals.sort()
        n = len(vals)
        q = lambda pr: vals[min(n - 1, int(pr * n))]
        counts = [0] * nb
        for t in vals:
            b = int((math.log10(t) - LO) / W)
            if 0 <= b < nb:
                counts[b] += 1
        setting = "reasoning" if "(reasoning)" in disp else "non-reasoning"
        prot = "code" if exp == "core_code" else "direct"
        for b, c in enumerate(counts):
            hist.append([disp, prot, setting, round(LO + b * W, 2),
                         round(LO + (b + 1) * W, 2), c])
        quant.append([disp, prot, setting, n, q(.10), q(.25), q(.50), q(.75), q(.90), q(.99),
                      round(sum(vals) / n, 1), round(q(.90) / q(.50), 2),
                      round((sum(vals) / n) / q(.50), 2)])
    write("F4d_spend_hist.csv",
          ["model", "protocol", "setting", "log10_lo", "log10_hi", "n_problem_runs"], hist)
    write("F4d_spend_quantiles.csv",
          ["model", "protocol", "setting", "n_problem_runs", "p10", "p25", "p50", "p75", "p90",
           "p99", "mean", "p90_over_p50", "mean_over_p50"], quant)


def token_bins():
    """F4c_token_bins.csv — accuracy against how many output tokens the model itself chose to
    spend on a problem, binned by powers of two, split by difficulty stratum.

    Output tokens come from `result.usage.completion_tokens`, the repo's own o200k count of the
    answer text the model actually wrote. Only single-attempt records are kept: tokens are summed over the self-repair loop, so
    a record that needed k attempts carries roughly k times the tokens AND is far likelier to be
    a failure, which would manufacture the very decline the figure is about. Difficulty is the
    intrinsic rubric label from benchmark/core.json, assigned before any model was run.
    """
    import math
    diff = {p["id"]: p.get("difficulty")
            for p in json.load(open(os.path.join(ROOT, "benchmark", "core.json")))}
    rows = []
    for key, disp in DISPLAY.items():
        acc = {}
        kept = dropped = 0
        for f in _run_files("core_code", key):
            for r in json.load(open(f))["results"]:
                out = rec_tokens(r, "completion_tokens")
                if out <= 0:
                    continue
                if r.get("num_attempts", 1) != 1:
                    dropped += 1
                    continue
                kept += 1
                cell = acc.setdefault((diff.get(r["id"], "unknown"), int(math.log2(out))), [0, 0])
                cell[0] += 1
                cell[1] += bool(r["passed"])
        setting = "reasoning" if "(reasoning)" in disp else "non-reasoning"
        for (lv, b) in sorted(acc):
            n, ok = acc[(lv, b)]
            rows.append([disp, setting, lv, b, 2 ** b, n, ok, round(100 * ok / n, 2),
                         round(100 * kept / (kept + dropped), 1)])
    write("F4c_token_bins.csv",
          ["model", "setting", "difficulty", "log2_bin", "bin_low_tokens", "n_problem_runs",
           "n_passed", "accuracy_pct", "single_attempt_pct"], rows)


def run_outcomes():
    """F24_run_outcomes.csv — one row per (problem, configuration, run): the long table the
    three-run-mean basis needs.

    F17_solve_matrix.csv stores a majority-of-three verdict per (problem, configuration) and so
    can only ever yield majority-of-three rates. Every accuracy in docs/results/ is instead the
    mean over the three runs, and the two bases disagree by up to 1.6 points because a majority
    absorbs one flaky run. This table keeps the runs apart, which is what makes a per-cell
    standard deviation possible at all; it also subsumes pass@3, all@3 and any re-stratification,
    and lets a reader recompute a figure without touching gitignored experiments/.

    The two ClimateGPT configurations are excluded, matching the 16-configuration leaderboard.
    """
    core = {p["id"]: (p.get("category"), p.get("difficulty"))
            for p in json.load(open(os.path.join(ROOT, "benchmark", "core.json")))}
    rows, excluded = [], 0
    for key, disp in DISPLAY.items():
        for f in _run_files("core_code", key):
            run = int(f.rsplit(".run", 1)[1].split(".")[0])
            for r in json.load(open(f))["results"]:
                cat, diff = core.get(r["id"], (None, None))
                err = 1 if r.get("error") else 0
                excluded += err
                rows.append([r["id"], cat, diff, disp, run, int(bool(r.get("passed"))), err])
    rows.sort(key=lambda t: (t[3], t[4], t[0]))
    write("F24_run_outcomes.csv",
          ["id", "category", "difficulty", "model", "run", "passed", "excluded"], rows)
    print(f"    {len(rows):,} rows; infrastructure-error records: {excluded}")


def composition():
    """F0_core_composition.csv — the corpus itself: category size x difficulty stratum.

    Read straight from benchmark/core.json (the frozen dataset), not from experiments/,
    because this table describes what was built rather than how anything scored.
    """
    core = json.load(open(os.path.join(ROOT, "benchmark", "core.json")))
    cats = sorted({p["category"] for p in core},
                  key=lambda c: -sum(1 for p in core if p["category"] == c))
    rows = []
    for c in cats:
        sub = [p for p in core if p["category"] == c]
        n = {d: sum(1 for p in sub if p["difficulty"] == d) for d in ("low", "medium", "high")}
        rows.append([c, len(sub), n["low"], n["medium"], n["high"],
                     sum(1 for p in sub if p.get("numeric_variantable")),
                     len({p["book"] for p in sub})])
    tot = [p["difficulty"] for p in core]
    rows.append(["ALL", len(core)] + [tot.count(d) for d in ("low", "medium", "high")]
                + [sum(1 for p in core if p.get("numeric_variantable")),
                   len({p["book"] for p in core})])
    write("F0_core_composition.csv",
          ["category", "n_total", "n_low", "n_medium", "n_high",
           "n_numeric_variantable", "n_books"], rows)


JOBS = {"composition": composition, "run_outcomes": run_outcomes, "tokens": tokens,
        "protocol_tokens": protocol_tokens, "spend_dist": spend_dist,
        "token_bins": token_bins,
        "forest": forest, "mcq": mcq, "trap_capture": trap_capture, "trap_family": trap_family,
        "scaffold": scaffold, "crossdomain": crossdomain, "discrimination": discrimination,
        "echo_funnel": echo_funnel, "repair": repair, "lift": lift,
        "tolerance": tolerance, "arity": arity,
        "solve_matrix": solve_matrix, "trap_matrix": trap_matrix, "answer_space": answer_space,
        "mcq_verdicts": mcq_verdicts, "unit_rescue": unit_rescue, "fragility": fragility,
        "trap_family_matrix": trap_family_matrix}

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(JOBS)):
        print(f"{k}:")
        JOBS[k]()
