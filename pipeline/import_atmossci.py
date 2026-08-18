"""Harvest AtmosSci-Bench's parameter-perturbed problems as open-ended numeric ones.

AtmosSci-Bench (Relaxed-System-Lab) generates its multiple-choice questions from
symbolic templates by PARAMETER PERTURBATION: each template (qN) is instantiated
at many parameter settings, with the correct answer computed by the template's own
solver. Dropping the multiple-choice options leaves a parameter-perturbed *variant*
set of numeric problems with solver-computed answers — so ``parent_id`` is the
template and ``variant`` the instance, giving the contamination-resistance axis.

Our runner needs ``{id, problem, sub_answers:[{sub, value, unit}]}``. We parse each
solver-computed answer into numeric sub-answers so the same code/direct protocols
and numeric grading apply. ``--category`` keeps only the given problem types. An
answer with a non-numeric entry drops that problem rather than risk a wrong GT.

All instances go into one file; each carries ``parent_id`` (template) and
``variant`` (instance), so base-vs-variant grouping can be done at analysis time.

Usage:
    # the paper's MCQ10 set (91 templates x 10 instances):
    uv run python -m pipeline.import_atmossci --out benchmark/external/atmossci_mcq.json \
        --src .../data/jsonl/main_1-10.jsonl .../data/jsonl/extra_1-10.jsonl
    # atmospheric categories only:
    uv run python -m pipeline.import_atmossci --out benchmark/external/atmossci_mcq.json \
        --src .../data/jsonl/main_1-10.jsonl .../data/jsonl/extra_1-10.jsonl \
        --category "Atmospheric Physics" "Atmospheric Dynamics"
"""

import re
import json
import argparse
from pathlib import Path


def parse_answer(answer: str):
    """Parse a plain-text answer into [(value, unit), ...], or None.

    Entries are newline-separated, each optionally labelled (``(1):``, ``North:``,
    ``0-10min:`` …). We take the value AFTER the last colon, so numbers inside a
    label (a time bin like ``0-10min``) are never mistaken for the answer."""
    sub_answers = []
    for line in answer.split("\n"):
        line = line.strip().rstrip(",").strip()
        if not line:
            continue
        value_part = line.rsplit(":", 1)[-1].strip() if ":" in line else line
        if re.match(r"^[-+]?inf(inity)?\b", value_part, re.IGNORECASE):
            value, unit = ("-inf" if value_part.lstrip().startswith("-") else "inf"), ""
        else:
            number = re.match(r"^([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(.*)$", value_part)
            if not number:
                return None  # an entry with no value -> reject the whole problem
            value, unit = number.group(1), number.group(2).strip()
        sub_answers.append((value, unit))
    return sub_answers or None


def convert(problem: dict):
    """Map one MCQ instance to an open-ended record (options dropped), or None."""
    parsed = parse_answer(problem["answer"])
    if not parsed:
        return None
    template = re.match(r"(MCQ_\d+)_(\d+)", problem["id"])
    return {
        "id": problem["id"],
        "parent_id": template.group(1) if template else None,
        "variant": int(template.group(2)) if template else None,
        "source": "AtmosSci-Bench",
        "problem": problem["problem"],
        "sub_answers": [{"sub": str(index + 1), "value": value, "unit": unit}
                        for index, (value, unit) in enumerate(parsed)],
        "category": problem.get("type", ""),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--src", nargs="+", required=True, help="AtmosSci-Bench MCQ jsonl file(s)")
    parser.add_argument("--out", required=True)
    parser.add_argument("--category", nargs="+", default=None,
                        help="keep only these problem types (default: all)")
    args = parser.parse_args()
    keep = set(args.category) if args.category else None

    records = [json.loads(line) for path in args.src
               for line in Path(path).read_text().splitlines() if line.strip()]
    converted = [record for record in (convert(problem) for problem in records)
                 if record and (keep is None or record["category"] in keep)]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(converted, indent=2, ensure_ascii=False))
    templates = {record["parent_id"] for record in converted}
    scope = f" in {sorted(keep)}" if keep else ""
    print(f"converted {len(converted)}/{len(records)} instances from {len(templates)} templates{scope}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
