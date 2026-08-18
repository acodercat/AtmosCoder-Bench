"""Variant generation v2 — layered, machine-verifiable safety gates.

Built on the v1 machinery (perturbation, constraint pairs, LLM text rewrite,
count-based text validation) plus four structural fixes motivated by audited
failure modes of v1:

  G1 TEXT-BOUND WHITELIST  only parameters typed INPUT_TEXT in
     pipeline/reports/param_types.json may be perturbed (run pipeline.type_params
     first). Physical constants are additionally gone from solve() signatures
     entirely (pipeline.demote_constants), so they cannot be perturbed even by a
     bug. INPUT_HIDDEN params are frozen: perturbing them would change the GT
     while the problem text stays the same.
  G2 VERIFIED CODE REWRITE  v1 edited defaults via str.replace, which fails
     SILENTLY on formatting mismatches ("T = 256", 2.5e6 vs 2500000.0), leaving
     base GT under a perturbed text. v2 rebuilds the signature and then VERIFIES
     by AST that every default equals the intended value; mismatch -> drop.
  G3 CONDITION GATE  at the variant point, bump each perturbed param by +0.5%
     and measure output amplification. amp > --max-amp (default 25) means the
     output lives on a near-cancellation (the air_225 class) -> reject variant.
     (Legitimate sharp physics like Clausius-Clapeyron has amp ~19, kept.)
     Also require >=1 output to move >=1% vs base (else the variant cannot
     distinguish memorization from solving).
  G4 HARD TEXT CONSISTENCY  in addition to v1's count-decrease check, every
     perturbed NEW value must be extractable from the rewritten text (allowing
     the standard unit transforms incl. degC<->K). No silent text/param skew.

Record format is identical to the v1 numeric-variants format (+ a "gates" field).

Usage:
    uv run python -m pipeline.variants --ids 2.3 air_75 --n 3 \
        --output pipeline/reports/variants_v2_pilot.json
    uv run python -m pipeline.variants --all --n 10 --output benchmark/variants_numeric.json
"""

import os
import json
import ast
import re
import random
import argparse
import threading
import concurrent.futures
from collections import Counter

from eval.engine import run_solver
from .perturb import (
    make_client, parse_solve_params, classify_params, perturb_value, get_bounds,
    detect_constraint_pairs, enforce_constraints, rewrite_problem_with_llm,
    text_validation, _stringify_for_match,
)
from .type_params import appears_in_text, strip_labels
from .certify_gt import extract_numbers


# ── G2: verified signature rewrite ──────────────────────────────────────────

def _sig_span(code: str):
    """(start, end_of_close_paren) of the solve() signature, comment-aware."""
    i = code.find("def solve(")
    if i < 0:
        raise ValueError("no def solve(")
    j = i + len("def solve(")
    depth, k = 1, j
    while depth:
        ch = code[k]
        if ch == "#":
            k = code.index("\n", k)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        k += 1
    return i, j, k  # 'def solve(' at i, inner = code[j:k-1]


def set_defaults(code: str, new_params: dict) -> str:
    """Rebuild the signature with new defaults, then AST-verify exact equality."""
    i, j, k = _sig_span(code)
    inner = re.sub(r"#[^\n]*", "", code[j:k - 1]).replace("\n", " ")
    parts, depth, cur = [], 0, ""
    for ch in inner:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)

    rebuilt = []
    for part in parts:
        if "=" not in part:
            rebuilt.append(part.strip()); continue
        name = part.split("=", 1)[0].strip().split(":")[0].strip()
        if name in new_params:
            rebuilt.append(f"{name}={new_params[name]!r}")
        else:
            rebuilt.append(part.strip())
    new_code = code[:i] + "def solve(" + ", ".join(rebuilt) + code[k - 1:]

    # verify: parse and compare every default we set
    fn = next(n for n in ast.walk(ast.parse(new_code))
              if isinstance(n, ast.FunctionDef) and n.name == "solve")
    args, defs = fn.args.args, fn.args.defaults
    got = {}
    for a, d in zip(args[len(args) - len(defs):], defs):
        try:
            got[a.arg] = ast.literal_eval(d)
        except (ValueError, SyntaxError):
            pass
    for name, want in new_params.items():
        if name not in got or got[name] != want:
            raise ValueError(f"default verify failed for {name}: {got.get(name)} != {want}")
    return new_code


