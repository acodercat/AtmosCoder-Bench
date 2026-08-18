"""Parent-echo forensics over the numeric-variant results.

Quantifies, across ALL complete (model, run) numeric-variant results, how often a
FAILED variant answer reproduces the PARENT problem's textbook answer — and records
every such instance as an auditable evidence record.

Failure taxonomy (record-level, per failed instance-run):
  ungradable : no runnable answer (no details)
  no-disc    : gradable, but no discriminative sub was graded — uninformative.
               A sub is *discriminative* iff the parent's and the variant's expected
               answers differ by more than --tol, so an unchanged answer can never
               count as an echo.
  ECHO       : on every graded discriminative sub, the model's value matches the
               PARENT's expected answer within --tol
  near-miss  : not echo; every graded sub is within --near-tol of the VARIANT's
               expected answer (a computational slip, not memorization)
  other      : gradable, neither of the above

Echo instances are further split by whether the model also solves the parent on
the core set (majority of 3 runs):
  strict_memorization = echo AND core-solved  — the model demonstrably knows this
      exact problem and reproduces its answer instead of computing the variant's.
  attractor           = echo but core-unsolved — the parent answer is typically
      reachable from memorized standard constants while ignoring the perturbed
      inputs; evidence of value-anchoring, NOT necessarily of per-problem leakage.

All grading primitives are imported from eval.analysis.robustness so the numbers
are definitionally consistent with the robustness report.

Usage:
  uv run python -m eval.analysis.echo_forensics \
      --json pipeline/reports/echo_evidence.json
"""
import argparse
import json
from collections import defaultdict

