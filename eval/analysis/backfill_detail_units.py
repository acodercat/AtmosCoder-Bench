"""Backfill units into result-file `details` (one-off migration, no LLM calls).

verify_solver stores per-sub `expected_units` / `actual_unit` since 2026-07-23 so
offline re-grading (eval.analysis.accuracy) can replay the runner's unit-aware
rule. Earlier result files stored bare numbers only. This script back-fills them
from artifacts already on disk:

- `expected_units`: joined from the benchmark files by (problem id, sub) — the
  ground truth always carried units.
- `actual_unit`: recovered only where it changes a grade — subs recorded
  passed=True whose bare numeric compare fails (these passed via unit
  reconciliation). Recovery is offline: code mode re-executes the stored final
  solver locally (run_solver, no API); direct mode re-parses the stored response
  boxes and matches the parsed number to the stored actual. Subs that never
  needed reconciliation keep `actual_unit: ""` (unknown-but-irrelevant at the
  recorded tolerance).

Idempotent; rewrites files in place (git is the backup).

    uv run python -m eval.analysis.backfill_detail_units            # all live experiment dirs
    uv run python -m eval.analysis.backfill_detail_units --exp core_code
"""

import json
import glob
import argparse
from pathlib import Path

from eval.engine import compare_values, run_solver, extract_code, _units_reconcile
from eval.protocols import _balanced_boxed, _parse_number, _parse_unit

BENCH_SOURCES = [
    "benchmark/core.json",
    "benchmark/variants_numeric.json",
    "benchmark/variants_paraphrase.json",
    "benchmark/traps.json",
    "benchmark/contradictions.json",
    "benchmark/external/atmossci_mcq.json",
    "benchmark/external/atmossci_mcq6.json",
    "benchmark/scaffolding_ablation/*.json",
    "benchmark/cross_domain/*.json",
]

LIVE_EXPS = ["core_code", "core_code_restrictive", "core_direct", "cross_domain",
             "mcq_code", "trap", "scaffolding_ablation",
             "variants_numeric_code", "variants_paraphrase_code"]


def build_unit_map():
    """(problem id, sub) -> ordered [(value, unit), ...], as verify_solver saw them.

    A sub may list several acceptable values, each with its own unit (e.g. the
    same answer accepted in °C and in K), so the map keeps the aligned pair list
    in benchmark order — the same order verify_solver stored `expected` in.
    """
    unit_map = {}
    for pattern in BENCH_SOURCES:
        for path in glob.glob(pattern):
            try:
                data = json.load(open(path))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, list):
                continue
            for prob in data:
                per_sub = {}
                for sub_answer in prob.get("sub_answers") or []:
                    per_sub.setdefault(str(sub_answer["sub"]), []).append(
                        (str(sub_answer["value"]), sub_answer.get("unit", "")))
                for sub, pairs in per_sub.items():
                    key = (prob["id"], sub)
                    if key in unit_map and unit_map[key] != pairs:
                        raise SystemExit(f"answer collision for {key}: "
                                         f"{unit_map[key]!r} vs {pairs!r} in {path}")
                    unit_map[key] = pairs
    return unit_map


def sub_passes(detail, tolerance=0.05):
    """The offline unit-aware rule (same as accuracy.regrade_one, per sub)."""
    actual = detail.get("actual")
    actual_unit = detail.get("actual_unit", "")
    expected_values = detail.get("expected") or []
    expected_units = detail.get("expected_units") or [""] * len(expected_values)
    for expected_value, expected_unit in zip(expected_values, expected_units):
        try:
            if compare_values(str(expected_value), actual, tolerance) or \
               _units_reconcile(expected_value, expected_unit, actual, actual_unit, tolerance):
                return True
        except Exception:
            pass
    return False


def actual_units_from_code(record):
    """Re-execute the stored final solver locally; map sub -> returned unit."""
    attempts = record.get("attempts") or []
    if not attempts:
        return None
    code = extract_code(attempts[-1].get("response") or "")
    if not code:
        return None
    ok, results, _ = run_solver(code)
    if not ok or not isinstance(results, dict):
        return None
    details = record.get("details") or []
    subs = [str(d["sub"]) for d in details]
    keys = list(results.keys())
    out = {}
    for position, sub in enumerate(subs):
        entry = results.get(sub)
        if entry is None and position < len(keys):  # positional fallback, as verify_solver
            entry = results[keys[position]]
        if isinstance(entry, dict):
            out[sub] = str(entry.get("unit", ""))
    return out


