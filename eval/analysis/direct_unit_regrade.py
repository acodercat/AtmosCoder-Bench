"""Offline unit-aware re-grade of the DIRECT protocol. Read-only.

The direct prompt forbids units inside the box ("just the number, no units or text"),
so a direct answer reaches the grader as a bare float and `eval.engine._units_reconcile`
— which needs a declared unit on BOTH sides — can never fire for it. The code protocol's
solver contract supplies `{"value", "unit"}`, so the same engine feature fires constantly
there. Part of the measured code-vs-direct gap is therefore an artifact of answer
ENCODING rather than answer QUALITY.

The units are usually present in the model's prose, just outside the box ("... ≈ 11232 m
… \\boxed{11232}"). This script recovers them and re-applies the engine's own
reconciliation, so the direct arm is graded on the same footing as the code arm.

Two re-grades are reported, bracketing the fair value:
  A  unit-aware, alignment unchanged   — the conservative fix (units only)
  B  unit-aware + order/subset-tolerant matching — an UPPER BOUND that also forgives the
     positional misalignment caused by models emitting more boxes than there are stored
     sub-answers

Original experiment files are never modified; results go to the --out JSON.

Usage:
    uv run python -m eval.analysis.direct_unit_regrade
    uv run python -m eval.analysis.direct_unit_regrade --exp-dir experiments/core_direct
"""

import re
import json
import glob
import os
import argparse
from itertools import permutations

from eval.engine import _units_reconcile, compare_values, _UNIT_FACTORS
from eval.protocols import _balanced_boxed

# Unit vocabulary: the engine's own scalar units, plus common compound forms the
# compound parser understands. Longest-first so "km" wins over "m".
_UNIT_WORDS = sorted(
    set(_UNIT_FACTORS) | {
        "m/s", "m s^-1", "m s^{-1}", "km/s", "cm/s", "mm/s", "km/h",
        "w/m^2", "w m^-2", "w m^{-2}", "j/kg", "kg/m^3", "g/m^3", "g/cm^3",
        "mol/l", "mg/l", "ug/m^3", "molecules/cm^3", "molecules cm^-3",
        "cm^3/s", "cm^3/min", "m^3/s", "m^2/s", "s^-1", "s^{-1}", "day^-1",
    },
    key=len, reverse=True)

# latex decoration that can sit between the number and its unit
_SEP = r"(?:\s|\\[,;:!]|~|\\ |\\quad|\\qquad|\$|\\,|\\;)*"
_WRAP = r"(?:\\(?:mathrm|text|rm|mbox|textrm|operatorname)\s*\{([^}]*)\}|([A-Za-z°%µ][A-Za-z0-9°%µ/^\-\{\}\.\s]*))"


def _clean_unit(raw: str) -> str:
    """Normalise a captured unit string into something the engine can parse."""
    if not raw:
        return ""
    u = raw.strip()
    u = re.sub(r"\\(?:mathrm|text|rm|mbox|textrm|operatorname)\s*\{([^}]*)\}", r"\1", u)
    u = u.replace("\\,", " ").replace("\\;", " ").replace("~", " ").replace("$", "")
    u = u.replace("{", "").replace("}", "").replace("\\", "")
    u = u.replace("−", "-").replace("·", " ").strip(" .,:;()")
    u = re.sub(r"\s+", " ", u)
    # trailing prose ("m of sea level rise") -> keep the leading unit token only
    parts = u.split(" ")
    if len(parts) > 2:
        u = " ".join(parts[:2])
    return u.strip()


def _looks_like_unit(u: str) -> bool:
    if not u:
        return False
    low = u.lower()
    if low in _UNIT_FACTORS:
        return True
    head = re.split(r"[ /^]", low)[0]
    return head in _UNIT_FACTORS or low in {w.lower() for w in _UNIT_WORDS}


def _number_variants(value: float) -> list[str]:
    """String forms a model might have written for this number."""
    out = set()
    for s in (repr(value), f"{value:g}", f"{value:.10g}", f"{value:.6g}", f"{value:.4g}",
              f"{value:.3g}", f"{value:.2f}", f"{value:.1f}"):
        s = s.rstrip("0").rstrip(".") if "." in s and "e" not in s.lower() else s
        if s and s not in ("-", ""):
            out.add(s)
    return [re.escape(s) for s in out if len(s) >= 1]


def unit_for_value(text: str, value: float) -> str:
    """Find the unit the model wrote next to `value` anywhere in its response."""
    if value is None:
        return ""
    for num in sorted(_number_variants(value), key=len, reverse=True):
        for m in re.finditer(num + r"(?![0-9])" + _SEP + _WRAP, text):
            u = _clean_unit(m.group(1) or m.group(2) or "")
            if _looks_like_unit(u):
                return u
    return ""


def _sub_ok(expected_list, actual, unit, tol):
    """Engine-identical check: plain compare, then unit reconciliation."""
    for exp in expected_list:
        if compare_values(str(exp), actual, tol):
            return True
    return False


