"""k>=2 certification of v2 variants: the final backstop.

Every deterministic check has passed; what remains unverifiable by machine is
(a) non-numeric text damage from the rewrite and (b) residual solver
unfaithfulness at the perturbed point. Both manifest the same way: an
independent expert solving the VARIANT TEXT will not reproduce the stored GT.

So: two independent models (GPT-5.4 + Claude/Opus) each blindly write a solver
from the variant text alone. Per-variant verdict:

  PASS_K2          both models reproduce the stored GT (<= tol)
  PASS_K1          exactly one reproduces it; the other failed/disagreed alone
  FAIL_BOTH_AGREE  the two models agree with each other but NOT with the GT
                   -> strong evidence the variant (text or GT) is wrong: REMOVE
  REVIEW           neither matches and they disagree with each other
                   -> the problem may just be hard for models; expert queue

Resume-safe: streams results; reruns only missing variant ids.

Usage:
    uv run python -m pipeline.k2_certify --input pipeline/reports/variants_v2_full.json \
        --out pipeline/reports/k2_variants.json --workers 8
"""

import json
import os
import re
import time
import tomllib
import argparse
import threading
import concurrent.futures
from collections import Counter

import anthropic
from openai import OpenAI

from eval.engine import run_solver, compare_values

CFG = tomllib.load(open("models.toml", "rb"))
GPT = CFG["gpt55-reasoning"]
CL = CFG["opus48"]

PROMPT = """You are an expert atmospheric scientist. Solve this problem by writing a Python
solve() function that implements the real physics/formulas (do NOT guess or
hard-code an answer). Standard library only. Do unit conversions explicitly.
Return a dict: sub-part id (str) -> {{"value": <number>, "unit": "<unit>"}}.

## Problem
{problem}

Output ONLY the Python code for solve()."""


def _extract(t):
    m = re.search(r"```(?:python)?\s*\n(.*?)```", t, re.DOTALL)
    return (m.group(1) if m else t).strip()


def _vals(res):
    out = []
    for v in res.values():
        x = v.get("value") if isinstance(v, dict) else v
        try:
            out.append(float(x))
        except (ValueError, TypeError):
            pass
    return out


def gpt_solve(client, problem):
    for a in range(2):
        try:
            r = client.chat.completions.create(
                model=GPT["model_id"],
                messages=[{"role": "user", "content": PROMPT.format(problem=problem)}],
                max_completion_tokens=8000)
            ok, res, _ = run_solver(_extract(r.choices[0].message.content or ""))
            return _vals(res) if ok else None
        except Exception:
            if a < 1:
                time.sleep(4)
    return None


def claude_solve(client, problem):
    for a in range(2):
        try:
            msg = client.messages.create(
                model=CL["model_id"], max_tokens=6000,
                messages=[{"role": "user", "content": PROMPT.format(problem=problem)}])
            ok, res, _ = run_solver(_extract(msg.content[0].text))
            return _vals(res) if ok else None
        except Exception:
            if a < 1:
                time.sleep(4)
    return None


def covers(model_vals, stored, tol):
    """A model "covers" the GT iff EVERY stored sub-answer is matched by some
    model value (order-agnostic). Extra model values are ignored — a model that
    also reports an intermediate (e.g. echoes a given mass) has still reproduced
    the answer; a model that omits a sub-answer leaves it unmatched and so fails.
    """
    if not model_vals or not stored:
        return False
    return all(any(compare_values(str(s), m, tol) for m in model_vals) for s in stored)


def certify(v, tol):
    stored = []
    for s in v["sub_answers"]:
        try:
            stored.append(float(s["value"]))
        except (ValueError, TypeError):
            pass
    gc = OpenAI(api_key=GPT["api_key"], base_url=GPT["base_url"], timeout=120)
    cc = anthropic.Anthropic(api_key=CL["api_key"], base_url=CL["base_url"], timeout=120)
    g = gpt_solve(gc, v["problem"])
    c = claude_solve(cc, v["problem"])
    g_ok = covers(g, stored, tol)
    c_ok = covers(c, stored, tol)
    if g_ok and c_ok:
        verdict = "PASS_K2"
    elif g_ok or c_ok:
        verdict = "PASS_K1"
    elif g and c and covers(g, c, tol) and covers(c, g, tol):
        verdict = "FAIL_BOTH_AGREE"
    else:
        verdict = "REVIEW"
    return {"id": v["id"], "parent_id": v["parent_id"], "verdict": verdict,
            "stored": stored, "gpt": g, "claude": c}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="pipeline/reports/variants_v2_full.json")
    ap.add_argument("--out", default="pipeline/reports/k2_variants.json")
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--ids", nargs="+", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    variants = json.load(open(args.input))
    if args.ids:
        variants = [v for v in variants if v["id"] in set(args.ids)]
    done = []
    if os.path.exists(args.out):
        done = json.load(open(args.out))
    done_ids = {r["id"] for r in done}
    todo = [v for v in variants if v["id"] not in done_ids]
    if args.limit:
        todo = todo[:args.limit]
    print(f"variants: {len(variants)} | done: {len(done_ids)} | todo: {len(todo)}")

    lock = threading.Lock()
    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(certify, v, args.tol): v["id"] for v in todo}
        for f in concurrent.futures.as_completed(futs):
            try:
                rec = f.result()
            except Exception as e:
                rec = {"id": futs[f], "verdict": "ERROR", "note": str(e)[:80]}
            with lock:
                done.append(rec)
                n += 1
                if n % 25 == 0:
                    json.dump(done, open(args.out, "w"), indent=1)
                    print(f"  {n}/{len(todo)} {dict(Counter(r['verdict'] for r in done))}", flush=True)

    json.dump(done, open(args.out, "w"), indent=1)
    print("\n=== verdicts ===", dict(Counter(r["verdict"] for r in done)))
    print("FAIL_BOTH_AGREE:", [r["id"] for r in done if r["verdict"] == "FAIL_BOTH_AGREE"][:30])
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