from eval.analysis.robustness import (
    discover_complete, load_runs, expected_values, close, maj,
    CORE_BM, NUM_BM, BASE_DIR, NUM_DIR)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tol", type=float, default=0.05,
                    help="relative tolerance: grading, echo match, discriminative gate")
    ap.add_argument("--near-tol", type=float, default=0.15,
                    help="near-miss band around the variant's expected answer")
    ap.add_argument("--json", help="write the full evidence report here")
    args = ap.parse_args()
    tol, ntol = args.tol, args.near_tol

    core = json.load(open(CORE_BM))
    vnum = json.load(open(NUM_BM))
    core_exp = {p["id"]: expected_values(p.get("sub_answers")) for p in core}
    vnum_exp = {v["id"]: expected_values(v.get("sub_answers")) for v in vnum}
    parent_of = {v["id"]: v["parent_id"] for v in vnum}

    base_ids = {p["id"] for p in core}
    num_ids = {v["id"] for v in vnum}
    base_ok, _ = discover_complete(BASE_DIR, base_ids)
    num_ok, _ = discover_complete(NUM_DIR, num_ids)
    models = sorted(set(base_ok) & set(num_ok))

    # precompute discriminative subs per variant (model-independent)
    disc_of = {}
    for vid, pid in parent_of.items():
        pexp, vexp = core_exp.get(pid, {}), vnum_exp.get(vid, {})
        disc_of[vid] = [s for s, pv in pexp.items()
                        if vexp.get(s) and all(not close(vv, x, tol) for x in pv for vv in vexp[s])]

    G = defaultdict(int)
    per_model = {}
    echo_by_parent = defaultdict(int)
    evidence = []
    for m in models:
        br = load_runs(base_ok[m], keep_details=False)
        vr = load_runs(num_ok[m], keep_details=True)
        base_solved = {p: maj(br, p) for p in base_ids}
        s = defaultdict(int)
        for run_i, r in enumerate(vr, start=1):
            for vid, (passed, ungr, _, fd) in r.items():
                s["total"] += 1; G["total"] += 1
                if passed:
                    continue
                s["fails"] += 1; G["fails"] += 1
                if ungr or not fd:
                    s["ungradable"] += 1; G["ungradable"] += 1
                    continue
                pid = parent_of[vid]
                pexp, vexp = core_exp.get(pid, {}), vnum_exp.get(vid, {})
                got = [sub for sub in disc_of[vid] if sub in fd]
                if not got:
                    s["no_disc"] += 1; G["no_disc"] += 1
                    continue
                if all(any(close(fd[sub], x, tol) for x in pexp[sub]) for sub in got):
                    s["echo"] += 1; G["echo"] += 1
                    echo_by_parent[pid] += 1
                    strict = bool(base_solved.get(pid))
                    if strict:
                        s["echo_strict"] += 1; G["echo_strict"] += 1
                    evidence.append({
                        "model": m, "run": run_i, "variant_id": vid, "parent_id": pid,
                        "strict_memorization": strict,
                        "subs": [{"sub": sub, "model_answer": fd[sub],
                                  "parent_expected": pexp[sub],
                                  "variant_expected": vexp.get(sub)}
                                 for sub in got],
                    })
                elif all(any(close(a, x, ntol) for x in vexp.get(sub, []))
                         for sub, a in fd.items() if vexp.get(sub)):
                    s["near_miss"] += 1; G["near_miss"] += 1
                else:
                    s["other"] += 1; G["other"] += 1
        per_model[m] = dict(s)

    # ---------------- print ----------------
    fl = G["fails"]
    print("=" * 100)
    print("ECHO FORENSICS  (numeric variants; %d models x 3 runs; tol=%.2f near-tol=%.2f)"
          % (len(models), tol, ntol))
    print("=" * 100)
    print("instance-runs=%d  failures=%d (%.1f%%)" % (G["total"], fl, 100 * fl / G["total"]))
    print("failure taxonomy:")
    for k, lab in [("other", "other wrong"), ("near_miss", "near-miss (variant +/-%.0f%%)" % (100 * ntol)),
                   ("ungradable", "ungradable"), ("echo", "ECHO (== parent answer)"),
                   ("no_disc", "no discriminative sub")]:
        print("  %-28s %6d  (%.1f%% of failures)" % (lab, G[k], 100 * G[k] / fl))
    print("echo split: strict_memorization=%d (core-solved)   attractor=%d (core-unsolved)"
          % (G["echo_strict"], G["echo"] - G["echo_strict"]))
    print("echo share of ALL runs: %.2f%%   strict share: %.2f%%"
          % (100 * G["echo"] / G["total"], 100 * G["echo_strict"] / G["total"]))

    print("\n%-28s %7s %6s %7s %6s %6s %6s" % ("model", "fails", "ECHO", "strict", "near", "other", "ungr"))
    for m in sorted(models, key=lambda x: -per_model[x].get("echo", 0)):
        s = per_model[m]
        print("%-28s %7d %6d %7d %6d %6d %6d" % (
            m, s.get("fails", 0), s.get("echo", 0), s.get("echo_strict", 0),
            s.get("near_miss", 0), s.get("other", 0), s.get("ungradable", 0)))

    top = sorted(echo_by_parent.items(), key=lambda kv: -kv[1])
    print("\nconcentration: %d echo runs over %d parents; top10:" % (G["echo"], len(echo_by_parent)))
    for p, c in top[:10]:
        print("   %-12s %d" % (p, c))

    # ---------------- save ----------------
    if args.json:
        report = {
            "name": "parent-echo forensic evidence (numeric variants)",
            "generated": "2026-07-11",
            "criteria": {
                "tol": tol, "near_tol": ntol,
                "echo": "failed variant answer matches parent expected within tol on all graded discriminative subs",
                "discriminative_sub": "parent and variant expected answers differ by > tol",
                "strict_memorization": "echo AND the model solves the parent on the core set (majority of 3 runs)",
                "attractor": "echo but core-unsolved (value-anchoring on memorized standard constants; not per-problem leakage evidence)",
                "outcome_rule": "problem outcome = majority of 3 runs",
            },
            "n_models": len(models), "models": models,
            "global": dict(G),
            "per_model": per_model,
            "echo_by_parent": dict(sorted(echo_by_parent.items(), key=lambda kv: -kv[1])),
            "evidence": evidence,
        }
        json.dump(report, open(args.json, "w"), indent=2, ensure_ascii=False)
        print("\nsaved -> %s  (%d evidence records, %d strict)" %
              (args.json, len(evidence), G["echo_strict"]))


if __name__ == "__main__":
    main()