def mineru_numbers(text: str):
    """Extra number candidates from $...$ math spans with MinerU's spaced-digit
    artifact ('$4 , 4 7 1 km$') collapsed. Append-only: cannot corrupt normal parsing."""
    out = []
    for m in re.finditer(r"\$[^$]{0,160}?\$", text):
        collapsed = re.sub(r"(?<=\d)[\s,]+(?=\d)", "", m.group(0))
        try:
            out += extract_numbers(collapsed) or []
        except Exception:
            pass
    return out


# ── G3: condition / responsiveness gate ─────────────────────────────────────

def _out_floats(res: dict):
    out = {}
    for kk, v in res.items():
        x = v.get("value") if isinstance(v, dict) else v
        try:
            out[kk] = float(x)
        except (ValueError, TypeError):
            pass
    return out


def condition_gate(code: str, all_defaults: dict, perturbed: list, max_amp: float):
    """Return (ok, amp). Local amplification at the variant point."""
    ok, res, _ = run_solver(code)
    if not ok:
        return False, None
    base = _out_floats(res)
    if not base:
        return False, None
    worst = 0.0
    ns = {}
    exec(code, ns)
    for name in perturbed:
        v = all_defaults[name]
        if not isinstance(v, (int, float)) or v == 0:
            continue
        kw = dict(all_defaults); kw[name] = v * 1.005
        try:
            r2 = _out_floats(ns["solve"](**kw))
        except Exception:
            return False, None
        for kk, b in base.items():
            if kk in r2 and b != 0:
                amp = abs(r2[kk] - b) / abs(b) / 0.005
                worst = max(worst, amp)
    return worst <= max_amp, round(worst, 1)


# ── per-problem generation ──────────────────────────────────────────────────

