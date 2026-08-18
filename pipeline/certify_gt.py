"""Ground-truth certification (S1+S2): re-anchor textbook answers and triangulate.

Step 1 (S1): recover each problem's ORIGINAL textbook answer (dropped from the
final dataset) from the intermediate extraction artifacts and re-attach it.

Step 2 (S2): triangulate the committed solver's ground truth against the textbook
answer and assign a certification tier:

    A_TEXTBOOK   solver output agrees with the textbook answer (numeric, <=tol)
    C_CONFLICT   textbook answer exists but solver disagrees  -> needs adjudication
    SYMBOLIC     textbook answer is symbolic/qualitative (no number) -> exclude review
    B_UNANCHORED no textbook answer found -> needs independent-solver consensus
    EXEC_ERROR   solver fails to execute

This stage uses NO LLM calls: it is fully deterministic and reproducible.
The independent-LLM-solver leg of the triangle (S2b) is run separately.

Usage:
    uv run python -m pipeline.certify_gt
    uv run python -m pipeline.certify_gt --input pipeline/reports/problems_final.json -t 0.02
"""

import json
import re
import glob
import argparse
from collections import Counter, defaultdict

from eval.engine import run_solver


# ── number extraction (handles a x 10^{b}, 10^{-4}, e-notation, commas) ──

def extract_numbers(s) -> list[float]:
    s = str(s)
    # unicode superscripts -> ^digits  (e.g. 10⁶ -> 10^6, m⁻² -> m^-2)
    sup = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
           "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-", "⁺": "+"}
    s = re.sub("[" + "".join(sup) + "]+",
               lambda m: "^" + "".join(sup[c] for c in m.group()), s)
    s = s.replace("\\times", " x ").replace("×", " x ").replace("\\,", "")
    # thousands separator only ("100,000"->"100000"); keep list commas ("4.3, 2.5")
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    # collapse spaced-out digits from per-character LaTeX ("5 0" -> "50", "3 . 3" -> "3.3").
    # Done BEFORE list-comma handling so "4.3, 2.5" (comma present) is never merged;
    # decimal merge requires a digit before the dot, so enumerations like "b. 10" are safe.
    s = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", s)
    s = re.sub(r"(?<=\d)\s+(?=\d)", "", s)
    # strip unit exponents (m^-2, s^{-1}, K^-1) so they aren't read as numbers;
    # leaves 10^4 intact (digit before ^, not a letter)
    s = re.sub(r"([A-Za-z])\s*\^\s*\{?\s*-?\d+\s*\}?", r"\1", s)
    out = []
    # mantissa x 10^exp
    for m in re.finditer(r"([-+]?\d*\.?\d+)\s*[xX*]\s*10\s*\^?\s*\{?\s*([-+]?\d+)\s*\}?", s):
        out.append(float(m.group(1)) * 10 ** int(m.group(2)))
    s2 = re.sub(r"[-+]?\d*\.?\d+\s*[xX*]\s*10\s*\^?\s*\{?\s*[-+]?\d+\s*\}?", "", s)
    # bare 10^{-4}
    for m in re.finditer(r"(?<![\d.])10\s*\^\s*\{?\s*([-+]?\d+)\s*\}?", s2):
        out.append(10 ** int(m.group(1)))
    s3 = re.sub(r"10\s*\^\s*\{?\s*[-+]?\d+\s*\}?", "", s2)
    # plain + e-notation
    for m in re.finditer(r"[-+]?\d*\.?\d+[eE][-+]?\d+|[-+]?\d*\.?\d+", s3):
        try:
            out.append(float(m.group(0)))
        except ValueError:
            pass
    return out


def to_float(v):
    try:
        return float(str(v).replace("×", "e").replace("x", "e"))
    except (ValueError, TypeError):
        return None


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


SOLUTION_MANUAL = "pipeline/reports/solution_manual_answers.json"


def load_textbook_answers() -> dict:
    """Return {(norm_book, id): (answer, source)} from all ground-truth sources.

    Keyed by (book, id), NOT id alone: ids are reused across sources
    (e.g. 'p_0' is a different problem in wallace_hobbs vs new_batch), so an
    id-only merge silently mis-attributes answers. The book field disambiguates.

    Sources, in priority order (concise/authoritative first):
      "textbook"        – original_answer/answer captured at extraction (concise)
      "solution_manual" – block parsed from the published solution PDF (prose)
    """
    table = {}
    # concise textbook answers (note: validated_problems_first_batch.json lives at the
    # data/intermediate root, NOT under extracted/* — it holds the Practical Meteorology
    # original answers captured from the book's Sample Applications)
    for f in (glob.glob("pipeline/reports/extracted/*/validated_problems.json")
              + glob.glob("pipeline/reports/extracted/*/extracted_problems.json")
              + glob.glob("pipeline/reports/*validated_problems*.json")):
        for e in json.load(open(f)):
            a = e.get("original_answer") or e.get("answer")
            if e.get("id") and e.get("book") and a:
                table.setdefault((_norm(e["book"]), str(e["id"])), (a, "textbook"))
    # solution-manual blocks (only fill gaps; do not override concise textbook)
    try:
        sm = json.load(open(SOLUTION_MANUAL))
    except FileNotFoundError:
        sm = {}
    for k, a in sm.items():
        book, pid = k.split("\t")
        table.setdefault((_norm(book), str(pid)), (a, "solution_manual"))
    return table


