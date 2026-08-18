"""Certify paraphrases by SEMANTIC EQUIVALENCE, not by solving.

k2_certify asks two models to SOLVE the text and reproduce the stored answer.
That is right for variants of solvable problems, but wrong for paraphrases of the
HARD (base-only) tier: those problems are selected because frontier models fail
them, so a solve-based gate rejects faithful paraphrases for the wrong reason.

A paraphrase only rewords; its numbers/answer/solver are inherited unchanged. So
the thing to certify is: does the reworded text describe EXACTLY the same problem
as the original? Two independent models (opus48 + gpt55-reasoning) judge equivalence; a
paraphrase is kept only if BOTH say YES. No solving required.

    uv run python -m pipeline.certify_paraphrase \
        --input pipeline/reports/paraphrased_baseonly.json \
        --base benchmark/base.json \
        --out pipeline/reports/equiv_baseonly.json
"""

import re
import json
import argparse
import concurrent.futures

from eval.models import load_config, build_model, ModelError

JUDGES = ("opus48", "gpt55-reasoning")

PROMPT = """Two versions of an atmospheric-science problem are given below. Decide whether they
are the SAME problem — i.e. a correct solution to one is necessarily a correct
solution to the other.

They are the SAME only if ALL hold:
- every given numeric value and its unit is present and identical in both
  (wording/notation may differ, e.g. "1.61 x 10^3 J" vs "1610 J", but the value must match);
- the physical scenario and assumptions are identical;
- the quantity asked for (and its requested unit) is identical;
- nothing is added, dropped, or changed that could alter the answer.

## Version A (original)
{a}

## Version B (paraphrase)
{b}

Answer with ONLY a JSON object: {{"same": true|false, "reason": "<one line>"}}"""


def parse(t):
    m = re.search(r"\{.*\}", t, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def judge(model, a, b, retries=3):
    for _ in range(retries):
        try:
            out = parse(model.generate(PROMPT.format(a=a, b=b),
                                       "You judge problem equivalence. Reply with only JSON.").text)
        except ModelError:
            continue
        if out and "same" in out:
            return bool(out["same"]), out.get("reason", "")
    return None, "no verdict"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--base", default="benchmark/base.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--judges", default=",".join(JUDGES),
                    help="comma-separated judge models (two independent vendors)")
    args = ap.parse_args()

    judges_list = tuple(j.strip() for j in args.judges.split(","))
    base = {p["id"]: p for p in json.load(open(args.base))}
    paras = json.load(open(args.input))
    models = {n: build_model(load_config(n)) for n in judges_list}

    def work(v):
        orig = base.get(v["parent_id"])
        if orig is None:
            return {"id": v["id"], "verdict": "ORPHAN"}
        verdicts = {}
        for n, m in models.items():
            same, reason = judge(m, orig["problem"], v["problem"])
            verdicts[n] = {"same": same, "reason": reason}
        oks = [verdicts[n]["same"] for n in judges_list]
        if all(x is True for x in oks):
            verdict = "EQUIVALENT"
        elif any(x is False for x in oks):
            verdict = "NOT_EQUIVALENT"
        else:
            verdict = "UNSURE"
        return {"id": v["id"], "parent": v["parent_id"], "verdict": verdict, "judges": verdicts}

    results, done = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(work, paras):
            results.append(r); done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(paras)}", flush=True)

    json.dump(results, open(args.out, "w"), indent=2, ensure_ascii=False)
    from collections import Counter
    print("verdicts:", dict(Counter(r["verdict"] for r in results)))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
