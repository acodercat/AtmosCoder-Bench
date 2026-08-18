# AtmosCoder-Bench — Paper-Writing Materials

These documents are the source material for the paper. Every empirical number in a
`results/` doc is regenerable from `experiments/` via the tools in `eval/analysis/`;
every dataset count in `dataset/` is regenerable from `benchmark/`. Files are grouped by
the paper section they feed.

## Layout

| Folder | Purpose | Feeds paper section |
|---|---|---|
| `dataset/` | how the benchmark is built and what it contains | **Dataset / Benchmark Construction** |
| `results/` | empirical findings, one doc per experiment | **Results / Analysis** |
| `evidence/` | verbatim `experiments/` excerpts behind the case discussions | **Supplementary evidence appendices** |
| `external_mcq/` | quality audit of the external AtmosSci-Bench MCQ comparison set | **Motivation / Related benchmarks** |

## Contents

### `dataset/`
- **`DATASET_CONSTRUCTION.md`** — the full Dataset section: execution-grounded construction
  pipeline (source curation → solver synthesis & three-way answer verification →
  parameterization → numeric & paraphrase variants → variant certification → defect
  audit → de-scaffolding → category/difficulty annotation → grading), the composition
  tables (436 core problems, 1,730 numeric + 2,180 paraphrase variants, sources,
  categories, difficulty), and the **trap** diagnostic family, the
  **scaffolding-ablation** paired set, and the external MCQ set.
- **`QUALITY_ASSURANCE.md`** — why the released problems are trustworthy: who proposes a
  problem versus the acceptance gate it has to survive, and the curation cut.
- **`RELIABILITY_ARGUMENT.md`** — a paper-writing aid, not a results doc: how to argue the
  benchmark's reliability, and which objections the evidence does and does not answer.
- **`CONVERGENT_FAILURE_AUDIT.md`** — behavioral QA: mining convergent wrong answers across the
  16 frontier configurations surfaced five repairable defects (all fixed and re-measured) that a
  static LLM convention audit had passed; method, adjudications, and before/after numbers.
- **`EVALUATION_PROMPTS.md`** — every prompt the harness sends, verbatim from `eval/protocols.py`:
  the `code` / `direct` / `agent` system and user prompts, the two repair prompts, and the
  `--system` / `--prompt` ablation presets.

### `results/` (16 models × 3 runs unless noted; numbers cross-verified against the raw result files)
- **`CORE_RESULTS.md`** — core-set leaderboard, code vs. direct protocols, uniform o200k token accounting.
- **`VARIANT_RESULTS.md`** — numeric (contamination) & paraphrase (linguistic) robustness; answer-echo forensics; per-problem contamination verdict.
- **`SCAFFOLDING_ABLATION.md`** — accuracy with vs. without handed-over knowledge (169 paired problems).
- **`PROMPT_SENSITIVITY.md`** — reasoning-permissive vs. code-only prompt ablation.
- **`TRAP_RESULTS.md`** — Trap-Gap diagnostics on the 67-problem trap set.
- **`MCQ_RESULTS.md`** — model accuracy on the external AtmosSci-Bench MCQ set, executable-graded (option mode vs code mode).
- **`MCQ_DATASET_AUDIT.md`** — adjudicated defect audit of that external set, and what it demonstrates about multi-model answer verification.
- **`CODE_VS_DIRECT_CASES.md`** — case studies dissecting the code-vs-direct protocol gap.
- **`FAILURE_CASES.md`** — verified case studies of core problems that defeat most or all configurations.
- **`VARIANT_FAILURE_CASES.md`** — case studies of problems solved in original form but lost under numeric or paraphrase perturbation.
- **`FABRICATION_RESULTS.md`** — process-integrity audit: confirmed cases of models asserting computations they never ran, and why the claim is inert under execution grounding but load-bearing under answer-only grading.
- **`CROSS_DOMAIN_RESULTS.md`** — the same construction method applied to four non-atmospheric environmental domains (131 problems).

### `evidence/`
Verbatim excerpts from `experiments/` behind the case discussions in `results/` — transcripts,
`details` tables and every attempt, nothing summarised. See
[`evidence/README.md`](evidence/README.md) for the file-by-file map and the transcript format.

### `external_mcq/`
- **`MCQ_AUDIT_SUMMARY.md`** — two-model audit of the AtmosSci-Bench MCQ set (answer-key defects exposed by exact-numeric grading).

## Reproducibility

- Results: `uv run python -m eval.analysis.{accuracy,robustness,echo_forensics,token_count,...}`.
- Dataset facts: `benchmark/README.md` (dataset card) and `benchmark/*.json`.
- Archived, superseded docs (e.g. the former `DATASET_SECTION.md`, `TRAP_DESIGN.md`, and the
  stale `DATASET_OVERVIEW.md` / `KNOWLEDGE_TAXONOMY.md`) are kept in an untracked local archive.
