"""Independent opus48 audit of the de-scaffolding rewrites — confirm nothing broke.

For every problem whose text was rewritten to remove a formula, compare the ORIGINAL
and the NEW statement and check, with an independent judge (opus48), that the rewrite is
faithful and the problem is still sound:

  formula_removed   the given solving equation is genuinely gone (not partially left).
  numbers_intact    every numerical input in the original survives in the new text.
  unambiguous       with the formula gone, the scenario still pins the correct method
                    uniquely (no new ambiguity that admits a different answer).
  answerable        all data needed to compute the stored answer is present.

A deterministic pre-check also extracts the numbers from both texts and flags any input
magnitude that vanished. Read-only. opus48 only.

    uv run python -m pipeline.verify_descaffold --out pipeline/reports/descaffold_verify.json
"""

import json
import argparse
import threading
import concurrent.futures
from collections import Counter

from eval.models import load_config, build_model, ModelError
from pipeline.certify_gt import extract_numbers
from pipeline.type_params import appears_in_text

JUDGE = "opus48"

PROMPT = """An atmospheric-science problem was rewritten to make it harder by REMOVING a solving
formula it used to hand the reader. Audit the rewrite. The numeric answer must be unchanged.

## Original statement
{old}

## Rewritten statement
{new}

## The answer the problem must still yield
{answers}

Check each point, then give an overall verdict:
- formula_removed: is the given solving equation genuinely gone (not still present in another form)?
- numbers_intact: does the rewrite keep every numerical input value from the original (none dropped
  or altered)? Removing the formula's own constants is fine; the problem's data must remain.
- unambiguous: with the formula gone, does the stated scenario/assumptions still make the intended
  method unique, so a competent solver reaches the SAME answer (no new ambiguity)?
- answerable: is all data needed to compute the stated answer still present?

Reply with ONLY a JSON object:
{{"formula_removed": <bool>, "numbers_intact": <bool>, "unambiguous": <bool>,
  "answerable": <bool>, "verdict": "<GOOD|PROBLEM>", "reason": "<one sentence>"}}"""


def _parse(raw):
    text = raw.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _missing_numbers(old_text, new_text):
    """Input magnitudes present in the original but gone from the rewrite (deterministic)."""
    new_nums = [abs(n) for n in (extract_numbers(new_text) or []) if n is not None]
    missing = []
    for n in (extract_numbers(old_text) or []):
        if n is not None and n != 0 and not appears_in_text(abs(n), new_nums):
            missing.append(n)
    return missing


def audit(model, old_text, new_text, problem):
    answers = ", ".join(f'{s["sub"]}: {s["value"]} {s["unit"]}' for s in problem["sub_answers"])
    prompt = PROMPT.format(old=old_text, new=new_text, answers=answers)
    try:
        raw = model.generate(prompt, "You are a meticulous benchmark auditor. Reply with only JSON.").text
    except ModelError as exc:
        return {"verdict": "ERROR", "reason": str(exc)[:100]}
    parsed = _parse(raw)
    if not parsed or parsed.get("verdict") not in {"GOOD", "PROBLEM"}:
        return {"verdict": "UNPARSED", "reason": (raw or "")[:100]}
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default="benchmark/base.json")
    parser.add_argument("--orig", default="backups/pre_descaffold_20260620/base.json")
    parser.add_argument("--descaffold", default="pipeline/reports/descaffold.json")
    parser.add_argument("--out", default="pipeline/reports/descaffold_verify.json")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    new = {p["id"]: p for p in json.load(open(args.base))}
    old = {p["id"]: p["problem"] for p in json.load(open(args.orig))}
    changed = [x["id"] for x in json.load(open(args.descaffold)) if x["status"] == "ACCEPTED"]
    print(f"auditing {len(changed)} de-scaffolded problems | judge: {JUDGE}")

    model = build_model(load_config(JUDGE))
    report, lock = [], threading.Lock()

    def work(pid):
        problem = new[pid]
        verdict = audit(model, old[pid], problem["problem"], problem)
        missing = _missing_numbers(old[pid], problem["problem"])
        row = {"id": pid, **verdict, "missing_numbers": missing}
        with lock:
            report.append(row)
            tag = row.get("verdict")
            flag = "" if tag == "GOOD" and not missing else "  <-- CHECK"
            print(f"  {pid:12s} {tag}{' missing='+str(missing) if missing else ''}{flag}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        list(executor.map(work, changed))

    report.sort(key=lambda r: (r.get("verdict") == "GOOD" and not r["missing_numbers"], r["id"]))
    json.dump(report, open(args.out, "w"), indent=2, ensure_ascii=False)

    print("\nverdicts:", dict(Counter(r.get("verdict") for r in report)))
    flagged = [r for r in report if r.get("verdict") != "GOOD" or r["missing_numbers"]]
    print(f"clean: {len(report) - len(flagged)} / {len(report)}")
    for r in flagged:
        print(f"  FLAG {r['id']:12s} verdict={r.get('verdict')} missing={r['missing_numbers']} | {r.get('reason','')}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
