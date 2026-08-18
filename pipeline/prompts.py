"""All LLM prompts used in the extraction pipeline."""

EXTRACT = """You are an expert atmospheric science educator. Your task is to extract well-defined, self-contained problems from textbook pages.

Extract TWO types of content:

## Type 1: Computational Problems
Problems where specific numerical inputs lead to a calculable numerical answer.
Examples: pollutant concentration, temperature change, wind speed, plume dispersion, mixing ratios, heat flux, etc.

## Type 2: Knowledge Problems
Factual or conceptual questions with objective, verifiable answers.
Examples: "What is the Pasquill-Gifford stability class for wind speed 5 m/s at night with 25% cloud cover?" → Answer: "D"

## Extraction Rules
1. Each problem MUST be **self-contained** — include all necessary equations, constants, and context within the problem text.
2. **Skip** problems that require reading a figure, graph, or diagram that cannot be described in text.
3. **Skip** purely qualitative/essay questions (e.g., "Describe the general circulation").
4. **Skip** "Broaden Knowledge & Comprehension" questions (conceptual).
5. For Sample Applications or worked examples: extract the problem statement and the FINAL answer only (not the solution steps).
6. For homework exercises: extract only those with clear numerical or objective answers.
7. If a problem has multiple sub-parts, keep them together as one problem.
8. Include relevant equations in the problem text if they are needed to solve it.
9. Each problem MUST explicitly state the expected output unit(s). Append "Express your answer in [unit]." at the end of the problem text. For multi-part problems, specify units per sub-part.

## Output Format
Return a JSON array:
```json
[
  {
    "type": "computational" or "knowledge",
    "topic": "short topic label, e.g. gaussian_plume, box_model, thermodynamics",
    "problem": "Full problem statement with all necessary context, equations, and constants",
    "answer": "The final answer with units, or a short factual answer",
    "source_hint": "e.g. Chapter 19 Homework A3, or Chapter 3 Sample Application p.65"
  }
]
```

If the pages contain NO extractable problems, return an empty array: []
Return ONLY the JSON array, no other text."""

EXTRACT_WITH_FIGURE_CHECK = """You are an expert atmospheric science educator. Given the following textbook problem set (one chapter), extract each individual problem.

## Rules
1. Extract each numbered problem (e.g., "1.1 Fog formation", "2.1 Scale height...") as a separate item.
2. If a problem has sub-parts (1, 2, 3...), keep them together as ONE problem.
3. For each problem, determine if it **requires reading a figure, graph, or image** that cannot be fully described in text. Set "requires_figure" accordingly.
4. Include all equations, constants, and context given in the problem text so it is self-contained.
5. Set "chapter" to the chapter number (e.g., "1", "2", "3").
6. Each problem MUST explicitly state the expected output unit(s). Append "Express your answer in [unit]." at the end of the problem text.

## Output Format
Return a JSON array:
```json
[
  {
    "id": "1.1",
    "title": "Fog formation",
    "chapter": "1",
    "problem": "Full problem text with all equations and given values...",
    "requires_figure": false
  }
]
```

Return ONLY the JSON array."""

MATCH_SOLUTION = """You are matching a problem with its solution from a textbook solutions manual.

## Problem
ID: {problem_id}
Title: {problem_title}
Chapter: {chapter}

{problem_text}

## Solutions Text (Chapter {chapter})
{solutions_chunk}

## Task
Find the solution for this specific problem in the solutions text above. Extract:
1. The final numerical answer(s) with units for each sub-part
2. A brief summary of the solution approach (1-2 sentences)

If this problem's solution is NOT found in the provided text, set "found" to false.

## Output Format
Return a JSON object:
```json
{{
  "found": true,
  "answer": "The final answer(s) with units",
  "solution_summary": "Brief description of how to solve it",
  "type": "computational" or "knowledge"
}}
```

Return ONLY the JSON object."""

NORMALIZE = """You are a precise answer parser. Given a problem and its answer, extract every numerical sub-answer.

## Rules
1. Split the answer into individual sub-parts (1, 2, 3, 3.1, 3.2, etc.)
2. For each sub-part, extract ONLY the numerical value(s) with units
3. Skip sub-parts that are purely qualitative (explanations, yes/no, descriptions)
4. If a sub-part has multiple numerical values, list each separately
5. Use scientific notation where appropriate (e.g., 2.7e-6 not 0.0000027)

## Output Format
Return a JSON object:
```json
{
  "sub_answers": [
    {"sub": "1", "value": "5.7", "unit": "pH"},
    {"sub": "2", "value": "5.0", "unit": "pH"}
  ],
  "has_numeric": true
}
```

If there are NO extractable numeric answers at all, return:
```json
{"sub_answers": [], "has_numeric": false}
```

Return ONLY the JSON object."""
