"""Print benchmark statistics.

Usage:
    python -m eval.stats                        # summary
    python -m eval.stats --category              # by category
    python -m eval.stats --book                  # by book
    python -m eval.stats --list                  # list all problems
    python -m eval.stats --list --filter atmospheric_dynamics
    python -m eval.stats --results               # show evaluation results
"""

import argparse
import json
from pathlib import Path
from collections import Counter

from tabulate import tabulate

PROBLEMS_FILE = Path("benchmark/core.json")
VARIANTS_FILE = Path("benchmark/variants_numeric.json")
RUNS_DIR = Path("experiments")


def load_problems():
    with open(PROBLEMS_FILE) as f:
        return json.load(f)


def load_variants():
    if VARIANTS_FILE.exists():
        with open(VARIANTS_FILE) as f:
            return json.load(f)
    return []


def print_summary(problems, variants):
    total_subs = sum(len(problem.get("sub_answers", [])) for problem in problems)
    rows = [
        ["Problems", len(problems)],
        ["Sub-answers", total_subs],
        ["Variants", len(variants)],
        ["Total (problems + variants)", len(problems) + len(variants)],
        ["Categories", len(set(problem.get("category", "") for problem in problems))],
        ["Source books", len(set(problem["book"] for problem in problems))],
    ]
    print(tabulate(rows, headers=["Metric", "Value"], tablefmt="simple_outline",
                   colalign=("left", "right")))


def print_by_category(problems):
    categories = Counter(problem.get("category", "unknown") for problem in problems)
    rows = []
    for category, count in categories.most_common():
        topics = Counter(problem.get("topic", "") for problem in problems
                         if problem.get("category") == category)
        top_topics = ", ".join(f"{topic} ({topic_count})"
                               for topic, topic_count in topics.most_common(3) if topic)
        rows.append([category, count, f"{count/len(problems)*100:.1f}%", top_topics])
    rows.append(["TOTAL", len(problems), "100%", ""])
    print(tabulate(rows, headers=["Category", "Count", "%", "Top Topics"],
                   tablefmt="simple_outline", colalign=("left", "right", "right", "left")))


def print_by_book(problems):
    books = Counter(problem["book"] for problem in problems)
    rows = [[book, count, f"{count/len(problems)*100:.1f}%"] for book, count in books.most_common()]
    rows.append(["TOTAL", len(problems), "100%"])
    print(tabulate(rows, headers=["Book", "Count", "%"],
                   tablefmt="simple_outline", colalign=("left", "right", "right")))


def print_list(problems, category_filter=None):
    filtered = problems
    if category_filter:
        filtered = [problem for problem in problems if problem.get("category") in category_filter]
    rows = [[problem["id"], problem.get("category", ""), problem.get("topic", ""),
             len(problem.get("sub_answers", [])), problem["book"][:30]]
            for problem in filtered]
    print(f"\n{len(rows)} problems" + (f" (filter: {category_filter})" if category_filter else ""))
    print(tabulate(rows, headers=["ID", "Category", "Topic", "Subs", "Book"],
                   tablefmt="simple_outline", colalign=("left", "left", "left", "right", "left")))


def print_results():
    if not RUNS_DIR.exists():
        print("No runs found.")
        return
    rows = []
    for result_file in sorted(RUNS_DIR.rglob("*.json")):
        try:
            metrics = json.loads(result_file.read_text()).get("metrics")
            if not metrics:  # skip non-result jsons (compare/summary outputs)
                continue
            rows.append([
                metrics.get("exp_id") or result_file.parent.name, metrics.get("model", ""),
                metrics.get("total", 0), metrics.get("passed", 0), f"{metrics.get('accuracy', 0):.1%}",
                metrics.get("failed", 0), metrics.get("errors", 0), f"{metrics.get('total_tokens', 0):,}",
            ])
        except Exception:
            continue
    if rows:
        print(tabulate(rows, headers=["Experiment", "Model", "Total", "Passed", "Accuracy", "Failed", "Errors", "Tokens"],
                       tablefmt="simple_outline", colalign=("left", "left", "right", "right", "right", "right", "right", "right")))
    else:
        print("No results found.")


def main():
    parser = argparse.ArgumentParser(description="AtmosCoder-Bench statistics")
    parser.add_argument("--category", "-c", action="store_true", help="Show by category")
    parser.add_argument("--book", "-b", action="store_true", help="Show by book")
    parser.add_argument("--list", "-l", action="store_true", help="List all problems")
    parser.add_argument("--filter", nargs="+", default=None, help="Filter by category (with --list)")
    parser.add_argument("--results", "-r", action="store_true", help="Show evaluation results")
    args = parser.parse_args()

    problems = load_problems()
    variants = load_variants()

    if args.results:
        print_results()
    elif args.category:
        print_by_category(problems)
    elif args.book:
        print_by_book(problems)
    elif args.list:
        print_list(problems, args.filter)
    else:
        print_summary(problems, variants)
        print()
        print_by_category(problems)
        print()
        print_by_book(problems)


if __name__ == "__main__":
    main()
