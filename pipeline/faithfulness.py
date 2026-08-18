"""V1-deterministic: audit base-solver FAITHFULNESS without any LLM.

A variant's ground truth is correct-by-construction iff the base solver is a
faithful function of its declared inputs. This script flags solvers that are
likely NOT faithful, using three deterministic signals + an extensible
physical-invariant (monotonicity) framework:

  (S) sensitivity   – perturb each input; an input that changes NO output is
                      "dead" (declared but ignored -> possibly hardcoded result).
  (F) fragility     – an input whose perturbation throws (log<0, /0, domain err)
                      means variants in that direction are ill-posed.
  (M) magic literal – a numeric constant in the body that is NOT a universal
                      constant, unit conversion, small int, or a param default.
                      This is the signature of a hardcoded parameter-dependent
                      quantity (e.g. 1.2 hard-coded e_s=611 = e_s(T_base)).
  (I) invariants    – per-topic monotonicity/sign relations checked over a sweep
                      (registry below; extensible). Catches sign/direction bugs
                      like 1.2 (vapor density must rise with temperature).

Usage:
    uv run python -m pipeline.faithfulness
    uv run python -m pipeline.faithfulness --id 1.2
"""

import json
import ast
import math
import argparse
from collections import defaultdict

from eval.engine import run_solver


# values that legitimately appear hardcoded: universal constants + unit conversions
UNIVERSAL = [
    math.pi, math.e, 9.8, 9.81, 287.0, 287.05, 8.314, 8.314462618, 461.5, 461.0,
    5.67e-8, 5.670e-8, 1.381e-23, 1.38e-23, 6.022e23, 6.02214e23, 2.5e6, 2.83e6,
    1004.0, 1005.0, 1850.0, 1846.0, 717.0, 2.998e8, 3.0e8, 6.674e-11, 0.622, 0.286,
    273.15, 273.0, 6.11, 611.0,  # 611 IS es(273): keep OUT so 1.2-style is caught
    # solar constant
    1361.0, 1366.0, 1367.0, 1370.0, 1376.0, 1360.0,
    # Earth radius (m) / mass (kg) / surface area / g0
    6.371e6, 6371000.0, 6.37e6, 6.378e6, 6378000.0, 6.4e6, 5.97e24, 5.972e24,
    # Earth angular velocity (rad/s) and 2*Omega
    7.292e-5, 7.29e-5, 1.458e-4, 1.4584e-4,
    # molar masses g/mol and kg/mol (water, air, CO2, O2, N2, O3, ozone)
    18.015, 18.0, 18.02, 28.97, 29.0, 28.0, 44.0, 44.01, 32.0, 48.0, 16.0,
    0.018, 0.018015, 0.029, 0.02897, 0.028, 0.044, 0.04401, 0.032, 0.048, 0.016,
    # latent heats (vaporization, sublimation, fusion) J/kg
    2.45e6, 2.50e6, 2.501e6, 2.834e6, 3.34e5, 3.337e5,
    # seconds per year / day, astronomical unit (m), solar luminosity (W)
    3.156e7, 3.1536e7, 31536000.0, 86400.0, 1.496e11, 3.8e26, 3.828e26,
    # misc standard: std gravity, gas const variants, Wien, Planck, electron charge
    9.80665, 8.31446, 2.898e-3, 6.626e-34, 1.602e-19, 1.0e-7,
    6371.0, 6378.0, 6.4e3, 71.6, 0.25, 0.35, 0.21,  # Earth radius (km), radar/empirical coeffs
]
UNIVERSAL.remove(611.0)  # intentionally NOT explained: hardcoded es is the bug we hunt
UNIT_CONV = {1.0, 10.0, 100.0, 1000.0, 60.0, 3600.0, 24.0, 12.0, 365.0, 0.5,
             1e3, 1e6, 1e9, 1e12, 1e-3, 1e-6, 1e-9, 1e-2, 0.01, 0.001, 3.6, 86400.0,
             180.0, 360.0, 1013.0, 1013.25, 101325.0, 1e5, 1e-5, 1e4, 1e-4, 1e-12,
             2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 1.5, 2.5}


