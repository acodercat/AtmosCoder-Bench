"""Aggregate repeated runs of the same model (the runner's ``--run N`` reps).

The runner writes each repetition to ``experiments/<exp_id>/<model_id>.run<N>.json``
(vs the single-run ``<model_id>.json``). This collects all reps per model under an
exp-id and reports per-run accuracy plus mean / std / min / max — the run-to-run
variance signal — and pass@k (a problem counts as solved if ANY rep passed it).

    uv run python -m eval.analysis.runs --exp-id base_ds4_rep
    uv run python -m eval.analysis.runs --exp-id base_ds4_rep --model deepseek-v4-flash-260425
"""

import re
import json
import argparse
import statistics
from collections import defaultdict
from pathlib import Path

from tabulate import tabulate

RUN_RE = re.compile(r"^(?P<model>.+)\.run(?P<run>\d+)\.json$")


def acc(results):
    passed = sum(1 for r in results if r.get("passed"))
    errors = sum(1 for r in results if r.get("error"))
    denom = len(results) - errors
    return passed, denom, (passed / denom if denom else 0.0)


def main():
    ap = argparse.ArgumentParser(description="aggregate repeated --run reps of a model")
    ap.add_argument("--exp-id", required=True)
    ap.add_argument("--model", default=None, help="filter to one model_id (default: all)")
    args = ap.parse_args()

    exp_dir = Path(f"experiments/{args.exp_id}")
    if not exp_dir.is_dir():
        raise SystemExit(f"no such exp dir: {exp_dir}")

    # model_id -> {run_index: results}
    reps = defaultdict(dict)
    for f in sorted(exp_dir.glob("*.run*.json")):
        m = RUN_RE.match(f.name)
        if not m:
            continue
        model = m.group("model")
        if args.model and model != args.model:
            continue
        reps[model][int(m.group("run"))] = json.loads(f.read_text()).get("results", [])

    if not reps:
        raise SystemExit(f"no *.run*.json files in {exp_dir} (did you run with --run N?)")

    rows = []
    for model, runs in sorted(reps.items()):
        accs, passed_sets = [], []
        per_run = []
        for r in sorted(runs):
            p, d, a = acc(runs[r])
            accs.append(a)
            per_run.append(f"r{r}={a:.1%}({p}/{d})")
            passed_sets.append({x["id"] for x in runs[r] if x.get("passed")})
        union = set().union(*passed_sets) if passed_sets else set()
        # pass@k denominator: union of all graded ids across reps
        graded = set().union(*[{x["id"] for x in runs[r] if not x.get("error")} for r in runs]) if runs else set()
        rows.append([
            model, len(accs),
            f"{statistics.mean(accs):.1%}",
            (f"{statistics.stdev(accs):.1%}" if len(accs) > 1 else "—"),
            f"{min(accs):.1%}", f"{max(accs):.1%}",
            f"{len(union)/len(graded):.1%}" if graded else "—",
            " ".join(per_run),
        ])

    print(tabulate(rows, headers=["model", "#runs", "mean", "std", "min", "max",
                                  f"pass@{max(len(r) for r in reps.values())}", "per-run"],
                   tablefmt="github"))


if __name__ == "__main__":
    main()
