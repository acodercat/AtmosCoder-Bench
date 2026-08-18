"""LLM well-posedness / answer-uniqueness audit for the 436 base problems.

Complements the base_rep convergent-error mining (which catches problems where
STRONG models actually split on a value). This catches problems where the text
is under-specified but models happened NOT to split (all recalled the same value,
or the problem is rarely attempted). It does NOT check GT numerical correctness
(certify_gt / k2 do that) and it does NOT judge difficulty.

The ONE question: solving from the text alone, would every competent atmospheric
scientist reach the SAME answer (within 5%)? Omitting a UNIVERSAL, uniquely-
recallable constant/formula is intended design (a knowledge test) and is NEVER a
defect. A defect exists only when an answer-affecting value/convention/unit is
unstated AND has >=2 defensible values differing >5%.

Two-vendor consensus (gpt55-reasoning + gemini-3.1-pro): only BOTH-DEFECT is high
confidence; split -> REVIEW. Output is a high-recall suspect list for skeptical
human re-verification, NOT a proof. Resume-safe.

    uv run python -m pipeline.llm_audit_wellposed --all --workers 8
    uv run python -m pipeline.llm_audit_wellposed --ids snp_94 air_126 4.6
"""

import json
import re
import argparse
import threading
import concurrent.futures
from pathlib import Path
from collections import Counter

from eval.models.registry import load_config, build_model

INPUT = Path("benchmark/base.json")
OUT = Path("pipeline/reports/llm_audit_wellposed.json")
JUDGES = ["gpt55-reasoning", "gemini-3.1-pro"]

AUDIT_SYSTEM = (
    "You audit an atmospheric-science benchmark for ONE thing only: does each problem "
    "have a UNIQUE answer? The problems deliberately omit standard constants and formulas "
    "- a competent solver is expected to RECALL them. That design is correct and is NEVER "
    "a defect. Do NOT overthink. Do NOT hunt for edge cases or hypothetical alternative "
    "methods. Assume a competent atmospheric scientist solving in good faith. Your default "
    "is OK; flag only when you are certain the answer genuinely splits."
)

AUDIT_PROMPT = """ONE question: solving from the problem text alone, would every competent atmospheric scientist arrive at the SAME numerical answer (within 5%)?
  - If YES (a value may be omitted, but it is universal knowledge everyone recalls to the same number - g, R, sigma, k_B, N_A, water density, molar volume, c_water, standard latent heat used consistently, canonical mid-latitude f0, etc.) -> OK. Omitting recallable universal knowledge is intended design, never a defect.
  - If NO - because some answer-affecting value/convention/unit is unstated AND genuinely has two or more defensible values that a competent solver could reasonably choose, giving answers that differ by MORE than 5% -> DEFECT.

Only these count as DEFECTS (real, non-hypothetical ambiguity):
  - A physical value that is genuinely temperature/condition-dependent with no condition given (e.g. latent heat with no temperature: 2.5e6 vs 2.26e6).
  - A required temperature/pressure/altitude reference the text never gives and that isn't a single standard value.
  - A named quantity with two established competing definitions (e.g. "mean droplet distance": N^(-1/3) vs equal-volume-sphere diameter).
  - An output unit that is genuinely undetermined AND the stored answer has NO unit label (so a grader can't reconcile).

NOT defects - never flag (this is normal, well-posed design):
  - Any universal constant omitted from the text (recall is expected).
  - A standard formula the solver must recall.
  - Canonical values with <5% spread (c_water 4184-4186, R_dry 287, g 9.8-9.81).
  - A value already present in the text in any notation.
  - The stored answer being in a unit a grader can reconcile (it has a unit label).
  - The problem being hard, terse, multi-step, or needing recalled knowledge.

Do not invent a second "defensible" value just to flag. If the only alternatives are wrong methods or non-standard constants, it is OK.

## Problem text
{problem}
## Reference solver code   (shows which values the answer depends on)
{code}
## Stored answer(s)
{sub_answers}

Respond ONLY JSON:
{{"verdict":"OK"|"DEFECT","defects":[{{"quantity":"...","value_used_by_code":<v>,"competing_value":<v2>,"answer_spread_pct":<n>,"why_two_defensible_values":"...","fix":"state it|add unit label"}}]}}
OK -> {{"verdict":"OK","defects":[]}}"""


def _parse(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"verdict": "PARSE_ERROR", "defects": [], "raw": text[:300]}
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        try:
            obj = json.loads(re.search(r"\{.*?\}\s*$", m.group(0), re.DOTALL).group(0))
        except Exception:
            return {"verdict": "PARSE_ERROR", "defects": [], "raw": text[:300]}
    obj.setdefault("verdict", "PARSE_ERROR")
    obj.setdefault("defects", [])
    return obj


def audit_one(prob, models):
    prompt = AUDIT_PROMPT.format(
        problem=prob["problem"],
        code=prob["code"],
        sub_answers=json.dumps(prob["sub_answers"], ensure_ascii=False),
    )
    verdicts = {}
    for name, model in models.items():
        try:
            comp = model.generate(prompt, AUDIT_SYSTEM)
            verdicts[name] = _parse(comp.text)
        except Exception as e:  # noqa: BLE001
            verdicts[name] = {"verdict": "ERROR", "defects": [], "raw": str(e)[:200]}
    flags = [v.get("verdict") == "DEFECT" for v in verdicts.values()]
    consensus = "DEFECT" if all(flags) else "REVIEW" if any(flags) else "OK"
    return {"id": prob["id"], "consensus": consensus, "judges": verdicts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ids", nargs="+")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    problems = json.load(open(INPUT))
    if args.ids:
        by_id = {p["id"]: p for p in problems}
        sample = [by_id[i] for i in args.ids if i in by_id]
    else:
        sample = problems

    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"]: r for r in json.load(open(OUT))} if OUT.exists() else {}
    todo = [p for p in sample if p["id"] not in done]
    print(f"well-posedness audit: {len(sample)} problems, {len(done)} cached, "
          f"{len(todo)} to run | judges={JUDGES}")

    models = {name: build_model(load_config(name)) for name in JUDGES}
    results = dict(done)
    lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(audit_one, p, models): p["id"] for p in todo}
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            r = fut.result()
            with lock:
                results[r["id"]] = r
                json.dump(list(results.values()), open(OUT, "w"), ensure_ascii=False, indent=1)
            if i % 20 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}")

    sub = [results[p["id"]] for p in sample if p["id"] in results]
    counts = Counter(r["consensus"] for r in sub)
    print(f"\n=== consensus over {len(sub)} ===")
    for k in ("OK", "REVIEW", "DEFECT"):
        print(f"  {k:7s} {counts.get(k,0)}")
    flagged = [r for r in sub if r["consensus"] in ("DEFECT", "REVIEW")]
    print(f"\n=== flagged ({len(flagged)}) — DEFECT first ===")
    for r in sorted(flagged, key=lambda x: x["consensus"] != "DEFECT"):
        evs = []
        for jn, jv in r["judges"].items():
            for d in jv.get("defects", []):
                evs.append(f"[{jn[:6]}/{d.get('quantity')}] {d.get('why_two_defensible_values','')[:90]}")
        print(f"  {r['id']:14s} {r['consensus']:7s} {' || '.join(evs)[:200]}")
    print(f"\nwritten: {OUT}")


if __name__ == "__main__":
    main()
