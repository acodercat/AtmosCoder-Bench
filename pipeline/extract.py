"""
Extract atmospheric science problems from textbook PDFs.

Pipeline: PDF → MinerU API (markdown) → LLM (extract problems) → JSON

Usage:
    uv run python extract.py book.pdf                          # single PDF
    uv run python extract.py                                   # all PDFs in sources/pdfs/
    uv run python extract.py --mode match-solutions \\
        --problems "sources/pdfs/IAC/problem*.pdf" \\
        --solutions "sources/pdfs/IAC/solutions.pdf"
    uv run python extract.py --mode normalize
"""

import json
import os
import glob
import time
import argparse

from openai import OpenAI

from . import prompts
from .config import Config
from .pdf import (
    pdf_to_markdown, call_llm, parse_json_array, parse_json_object,
    chunk_by_lines, chunk_by_sections,
)


# ── Extract: PDF with answers inline ──

def cmd_extract(pdf_paths: list[str], config: Config, client: OpenAI, output_dir: str):
    all_problems = []
    for pdf_path in pdf_paths:
        book_title = os.path.basename(pdf_path).replace(".pdf", "")
        print(f"\nProcessing: {book_title}")
        md = pdf_to_markdown(pdf_path, config, output_dir)
        if not md:
            continue
        for label, content in chunk_by_lines(md):
            print(f"  [LLM] {label}...", end=" ", flush=True)
            user_msg = (
                f"Extract problems from the following textbook pages.\n\n"
                f"Book: {book_title}\nSection: {label}\n\n"
                f"--- CONTENT START ---\n{content}\n--- CONTENT END ---"
            )
            raw = call_llm(client, config, prompts.EXTRACT, user_msg)
            problems = parse_json_array(raw)
            for p in problems:
                p["book"] = book_title
            print(f"found {len(problems)} problems")
            all_problems.extend(problems)
            time.sleep(2)

    out_path = os.path.join(output_dir, "extracted_problems.json")
    with open(out_path, "w") as f:
        json.dump(all_problems, f, indent=2, ensure_ascii=False)
    comp = sum(1 for p in all_problems if p.get("type") == "computational")
    print(f"\n=== Done: {len(all_problems)} problems ({comp} computational) → {out_path} ===")


# ── Match: separate problem/solution PDFs ──

def _get_solutions_for_chapter(solutions_md: str, chapter: str) -> str:
    lines = solutions_md.split("\n")
    chapter_int = int(chapter) if chapter.isdigit() else chapter
    target = f"chapter {chapter_int}"
    start, end = None, None
    for i, line in enumerate(lines):
        lower = line.lower().strip()
        has_chapter_marker = lower.startswith("#") or "solution" in lower
        if target in lower and has_chapter_marker and start is None:
            start = i
        elif start is not None and "chapter" in lower and target not in lower and has_chapter_marker:
            end = i
            break
    return "\n".join(lines[start:end]) if start is not None else ""