def base_defaults_and_literals(code: str):
    """Return (param_defaults dict, body_literals list[float])."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}, []
    defaults, literals, default_nodes = {}, [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "solve":
            args = node.args.args
            defs = node.args.defaults
            for a, d in zip(args[len(args) - len(defs):], defs):
                try:
                    defaults[a.arg] = ast.literal_eval(d)
                except (ValueError, SyntaxError):
                    pass
                default_nodes.add(id(d))
    # numeric literals in the body (exclude the signature defaults)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool) and id(node) not in default_nodes:
            literals.append(float(node.value))
    return defaults, literals


def is_explained(x: float, defaults: dict) -> bool:
    a = abs(x)
    if a == 0 or a == 1:
        return True
    if a == int(a) and a <= 12:               # small ints
        return True
    if a in UNIT_CONV:
        return True
    for u in list(UNIT_CONV) + UNIVERSAL:
        if u and abs(a - abs(u)) / abs(u) <= 0.01:
            return True
    for dv in defaults.values():              # equals a declared parameter value
        if isinstance(dv, (int, float)) and dv and abs(a - abs(dv)) / abs(dv) <= 0.01:
            return True
    return False


def call(code: str, kwargs: dict):
    ns = {}
    exec(code, ns)
    return ns["solve"](**kwargs)


def out_vals(res: dict):
    out = []
    for v in res.values():
        x = v.get("value") if isinstance(v, dict) else v
        try:
            out.append(float(x))
        except (ValueError, TypeError):
            out.append(None)
    return out


def sensitivity(code: str, defaults: dict):
    """Return (dead_inputs, fragile_inputs)."""
    ok, base_res, _ = run_solver(code)
    if not ok:
        return [], []
    base = out_vals(base_res)
    dead, fragile = [], []
    for p, v in defaults.items():
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        delta = v * 1.05 if v != 0 else 0.05
        changed = False
        for d in (delta, (v * 0.95 if v != 0 else -0.05)):
            kw = dict(defaults); kw[p] = d
            try:
                res = out_vals(call(code, kw))
            except Exception:
                fragile.append(p)
                changed = True
                break
            for a, b in zip(base, res):
                if a is None or b is None:
                    continue
                if abs(a - b) > 1e-9 * max(abs(a), 1e-9):
                    changed = True
        if not changed and p not in fragile:
            dead.append(p)
    return dead, sorted(set(fragile))


# ── (I) physical-invariant registry: monotonic relations the answer MUST obey ──
# each rule: applies-if(problem) -> (param, direction, output_index_or_None)
# direction: +1 output increases with param, -1 decreases. Checked over a sweep.
INVARIANTS = [
    # saturation vapour density / pressure must INCREASE with temperature
    {"need": ["saturation", "vapor"], "param_like": ["t"], "sign": +1,
     "desc": "saturation vapour increases with T (Clausius-Clapeyron)"},
]


def check_invariants(problem: dict, code: str, defaults: dict):
    txt = (problem.get("problem", "") + " " + " ".join(problem.get("knowledge_points", []))).lower()
    viol = []
    for rule in INVARIANTS:
        if not all(w in txt for w in rule["need"]):
            continue
        params = [p for p in defaults if any(pl == p.lower()[:len(pl)] for pl in rule["param_like"])
                  and isinstance(defaults[p], (int, float))]
        for p in params:
            xs = []
            base_v = defaults[p]
            for f in (0.9, 0.95, 1.0, 1.05, 1.1):
                kw = dict(defaults); kw[p] = base_v * f
                try:
                    ys = out_vals(call(code, kw))
                except Exception:
                    ys = []
                xs.append((base_v * f, ys[0] if ys else None))
            seq = [y for _, y in xs if y is not None]
            if len(seq) >= 3:
                incr = all(b >= a - 1e-12 for a, b in zip(seq, seq[1:]))
                decr = all(b <= a + 1e-12 for a, b in zip(seq, seq[1:]))
                good = incr if rule["sign"] > 0 else decr
                if not good:
                    viol.append(f"{p}: {rule['desc']} VIOLATED (seq={[round(s,3) for s in seq]})")
    return viol


def main():
    ap = argparse.ArgumentParser(description="deterministic solver-faithfulness audit")
    ap.add_argument("--input", default="pipeline/reports/problems_final.json")
    ap.add_argument("--id", default=None)
    ap.add_argument("--out", default="pipeline/reports/solver_faithfulness_audit.json")
    args = ap.parse_args()

    problems = json.load(open(args.input))
    if args.id:
        problems = [p for p in problems if p["id"] == args.id]

    records = []
    for p in problems:
        defaults, literals = base_defaults_and_literals(p["code"])
        dead, fragile = sensitivity(p["code"], defaults)
        magic = sorted({round(x, 6) for x in literals if not is_explained(x, defaults)})
        inv = check_invariants(p, p["code"], defaults)
        risk = []
        if dead:
            risk.append("DEAD_INPUT")
        if magic:
            risk.append("MAGIC_LITERAL")
        if inv:
            risk.append("INVARIANT_VIOLATION")
        if fragile:
            risk.append("FRAGILE")
        records.append({"id": p["id"], "book": p.get("book", ""), "risk": risk,
                        "dead_inputs": dead, "fragile_inputs": fragile,
                        "magic_literals": magic, "invariant_violations": inv})

    json.dump(records, open(args.out, "w"), indent=2, ensure_ascii=False)
    flagged = [r for r in records if r["risk"]]
    by = defaultdict(int)
    for r in records:
        for x in r["risk"]:
            by[x] += 1
    print(f"audited {len(records)} solvers | flagged {len(flagged)}")
    print("by signal:", dict(by))
    print("\n=== INVARIANT_VIOLATION (highest priority — wrong physical direction) ===")
    for r in records:
        if "INVARIANT_VIOLATION" in r["risk"]:
            print(f"  {r['id']:8s} {r['invariant_violations']}")
    print("\n=== DEAD_INPUT (declared input ignored by solver) ===")
    for r in records:
        if "DEAD_INPUT" in r["risk"]:
            print(f"  {r['id']:8s} dead={r['dead_inputs']}")
    print("\n=== MAGIC_LITERAL (top 25; hardcoded value not explained) ===")
    ml = [r for r in records if "MAGIC_LITERAL" in r["risk"]]
    print(f"  total: {len(ml)}")
    for r in ml[:25]:
        print(f"  {r['id']:8s} {r['magic_literals']}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