def _sub_ok_units(expected_list, expected_unit, actual, actual_unit, tol):
    if _sub_ok(expected_list, actual, actual_unit, tol):
        return True
    if not actual_unit or not expected_unit:
        return False
    return any(_units_reconcile(str(exp), expected_unit, actual, actual_unit, tol)
               for exp in expected_list)


def regrade_record(record, problem, tol):
    """Return (orig_pass, unit_aware_pass, subset_pass, evidence)."""
    details = record.get("details") or []
    if not details:
        return None
    orig = bool(record.get("passed"))
    subs = problem.get("sub_answers", [])
    expected_units = [(s.get("unit") or "") for s in subs]
    text = ((record.get("attempts") or [{}])[-1]).get("response", "") or ""
    boxes = [b for b in _balanced_boxed(text)] if text else []

    # units for the graded actuals, recovered from the prose
    actuals, units = [], []
    for d in details:
        a = d.get("actual")
        actuals.append(a)
        units.append(unit_for_value(text, a) if isinstance(a, (int, float)) else "")

    # --- A: unit-aware, alignment unchanged.
    # Start from the ENGINE's own per-sub verdict and only try to UPGRADE the subs it
    # failed; never re-derive a pass ourselves, so the re-grade is monotone by
    # construction (it can add credit, never remove it).
    ok_a = True
    for d, a, u, eu in zip(details, actuals, units, expected_units + [""] * len(details)):
        if d.get("passed"):
            continue
        exp = d.get("expected") or []
        upgraded = (a is not None and u and eu
                    and any(_units_reconcile(str(e), eu, a, u, tol) for e in exp))
        if not upgraded:
            ok_a = False
            break

    # --- B: unit-aware + order/subset tolerant (upper bound)
    ok_b = ok_a
    if not ok_b and boxes:
        nums = []
        for b in boxes:
            m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", b.replace(",", ""))
            if m:
                try:
                    v = float(m.group(0))
                except ValueError:
                    continue
                nums.append(v)
        need = [(d.get("expected") or [], eu) for d, eu in
                zip(details, expected_units + [""] * len(details))]
        if nums and len(need) <= len(nums) <= 8:
            for combo in permutations(nums, len(need)):
                if all(_sub_ok_units(exp, eu, v, unit_for_value(text, v), tol)
                       for (exp, eu), v in zip(need, combo)):
                    ok_b = True
                    break
    evidence = {"units_recovered": units, "n_boxes": len(boxes)}
    return orig, ok_a, ok_b, evidence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp-dir", default="experiments/core_direct")
    ap.add_argument("--dataset", default="benchmark/core.json")
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--out", default="docs/results/_direct_unit_regrade.json")
    args = ap.parse_args()

    problems = {p["id"]: p for p in json.load(open(args.dataset))}
    rows, per_problem = [], {}

    for path in sorted(glob.glob(f"{args.exp_dir}/*.run1.json")):
        model = os.path.basename(path).replace(".run1.json", "")
        data = json.load(open(path))
        n = p_orig = p_a = p_b = 0
        recovered = 0
        for rec in data["results"]:
            if rec.get("error"):
                continue
            prob = problems.get(rec["id"])
            if not prob:
                continue
            out = regrade_record(rec, prob, args.tol)
            if out is None:
                continue
            orig, a, b, ev = out
            n += 1
            p_orig += orig
            p_a += a
            p_b += b
            recovered += sum(1 for u in ev["units_recovered"] if u)
            if not orig and a:
                per_problem.setdefault(rec["id"], []).append(model)
        if n:
            rows.append({"model": model, "n": n,
                         "orig": p_orig / n * 100,
                         "unit_aware": p_a / n * 100,
                         "subset_upper": p_b / n * 100,
                         "units_recovered": recovered})

    print(f"{'model':30s} {'n':>4s} {'original':>9s} {'unit-aware':>11s} {'+subset(UB)':>12s}")
    print("-" * 70)
    for r in sorted(rows, key=lambda x: -x["unit_aware"]):
        print(f"{r['model']:30s} {r['n']:4d} {r['orig']:8.1f}% {r['unit_aware']:10.1f}% "
              f"{r['subset_upper']:11.1f}%   (+{r['unit_aware']-r['orig']:.1f} / "
              f"+{r['subset_upper']-r['orig']:.1f})")
    if rows:
        mo = sum(r["orig"] for r in rows) / len(rows)
        ma = sum(r["unit_aware"] for r in rows) / len(rows)
        mb = sum(r["subset_upper"] for r in rows) / len(rows)
        print("-" * 70)
        print(f"{'MEAN':30s}      {mo:8.1f}% {ma:10.1f}% {mb:11.1f}%   "
              f"(+{ma-mo:.1f} / +{mb-mo:.1f})")

    json.dump({"per_model": rows,
               "problems_recovered_by_units": {k: v for k, v in sorted(per_problem.items())}},
              open(args.out, "w"), indent=2, ensure_ascii=False)
    print(f"\nrecovered-by-unit problems: {len(per_problem)}")
    print(f"-> {args.out}   (original experiment files untouched)")


if __name__ == "__main__":
    main()