def cmd_match_solutions(problem_glob: str, solutions_path: str, config: Config, client: OpenAI, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    solutions_key = os.path.basename(solutions_path).replace(".pdf", "")
    markdowns = {}
    for pdf_path in sorted(glob.glob(problem_glob)) + [solutions_path]:
        name = os.path.basename(pdf_path).replace(".pdf", "")
        md = pdf_to_markdown(pdf_path, config, output_dir)
        if md:
            markdowns[name] = md

    solutions_md = markdowns.get(solutions_key, "")
    if not solutions_md:
        print(f"ERROR: {solutions_key}.pdf not parsed")
        return

    # Extract problems
    print("\n=== Extracting problems ===")
    all_problems = []
    for name, md in sorted(markdowns.items()):
        if name == solutions_key:
            continue
        for chunk in chunk_by_sections(md):
            print(f"  [LLM] {name}...", end=" ", flush=True)
            raw = call_llm(client, config, prompts.EXTRACT_WITH_FIGURE_CHECK,
                           f"Extract problems from this chapter:\n\n{chunk}")
            problems = parse_json_array(raw)
            print(f"found {len(problems)}")
            all_problems.extend(problems)
            time.sleep(2)

    text_problems = [p for p in all_problems if not p.get("requires_figure", False)]
    print(f"\nTotal: {len(all_problems)}, text-only: {len(text_problems)}")

    # Match
    print("\n=== Matching to solutions ===")
    results = []
    for p in text_problems:
        chapter = p.get("chapter", "")
        print(f"  Matching {p.get('id', '?')}...", end=" ", flush=True)
        sol_chunk = _get_solutions_for_chapter(solutions_md, chapter) or solutions_md
        user_msg = prompts.MATCH_SOLUTION.format(
            problem_id=p.get("id", ""), problem_title=p.get("title", ""),
            chapter=chapter, problem_text=p["problem"], solutions_chunk=sol_chunk,
        )
        match = parse_json_object(
            call_llm(client, config, "You are a precise answer extractor. Return ONLY valid JSON.", user_msg)
        )
        if match.get("found"):
            results.append({
                "id": p.get("id", ""), "title": p.get("title", ""), "chapter": chapter,
                "type": match.get("type", "computational"), "problem": p["problem"],
                "answer": match["answer"], "solution_summary": match.get("solution_summary", ""),
                "book": os.path.basename(os.path.dirname(solutions_path)),
            })
            print(f"matched → {match['answer'][:60]}")
        else:
            print("not found")
        time.sleep(2)

    out_path = os.path.join(output_dir, "extracted_problems.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n=== Done: {len(results)}/{len(text_problems)} matched → {out_path} ===")


# ── Normalize: split answers into numeric sub-answers ──

def cmd_normalize(input_paths: list[str], output_path: str, config: Config, client: OpenAI):
    all_problems = []
    for path in input_paths:
        with open(path) as f:
            problems = json.load(f)
        print(f"  Loaded {len(problems)} from {path}")
        all_problems.extend(problems)
    print(f"Total: {len(all_problems)} problems")

    results, skipped = [], 0
    for i, p in enumerate(all_problems):
        pid = p.get("id", f"p_{i}")
        print(f"  [{pid}]...", end=" ", flush=True)
        user_msg = f"Problem: {p['problem']}\n\nAnswer: {p.get('answer', '')}"
        parsed = parse_json_object(call_llm(client, config, prompts.NORMALIZE, user_msg))
        if not parsed.get("has_numeric") or not parsed.get("sub_answers"):
            print("no numeric → skip")
            skipped += 1
            continue
        print(f"{len(parsed['sub_answers'])} numeric answers")
        entry = {
            "id": pid,
            "book": p.get("book", ""),
            "problem": p["problem"],
            "original_answer": p.get("answer", ""),
            "sub_answers": parsed["sub_answers"],
        }
        # Only include non-empty optional fields
        for key in ("title", "chapter", "solution_summary"):
            val = p.get(key, "")
            if val:
                entry[key] = val
        results.append(entry)
        time.sleep(1)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    total_subs = sum(len(r["sub_answers"]) for r in results)
    print(f"\n=== Done: {len(results)} problems, {total_subs} sub-answers → {output_path} ===")


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(description="AtmosCoder-Bench: extract problems from textbook PDFs")
    parser.add_argument("pdfs", nargs="*", help="PDF file(s) to process")
    parser.add_argument("--mode", choices=["extract", "match-solutions", "normalize"], default="extract")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--problems", help="Glob for problem PDFs (match-solutions mode)")
    parser.add_argument("--solutions", help="Solutions PDF path (match-solutions mode)")
    parser.add_argument("--inputs", nargs="*", help="Input JSON files (normalize mode)")
    args = parser.parse_args()

    config = Config()
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    output_dir = args.output or config.output_dir
    os.makedirs(output_dir, exist_ok=True)

    if args.mode == "normalize":
        input_paths = args.inputs or sorted(glob.glob(os.path.join(output_dir, "**/*.json"), recursive=True))
        cmd_normalize(input_paths, os.path.join(output_dir, "validated_problems.json"), config, client)
    elif args.mode == "match-solutions":
        if not args.problems or not args.solutions:
            parser.error("--problems and --solutions required")
        cmd_match_solutions(args.problems, args.solutions, config, client, output_dir)
    else:
        pdf_files = args.pdfs or sorted(glob.glob(os.path.join(config.materials_dir, "**/*.pdf"), recursive=True))
        if not pdf_files:
            print(f"No PDFs found in {config.materials_dir}")
            return
        print(f"Found {len(pdf_files)} PDF(s)")
        cmd_extract(pdf_files, config, client, output_dir)


if __name__ == "__main__":
    main()
