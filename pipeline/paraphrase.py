"""Paraphrase layer over variants_numeric.json — same parameters, reworded text.

Each variant already carries perturbed parameters + a faithful solver + a
k2-verified answer. Here we rewrite only its ``problem`` text (phrasing,
structure, framing) while keeping every number/unit, the asked quantity, and the
answer identical. The result tests *expression robustness* on top of the
contamination resistance the variant already provides.

Fidelity is enforced the same way variants are: the rewrite is rejected unless
(1) every perturbed parameter value still appears verbatim in the new text and
(2) the text actually changed enough (token edit ratio). Semantic preservation
is then certified separately by re-running pipeline.k2_certify on the output:
two independent models must reproduce the (unchanged) stored answer.

Usage:
    uv run python -m pipeline.paraphrase --limit 6 --out pipeline/reports/paraphrase_pilot.json
    uv run python -m pipeline.paraphrase --out benchmark/variants_paraphrased.json --workers 8
"""

import os
import json
import difflib
import argparse
import threading
import concurrent.futures
from collections import Counter

from eval.models import load_config, build_model
from .type_params import appears_in_text, strip_labels
from .certify_gt import extract_numbers

PROMPT = """You are rewriting an atmospheric-science exam problem to test whether a solver
is robust to *how a question is phrased*. Produce a paraphrase that a human
instructor would accept as the SAME problem.

MUST change (make it clearly reworded, not a synonym swap):
- sentence structure and phrasing; reorder the given quantities;
- the framing — e.g. turn an inline "Given: ..." list into flowing prose, or
  prose into a list; vary the narration ("a weather station reports" ->
  "an automatic sensor records").

MUST NOT change (these define the problem):
- any numeric value or its unit — copy every number exactly as written;
- the physical scenario, the quantity being asked, or the requested output unit;
- do not add, drop, or invent any information or number.

## Original problem
{problem}

Output ONLY the rewritten problem text (no preamble, no code)."""


def edit_ratio(a: str, b: str) -> float:
    """1 - similarity over tokens; higher = more reworded."""
    return 1.0 - difflib.SequenceMatcher(None, a.split(), b.split()).ratio()


def numbers_preserved(variant: dict, new_text: str) -> bool:
    """Every perturbed parameter's MAGNITUDE must still be extractable from the text.

    We check ``abs(value)`` and skip zeros: sign is carried by wording ("loses",
    "−", "from rest") and a 0 has no magnitude to drop. Semantic preservation of
    sign/zero is the job of the downstream k>=2 gate (a flipped sign yields the
    wrong-signed answer and fails certification), so this gate only guards that
    the numeric magnitudes survived the rewrite.
    """
    # Compare by MAGNITUDE on both sides: the param value is abs'd, so the text
    # numbers must be too — otherwise a negative perturbed value (e.g. F* = -737)
    # is extracted signed and never matches its abs, wrongly failing the gate.
    tnums = [abs(t) for t in (extract_numbers(strip_labels(new_text)) or []) if t is not None]
    for v in variant.get("parameters", {}).values():
        fv = float(v)
        if fv != 0 and not appears_in_text(abs(fv), tnums):
            return False
    return True


def paraphrase_one(model, variant: dict, min_edit: float, attempts: int = 3) -> dict | None:
    """Return a record identical to the variant but with reworded text, or None
    if no attempt passed the fidelity gates. Generation is stochastic, so a few
    retries recover most rewrites that dropped a number or stayed too literal."""
    original = variant["problem"]
    for _ in range(attempts):
        try:
            new_text = model.generate(PROMPT.format(problem=original)).text.strip()
        except Exception:
            continue
        if len(new_text) < 30 or not numbers_preserved(variant, new_text):
            continue
        er = edit_ratio(original, new_text)
        if er < min_edit:  # too close to the original to test anything
            continue
        rec = dict(variant)  # same id/parent/params/code/sub_answers
        rec["problem"] = new_text
        rec["paraphrase"] = {"edit_ratio": round(er, 3)}
        rec.pop("k2", None)  # the paraphrased text must be re-certified by k2_certify
        return rec
    return None


def main():
    ap = argparse.ArgumentParser(description="paraphrase variants_numeric.json (params fixed, text reworded)")
    ap.add_argument("--input", default="benchmark/variants_numeric.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="opus48", help="rewriter model from models.toml")
    ap.add_argument("--ids", nargs="+", default=None, help="only these variant ids")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--min-edit", type=float, default=0.25, help="min token edit ratio to keep")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    variants = json.load(open(args.input))
    if args.ids:
        variants = [v for v in variants if v["id"] in set(args.ids)]
    if args.limit:
        variants = variants[:args.limit]

    # resume: keep already-paraphrased ids, skip them
    out = json.load(open(args.out)) if os.path.exists(args.out) else []
    done = {r["id"] for r in out}
    todo = [v for v in variants if v["id"] not in done]
    print(f"variants: {len(variants)} | resume-done: {len(done)} | todo: {len(todo)}")

    model = build_model(load_config(args.model))
    reject = Counter()
    lock = threading.Lock()
    n = 0

    def work(v):
        nonlocal n
        rec = paraphrase_one(model, v, args.min_edit)
        with lock:
            if rec:
                out.append(rec)
            else:
                reject[v["parent_id"]] += 1
            n += 1
            if n % 50 == 0:  # checkpoint
                json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)
                print(f"  {n}/{len(todo)} ({len(out)} kept)", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))

    json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)
    print(f"paraphrased {len(out)}/{len(variants)} total | rejected this run {sum(reject.values())}")
    print(f"wrote {args.out}  (next: certify with pipeline.k2_certify --input {args.out})")


if __name__ == "__main__":
    main()
