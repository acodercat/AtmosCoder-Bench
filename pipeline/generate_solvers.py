"""
Generate and verify Python solvers for each problem.

For each problem:
  1. LLM generates a solve() function that returns a results dict
  2. Execute via exec() + call solve()
  3. Compare returned values to known answers (5% tolerance)
  4. Retry with error feedback if failed (up to 3 attempts)

Output: data/processed/solvers.json — validated (problem, code, answer) triples
"""

import json
import os
import time
import argparse

from openai import OpenAI

from .config import Config
from .pdf import call_llm
from eval.engine import extract_code as _extract_code, run_solver, verify_solver

SOLVER_PROMPT = """You are an expert atmospheric scientist and Python programmer.
Given a physics/atmospheric science problem, write a `solve()` function that computes and returns the answer(s).

## Rules
1. All given/input values from the problem must be **function parameters with defaults**.
2. Derived values (unit conversions, intermediate calculations) stay inside the function body.
3. Return a dict mapping sub-part id (string) to {{"value": <number>, "unit": "<unit>"}}.
4. Only use standard library (math, etc.). No external packages.
5. Do unit conversions explicitly in code.
6. Add brief comments explaining the physics/formula being applied.

## Example
```python
def solve(Q=34, u=5, sigma_y=24, sigma_z=37) -> dict:
    import math

    # Centreline concentration: c = Q / (2 * pi * u * sigma_y * sigma_z)
    c = Q / (2 * math.pi * u * sigma_y * sigma_z)
    c_ug = c * 1e6  # g/m^3 → μg/m^3

    return {{
        "1": {{"value": round(c_ug, 1), "unit": "μg/m^3"}},
    }}
```

## Problem
{problem}

Write ONLY the Python code containing the solve() function. No explanation."""

RETRY_PROMPT = """The previous solver failed verification.

## Code
```python
{code}
```

## Execution Result
{exec_result}

## Verification Details
{details}

## Problem (reminder)
{problem}

Fix the code. Common issues:
- Unit conversion errors (km↔m, g↔μg, etc.)
- Wrong formula or missing terms
- Integer division instead of float
- All given values must be function parameters with defaults

Write ONLY the corrected Python code with the solve() function."""


def generate_solver_for_problem(problem: dict, config: Config, client: OpenAI, max_attempts: int = 3) -> dict | None:
    """Generate and verify a solver for one problem."""
    problem_text = problem["problem"]
    expected = problem["sub_answers"]

    # NOTE: expected answers are NOT passed to the LLM — only used for verification
    user_msg = SOLVER_PROMPT.format(problem=problem_text)
    raw = call_llm(client, config, "You are a Python code generator. Return ONLY executable Python code.", user_msg)
    code = _extract_code(raw)

    for attempt in range(max_attempts):
        success, solver_results, exec_info = run_solver(code)

        if success:
            passed, details = verify_solver(solver_results, expected)
            if passed:
                return {
                    "id": problem["id"],
                    "book": problem.get("book", ""),
                    "problem": problem_text,
                    "code": code,
                    "sub_answers": expected,
                    "verified": True,
                    "attempts": attempt + 1,
                }
        else:
            details = [{"error": exec_info[:500]}]

        if attempt < max_attempts - 1:
            retry_msg = RETRY_PROMPT.format(
                code=code, exec_result=exec_info[:500],
                details=json.dumps(details, indent=2),
                problem=problem_text,
            )
            raw = call_llm(client, config, "You are a Python code generator. Return ONLY executable Python code.", retry_msg)
            code = _extract_code(raw)

    return None


def main():
    parser = argparse.ArgumentParser(description="Generate and verify Python solvers")
    parser.add_argument("--input", default="evals/problems.json")
    parser.add_argument("--output", default="evals/problems.json")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    config = Config()
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    with open(args.input) as f:
        problems = json.load(f)

    end = args.start + args.limit if args.limit else len(problems)
    problems = problems[args.start:end]
    print(f"Processing {len(problems)} problems (index {args.start}-{args.start + len(problems) - 1})")

    results = []
    if os.path.exists(args.output):
        with open(args.output) as f:
            results = json.load(f)
        existing_ids = {r["id"] for r in results}
        print(f"Loaded {len(results)} existing, resuming...")
    else:
        existing_ids = set()

    passed, failed = 0, 0
    for i, p in enumerate(problems):
        pid = p["id"]
        if pid in existing_ids:
            continue

        print(f"\n[{args.start + i}] {pid} ({len(p['sub_answers'])} answers)...", flush=True)

        result = generate_solver_for_problem(p, config, client)
        if result:
            results.append(result)
            passed += 1
            print(f"  PASS (attempt {result['attempts']})")
        else:
            failed += 1
            print("  FAIL after 3 attempts")

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        time.sleep(1)

    print(f"\n=== Done: {passed} passed, {failed} failed, {len(results)} total verified ===")


if __name__ == "__main__":
    main()