def lookup_textbook(problem: dict, table: dict):
    book = _norm(problem.get("book", ""))
    pid = str(problem.get("id"))
    if (book, pid) in table:
        return table[(book, pid)]
    # sub-part id suffix ("4.4b" -> "4.4"): the manual numbers the parent problem
    stripped = re.sub(r"[a-zA-Z]+$", "", pid)
    if stripped != pid and (book, stripped) in table:
        return table[(book, stripped)]
    return (None, None)


def certify(problem: dict, table: dict, tol: float) -> dict:
    pid = problem["id"]
    tb, source = lookup_textbook(problem, table)
    rec = {"id": pid, "book": problem.get("book", ""),
           "solver_gt": [s["value"] for s in problem["sub_answers"]],
           "textbook_answer": tb, "source": source}

    ok, results, info = run_solver(problem["code"])
    if not ok:
        rec["tier"] = "EXEC_ERROR"
        rec["note"] = info[:120]
        return rec

    solver_nums = [to_float(s["value"]) for s in problem["sub_answers"]]
    solver_nums = [x for x in solver_nums if x is not None]
    rec["solver_nums"] = solver_nums

    if tb is None:
        rec["tier"] = "B_UNANCHORED"
        return rec

    tb_nums = extract_numbers(tb)
    rec["textbook_nums"] = tb_nums
    if not tb_nums:
        rec["tier"] = "SYMBOLIC"
        return rec

    # every solver number must find a textbook number within tol
    unmatched = [g for g in solver_nums
                 if not any(abs(g - o) / max(abs(o), 1e-12) <= tol for o in tb_nums)]
    matched = not unmatched

    if source == "solution_manual":
        # prose blocks: a match weakly CONFIRMS; a non-match is NOT conclusive
        # (final answers often live in equations/figures), so route to expert.
        rec["tier"] = "A_SOLUTION" if matched else "EXPERT_REVIEW"
        if not matched:
            rec["unmatched"] = unmatched
    else:
        # concise textbook answer: non-match is a genuine conflict
        if matched:
            rec["tier"] = "A_TEXTBOOK"
            rec["subpart_count_mismatch"] = len(solver_nums) != len(tb_nums)
        else:
            rec["tier"] = "C_CONFLICT"
            rec["unmatched"] = unmatched
    return rec


def main():
    ap = argparse.ArgumentParser(description="GT certification: textbook vs solver triangulation")
    ap.add_argument("--input", default="pipeline/reports/problems_final.json")
    ap.add_argument("--tolerance", "-t", type=float, default=0.02,
                    help="tight tolerance for textbook agreement (default 2%%)")
    ap.add_argument("--enriched-out", default="pipeline/reports/problems_final_certified.json")
    ap.add_argument("--report-out", default="pipeline/reports/gt_certification_report.json")
    args = ap.parse_args()

    problems = json.load(open(args.input))
    table = load_textbook_answers()
    print(f"loaded {len(problems)} problems | textbook answer entries (by book+id): {len(table)}")

    records = [certify(p, table, args.tolerance) for p in problems]
    by_tier = Counter(r["tier"] for r in records)

    # enriched dataset: attach textbook_answer + certification
    enriched = []
    rec_by_id = {r["id"]: r for r in records}
    for p in problems:
        q = dict(p)
        r = rec_by_id[p["id"]]
        q["textbook_answer"] = r.get("textbook_answer")
        q["certification"] = {"tier": r["tier"], "source": r.get("source")}
        enriched.append(q)
    json.dump(enriched, open(args.enriched_out, "w"), indent=2, ensure_ascii=False)
    json.dump(records, open(args.report_out, "w"), indent=2, ensure_ascii=False)

    print(f"\n=== Certification tiers (tol={args.tolerance:.0%}) ===")
    order = ["A_TEXTBOOK", "A_SOLUTION", "EXPERT_REVIEW", "C_CONFLICT", "SYMBOLIC", "B_UNANCHORED", "EXEC_ERROR"]
    for t in order:
        print(f"  {t:14s} {by_tier.get(t,0):4d}")
    print(f"  {'TOTAL':14s} {len(records):4d}")

    # coverage by book
    print("\n=== textbook-anchored (A+C+SYMBOLIC) vs unanchored by book ===")
    tot, anc = defaultdict(int), defaultdict(int)
    for r in records:
        b = r["book"].split()[0] if r["book"] else "?"
        tot[b] += 1
        anc[b] += r["tier"] in ("A_TEXTBOOK", "A_SOLUTION", "EXPERT_REVIEW", "C_CONFLICT", "SYMBOLIC")
    for b in sorted(tot, key=lambda b: -tot[b]):
        print(f"  {b:14s} anchored {anc[b]:3d}/{tot[b]:3d}")

    conflicts = [r for r in records if r["tier"] == "C_CONFLICT"]
    print(f"\n=== C_CONFLICT ({len(conflicts)}) — solver GT disagrees with textbook ===")
    for r in conflicts:
        print(f"  {r['id']:8s} solver={r['solver_gt']}  textbook={str(r['textbook_answer'])[:65]}")

    sym = [r for r in records if r["tier"] == "SYMBOLIC"]
    print(f"\n=== SYMBOLIC ({len(sym)}) — textbook answer non-numeric, review for exclusion ===")
    for r in sym:
        print(f"  {r['id']:8s} textbook={str(r['textbook_answer'])[:70]}")

    print(f"\nwrote enriched dataset -> {args.enriched_out}")
    print(f"wrote full report      -> {args.report_out}")


if __name__ == "__main__":
    main()
