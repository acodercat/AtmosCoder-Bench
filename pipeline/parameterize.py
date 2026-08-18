"""Refactor solvers: extract hardcoded values into function parameters with defaults.

Uses LLM to read the problem + current solve() and rewrite with parameters.
Runs 10 concurrent requests, verifies each refactored solver still passes.
"""

import json
import argparse
import concurrent.futures

from openai import OpenAI

from .config import Config
from eval.engine import run_solver, verify_solver

REFACTOR_PROMPT = """You are refactoring a Python solve() function.

## Current Code
```python
{code}
```

## Problem (for context)
{problem}

## Task
Rewrite solve() so that all **given/input values from the problem** become function parameters with their current values as defaults. Keep derived/computed values inside the function body.

## Rules
1. Parameters = values stated in the problem (e.g., wind speed, emission rate, temperature, pressure, concentrations, distances, angles, rate constants).
2. Derived values (unit conversions, intermediate calculations) stay inside the body.
3. Keep the same return format — dict mapping sub-part id to {{"value": ..., "unit": ...}}.
4. Keep comments. Keep the same computation logic. Do NOT change the math.
5. Use descriptive parameter names matching the variable names already in the code.

## Example
Before:
```python
def solve() -> dict:
    Q = 34    # g/s emission rate
    u = 5     # m/s wind speed
    c = Q / (2 * 3.14159 * u * 24 * 37)
    return {{"1": {{"value": c, "unit": "g/m^3"}}}}
```

After:
```python
def solve(Q=34, u=5, sigma_y=24, sigma_z=37) -> dict:
    import math
    c = Q / (2 * math.pi * u * sigma_y * sigma_z)
    return {{"1": {{"value": c, "unit": "g/m^3"}}}}
```

Write ONLY the refactored Python code. No explanation."""


def refactor_one(solver: dict, config: Config, client: OpenAI) -> dict | None:
    """Refactor one solver. Returns updated solver dict or None on failure."""
    user_msg = REFACTOR_PROMPT.format(code=solver["code"], problem=solver["problem"])

    try:
        resp = client.chat.completions.create(
            model=config.model_id,
            temperature=0.1,
            max_tokens=config.max_tokens,
            messages=[
                {"role": "system", "content": "You are a Python code refactorer. Return ONLY executable Python code."},
                {"role": "user", "content": user_msg},
            ],
        )
        raw = resp.choices[0].message.content
        if not raw:
            return None
    except Exception as e:
        print(f"  LLM error: {e}")
        return None

    # Extract code
    raw = raw.strip()
    import re
    match = re.search(r'```(?:python)?\s*\n(.*?)```', raw, re.DOTALL)
    code = match.group(1).strip() if match else raw

    # Verify: call with no args (defaults) should give same result
    success, results, info = run_solver(code)
    if not success:
        return None

    passed, _ = verify_solver(results, solver["sub_answers"])
    if not passed:
        return None

    # Check that solve() now has parameters (not just `def solve() -> dict:`)
    if "def solve()" in code and "def solve() ->" in code:
        # No parameters added — LLM didn't refactor
        return None

    return {**solver, "code": code}


def main():
    parser = argparse.ArgumentParser(description="Parameterize solvers")
    parser.add_argument("--input", default="data/processed/solvers.json")
    parser.add_argument("--output", default="data/processed/solvers_parameterized.json")
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    config = Config()

    with open(args.input) as f:
        solvers = json.load(f)
    print(f"Loaded {len(solvers)} solvers")

    # Process with thread pool (IO-bound LLM calls)
    results = [None] * len(solvers)
    passed, failed = 0, 0

    def process(idx_solver):
        idx, solver = idx_solver
        client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        result = refactor_one(solver, config, client)
        return idx, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process, (i, s)): i for i, s in enumerate(solvers)}

        for future in concurrent.futures.as_completed(futures):
            idx, result = future.result()
            pid = solvers[idx]["id"]
            if result:
                results[idx] = result
                passed += 1
                print(f"  [{passed+failed}/{len(solvers)}] {pid}: PASS")
            else:
                results[idx] = solvers[idx]  # keep original if refactor fails
                failed += 1
                print(f"  [{passed+failed}/{len(solvers)}] {pid}: FAIL (kept original)")

            # Save periodically
            if (passed + failed) % 50 == 0:
                with open(args.output, "w") as f:
                    json.dump([r for r in results if r], f, indent=2, ensure_ascii=False)

    # Final save
    final = [r for r in results if r]
    with open(args.output, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print("\n=== Done ===")
    print(f"Parameterized: {passed}/{len(solvers)}")
    print(f"Kept original: {failed}")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