def gen_for_problem(solver, types, n_variants, base_seed, client, model_cfg,
                    max_amp, reject_log, start_variant=0):
    pid = solver["id"]
    code = solver["code"]
    ptypes = types.get(pid, {})
    all_params = parse_solve_params(code)
    if not all_params:
        reject_log["no_params"] += 1
        return []
    defaults = {p["name"]: p["default"] for p in all_params}

    # G1: v1 heuristics AND typed INPUT_TEXT
    heur, skipped = classify_params(all_params)
    # value-aware un-skip: v1's "M_*" name pattern also fires on Stull's wind-speed
    # notation (M_O = observed wind). Only freeze as molar mass if the VALUE is one.
    MOLAR = (1.008, 2.016, 4.0, 12.0, 14.0, 16.0, 18.015, 28.0, 28.97, 29.0,
             30.0, 32.0, 40.0, 44.01, 46.0, 48.0, 61.0, 64.0, 98.0)
    def _is_molar_value(v):
        av = abs(v)
        return any(abs(av - m) / m <= 0.02 or (av > 0 and abs(av * 1000 - m) / m <= 0.02)
                   for m in MOLAR)
    rescued = [n for n, why in skipped
               if why == "molecular/atomic weight" and not _is_molar_value(defaults.get(n, 0) or 0)]
    if rescued:
        heur = heur + [{"name": n, "default": defaults[n]} for n in rescued]
        skipped = [(n, w) for n, w in skipped if n not in rescued]
    perturbable = [p for p in heur if ptypes.get(p["name"], {}).get("type") == "INPUT_TEXT"]
    frozen = [(p["name"], "not INPUT_TEXT") for p in heur
              if ptypes.get(p["name"], {}).get("type") != "INPUT_TEXT"] + skipped
    if not perturbable:
        reject_log["no_perturbable"] += 1
        return []
    perturbed_names = {p["name"] for p in perturbable}
    constraint_pairs = detect_constraint_pairs(perturbable)

    ok0, res0, _ = run_solver(code)
    if not ok0:
        reject_log["base_exec"] += 1
        return []
    base_out = _out_floats(res0)
    # anti-memorization reference: the PARENT'S STORED (graded) answers
    stored = {}
    for s in solver.get("sub_answers", []):
        try:
            stored[s["sub"]] = float(s["value"])
        except (ValueError, TypeError, KeyError):
            pass

    variants, attempt = [], 0
    max_attempts = max(n_variants * 9, 40)  # floor so small top-ups still get a fair budget
    while len(variants) < n_variants and attempt < max_attempts:
        rng = random.Random(base_seed + 7919 * start_variant + attempt)
        attempt += 1
        # adaptive ladder: insensitive physics (4th roots etc.) needs a larger
        # input perturbation to move the answer past the grading tolerance
        factor = 0.25 if attempt <= max_attempts / 3 else \
                 (0.4 if attempt <= 2 * max_attempts / 3 else 0.5)
        new_params = dict(defaults)
        ok = True
        for p in perturbable:
            bounds = get_bounds(p["name"])
            if bounds is not None:
                lo, hi = bounds
                if not (lo < p["default"] < hi):
                    bounds = None
            if bounds is None and 0.0 < p["default"] < 1.0:
                # fraction-safe: a default strictly inside (0,1) stays inside (0,1).
                # Required for fractions/albedos/absorptivities (must not cross 1);
                # for genuinely dimensional small values this only narrows the range.
                bounds = (0.0, 1.0)
            nv = perturb_value(p["default"], rng, factor=factor, bounds=bounds)
            if nv is None:
                ok = False; break
            if abs(nv) >= 1e5 or 0 < abs(nv) < 1e-3:
                nv = float(f"{nv:.4g}")  # keep text-friendly significant figures
            new_params[p["name"]] = nv
        # identical given values are textually ambiguous (two params both '6e-10'):
        # the rewriter cannot tell which occurrence belongs to which parameter, so
        # freeze ALL params sharing a duplicated default — perturb none of them
        dup_defaults = {d for d, c in Counter(p["default"] for p in perturbable).items() if c > 1}
        for p in perturbable:
            if p["default"] in dup_defaults:
                new_params[p["name"]] = p["default"]
        if not ok or not enforce_constraints(new_params, constraint_pairs):
            reject_log["perturb/constraint"] += 1
            continue

        # G2: verified rewrite of defaults
        try:
            mod_code = set_defaults(code, {k: v for k, v in new_params.items()
                                           if k in perturbed_names})
        except ValueError:
            reject_log["G2_sig_verify"] += 1
            continue

        okx, res, _ = run_solver(mod_code)
        if not okx or not res:
            reject_log["variant_exec"] += 1
            continue
        out = _out_floats(res)
        # finite + 10x cap (v1)
        bad = False
        for kk, f in out.items():
            if not (-1e30 < f < 1e30):
                bad = True; break
            b = base_out.get(kk)
            if b is not None and b != 0 and abs(f / b) > 10:
                bad = True; break
        if bad:
            reject_log["finite/10x"] += 1
            continue
        if any(f == 0 for f in out.values()):
            # a zero answer cannot be graded under relative tolerance
            reject_log["G3_zero_gt"] += 1
            continue
        # G3b anti-memorization: >=1 sub-answer must move past the 5% grading
        # tolerance (with margin) RELATIVE TO THE PARENT'S STORED ANSWER —
        # otherwise a model that memorized the base answer passes this variant.
        moved = max((abs(out[k] - stored[k]) / abs(stored[k])
                     for k in out if k in stored and stored[k] != 0), default=0.0)
        if moved <= 0.06:
            reject_log["G3_memo_transparent"] += 1
            continue

        # G3: condition gate at the variant point
        cond_ok, amp = condition_gate(mod_code, new_params, sorted(perturbed_names), max_amp)
        if not cond_ok:
            reject_log["G3_ill_conditioned"] += 1
            continue

        # text rewrite + G4 validations
        new_problem = rewrite_problem_with_llm(
            solver["problem"], all_params, new_params, perturbed_names, client, model_cfg)
        changes = [p for p in perturbable if new_params[p["name"]] != p["default"]]
        if changes and new_problem.strip() == solver["problem"].strip():
            reject_log["G4_rewrite_failed"] += 1
            continue
        okt, _why = text_validation(new_problem, all_params, new_params, perturbed_names,
                                    orig_text=solver["problem"])
        if not okt:
            # the count check only applies when the old value literally appears in the
            # original text; with a unit transform (param 1e-6 m, text "1 um") it can
            # only misfire. In that case rely on the transform-aware checks below
            # (+ the k>=2 gate downstream).
            literal_applies = any(
                s in solver["problem"]
                for p in changes for s in _stringify_for_match(p["default"]))
            if literal_applies:
                reject_log["G4_count_check"] += 1
                continue
        tnums = (extract_numbers(strip_labels(new_problem)) or []) \
            + mineru_numbers(strip_labels(new_problem))
        # EVERY perturbable param's CURRENT value (new if changed, default if not)
        # must be in the rewritten text — also catches the rewriter touching a
        # value whose parameter stayed at its default (text/param skew).
        if not all(appears_in_text(float(new_params[p["name"]]), tnums) for p in perturbable):
            reject_log["G4_value_not_in_text"] += 1
            continue

        vi = start_variant + len(variants) + 1
        variants.append({
            "id": f"{pid}_v{vi}", "parent_id": pid, "variant": vi,
            "book": solver.get("book", ""), "problem": new_problem, "code": mod_code,
            "sub_answers": [{"sub": kk,
                             "value": str(v.get("value", "") if isinstance(v, dict) else v),
                             "unit": (v.get("unit", "") if isinstance(v, dict) else "")}
                            for kk, v in res.items()],
            "parameters": {k: v for k, v in new_params.items() if k in perturbed_names},
            "skipped_params": [n for n, _ in frozen],
            "gates": {"amp": amp, "max_out_change": round(moved, 4)},
        })
    if len(variants) < n_variants:
        reject_log[f"short:{pid}"] = n_variants - len(variants)
    return variants