def actual_units_from_direct(record):
    """Re-parse the stored boxed answers; match parsed number to stored actual."""
    attempts = record.get("attempts") or []
    if not attempts:
        return None
    boxes = _balanced_boxed(attempts[-1].get("response") or "")
    parsed = []
    for box in boxes:
        number = _parse_number(box)
        if number is not None:
            parsed.append((number, _parse_unit(box)))
    out = {}
    for detail in record.get("details") or []:
        actual = detail.get("actual")
        if not isinstance(actual, (int, float)):
            continue
        units = {unit for number, unit in parsed
                 if abs(number - actual) <= 1e-9 * max(1.0, abs(actual))}
        if len(units) == 1:
            out[str(detail["sub"])] = units.pop()
    return out


def backfill_file(path, unit_map, tolerance):
    data = json.load(open(path))
    results = data.get("results")
    if not isinstance(results, list):
        return None
    mode = (data.get("metrics") or {}).get("mode", "code")
    stats = {"records": 0, "subs_units": 0, "recovered": 0, "unrecovered": 0, "unknown_id": 0}
    changed = False
    for record in results:
        details = record.get("details")
        if not details:
            continue
        stats["records"] += 1
        # pass 1: expected units from the benchmark join
        for detail in details:
            if "sub" not in detail:  # e.g. verify_solver's [{"error": "empty results"}]
                continue
            key = (record["id"], str(detail["sub"]))
            if "expected_units" not in detail:
                pairs = unit_map.get(key)
                expected = [str(v) for v in (detail.get("expected") or [])]
                if pairs is not None and len(pairs) == len(expected):
                    detail["expected_units"] = [u for _, u in pairs]
                    stats["subs_units"] += 1
                    changed = True
                else:
                    stats["unknown_id"] += 1
        # pass 2: recover actual units where they change the offline grade —
        # (a) subs recorded passed=True that the offline rule cannot yet pass
        #     (the pass hinged on the model's declared unit), and
        # (b) subs recorded passed=False that the offline rule would wrongly
        #     pass with an unknown ("") unit (the runtime unit blocked a
        #     reconcile the empty unit permits, e.g. % vs a declared kelvin).
        needs_actual = [d for d in details
                        if "sub" in d and isinstance(d.get("actual"), (int, float))
                        and "actual_unit" not in d
                        and bool(d.get("passed")) != sub_passes(d, tolerance)]
        recovered = None
        if needs_actual:
            recovered = (actual_units_from_code(record) if mode == "code"
                         else actual_units_from_direct(record))
        for detail in needs_actual:
            unit = (recovered or {}).get(str(detail["sub"]))
            if unit is not None:
                detail["actual_unit"] = unit
                changed = True
            if sub_passes(detail, tolerance) == bool(detail.get("passed")):
                stats["recovered"] += 1
            else:
                stats["unrecovered"] += 1
    if changed:
        json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp", nargs="+", default=LIVE_EXPS)
    parser.add_argument("--tolerance", type=float, default=0.05,
                        help="run tolerance used to detect reconciliation-passed subs")
    args = parser.parse_args()
    unit_map = build_unit_map()
    print(f"unit map: {len(unit_map)} (id, sub) entries")
    for exp in args.exp:
        for path in sorted(glob.glob(f"experiments/{exp}/*.json")):
            stats = backfill_file(Path(path), unit_map, args.tolerance)
            if stats is None:
                continue
            flag = ""
            if stats["unrecovered"]:
                flag = f"  !! {stats['unrecovered']} reconciliation-passed subs UNRECOVERED"
            if stats["unknown_id"]:
                flag += f"  ?? {stats['unknown_id']} subs with no benchmark unit"
            print(f"{path}: exp_units+{stats['subs_units']} actual_units+{stats['recovered']}{flag}")


if __name__ == "__main__":
    main()
