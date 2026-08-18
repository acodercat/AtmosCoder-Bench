"""Clean messy LaTeX in problem texts while preserving meaning exactly.

Usage:
    python -m pipeline.clean_latex
    python -m pipeline.clean_latex --id 11.1
    python -m pipeline.clean_latex --sample 5
"""

import json
import argparse
import tomllib
import concurrent.futures
import threading
from pathlib import Path

from openai import OpenAI

CLEAN_PROMPT = """Clean up the formatting of this atmospheric science problem. Output ONLY the cleaned text.

What to fix:
- Convert messy LaTeX like $k _ {{ 1 }} ~ = ~ 2 . 5 {{ \\bf x }} 1 0 ^ {{ - 1 5 }}$ to clean format like k₁ = 2.5 × 10⁻¹⁵
- Remove unnecessary $...$ wrapping around simple values
- Fix spaced-out numbers like "2 7 0" → "270" and "- 6 . 5" → "-6.5"
- Convert \\mathrm{{K}} \\mathrm{{km}}^{{-1}} to K km⁻¹ or K/km
- Keep LaTeX only for actual equations and formulas that need it

CRITICAL rules:
- Do NOT change the meaning of the problem in any way
- Do NOT change any numerical values
- Do NOT add or remove any information
- Do NOT rephrase sentences — only fix formatting
- Keep the "Express your answer in ..." line exactly as is
- Output ONLY the cleaned problem text

Text to clean:
{problem}"""


def clean_one(problem, client, model_cfg):
    try:
        resp = client.chat.completions.create(
            model=model_cfg["model_id"],
            temperature=0.0,
            max_tokens=80000,
            messages=[{"role": "user", "content": CLEAN_PROMPT.format(problem=problem["problem"])}],
        )
        result = resp.choices[0].message.content
        return problem["id"], result.strip() if result else problem["problem"]
    except Exception:
        return problem["id"], problem["problem"]


def main():
    parser = argparse.ArgumentParser(description="Clean LaTeX in problem texts")
    parser.add_argument("--id", default=None)
    parser.add_argument("--sample", type=int, default=None)
    parser.add_argument("--model", default="gemini")
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    with open(Path("models.toml"), "rb") as f:
        model_cfg = tomllib.load(f)[args.model]
    with open("evals/problems.json") as f:
        problems = json.load(f)

    # Detect messy ones
    messy_indicators = ['{ \\bf x }', '{ \\mathrm {', '~ = ~', '\\mathbf {', '\\mathbf{']
    to_clean = [p for p in problems if any(ind in p['problem'] for ind in messy_indicators) or ('$ ' in p['problem'] and ' $' in p['problem'])]

    if args.id:
        to_clean = [p for p in problems if p['id'] == args.id]
    elif args.sample:
        import random
        random.seed(42)
        to_clean = random.sample(to_clean, min(args.sample, len(to_clean)))

    print(f"Cleaning {len(to_clean)}/{len(problems)} problems...", flush=True)

    by_id = {p['id']: p for p in problems}
    lock = threading.Lock()
    cleaned = 0

    def process(p):
        client = OpenAI(api_key=model_cfg["api_key"], base_url=model_cfg.get("base_url"))
        return clean_one(p, client, model_cfg)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process, p): p for p in to_clean}
        for future in concurrent.futures.as_completed(futures):
            pid, new_text = future.result()
            with lock:
                by_id[pid]["problem"] = new_text
                cleaned += 1
                if cleaned % 50 == 0:
                    print(f"  {cleaned}/{len(to_clean)}", flush=True)
                    with open("evals/problems.json", "w") as f:
                        json.dump(problems, f, indent=2, ensure_ascii=False)

    with open("evals/problems.json", "w") as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)

    print(f"\nDone: cleaned {cleaned} problems", flush=True)


if __name__ == "__main__":
    main()