def main():
    ap = argparse.ArgumentParser(description="variant generation v2 (gated)")
    ap.add_argument("--input", default="pipeline/reports/problems_final.json")
    ap.add_argument("--types", default="pipeline/reports/param_types.json")
    ap.add_argument("--output", required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--ids", nargs="+", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--model", default="gemini")
    ap.add_argument("--max-amp", type=float, default=25.0)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--topup", action="store_true",
                    help="fill parents that have fewer than --n variants in the output")
    args = ap.parse_args()

    import tomllib
    model_cfg = tomllib.load(open("models.toml", "rb"))[args.model]
    problems = json.load(open(args.input))
    types = json.load(open(args.types))
    # variants get full-precision GT: use de-rounded solver twins where available
    # (base stored answers stay textbook-aligned; see pipeline.deround)
    try:
        _dr = json.load(open("pipeline/reports/derounded_solvers.json"))
        for p in problems:
            p["code"] = _dr.get(p["id"], p["code"])
    except FileNotFoundError:
        pass
    if args.ids:
        problems = [p for p in problems if p["id"] in set(args.ids)]
    elif not args.all:
        raise SystemExit("pass --ids ... or --all")

    done = []
    if os.path.exists(args.output):
        done = json.load(open(args.output))
    counts = Counter(v["parent_id"] for v in done)
    maxidx = {}
    for v in done:
        maxidx[v["parent_id"]] = max(maxidx.get(v["parent_id"], 0), v.get("variant", 0))
    if args.topup:
        todo = [(p, args.n - counts.get(p["id"], 0), maxidx.get(p["id"], 0))
                for p in problems if counts.get(p["id"], 0) < args.n]
    else:
        todo = [(p, args.n, 0) for p in problems if p["id"] not in counts]
    print(f"problems: {len(problems)} | resume-done: {len(counts)} | todo: {len(todo)}")

    reject_log = Counter()
    lock = threading.Lock()

    def work(item):
        p, k, start = item
        client = make_client(model_cfg)
        return gen_for_problem(p, types, k, args.seed, client, model_cfg,
                               args.max_amp, reject_log, start_variant=start)

    n_done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, t): t[0]["id"] for t in todo}
        for f in concurrent.futures.as_completed(futs):
            try:
                vs = f.result()
            except Exception as e:
                with lock:
                    reject_log[f"ERROR:{futs[f]}"] = 1
                print(f"  ERROR {futs[f]}: {e}", flush=True)
                vs = []
            with lock:
                done.extend(vs)
                n_done += 1
                if n_done % 10 == 0:
                    json.dump(done, open(args.output, "w"), indent=1, ensure_ascii=False)
                    print(f"  {n_done}/{len(todo)} ({len(done)} variants)", flush=True)

    json.dump(done, open(args.output, "w"), indent=1, ensure_ascii=False)
    print(f"\nwrote {len(done)} variants -> {args.output}")
    print("gate rejections:", dict(reject_log))


if __name__ == "__main__":
    main()
