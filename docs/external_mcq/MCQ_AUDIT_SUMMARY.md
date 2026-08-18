# AtmosSci-Bench MCQ quality audit — raw two-model screening (stage 1)

A two-model screening of the external **AtmosSci-Bench** multiple-choice pool as
imported (85 numeric-answer templates / 850 instances — 66 of the official
MCQ10's 67 templates plus 19 from MCQ10_EXT; MCQ_6 carries a non-numeric answer
and was not imported at the time), run with the project's own APIs. Purpose:
quantify how much of the MCQ set is ambiguous, under-specified, or has a wrong
answer key — defects that the multiple-choice format hides but exact-numeric,
execution-based grading exposes.

> **Read together with `docs/results/MCQ_DATASET_AUDIT.md`.** This file reports
> the *raw screening signals*. Raw LLM-auditor flags over-report (a known failure
> mode), so no problem is condemned on them alone: the final adjudication
> intersects both auditors with the blind solve-check and a unit-aware
> confirmation pass, which on the current evaluation set (the official MCQ10,
> N = 670) yields **19 genuinely defective templates (190 problems, 28 %)**, of
> which **9 carry keys two independent solvers contradict**. The funnel — 59
> both-flagged → 21 intersection-flagged (within MCQ10) → 19 confirmed — is the
> point: the pipeline discards over-flagging rather than rubber-stamping it.

## Method

Each of the 85 parent templates was assessed independently by **two frontier
models, GPT-5.4 and Gemini-3.1-Pro** (`pipeline/audit_mcq.py`), on:
- **well_posed** — unambiguous, single correct interpretation;
- **self_contained** — solvable from the text alone (all data / standard constants present);
- **answer_plausible** — the reference answer is physically reasonable.

Separately, a **k2 solve-check** (`pipeline/k2_certify.py`, GPT-5.4 + Claude Opus 4.8)
had two independent models *solve* each template blind; when both agree on a
value that differs from the stored key, the key is contradicted.

A template is **flagged** if a model marks any of the three criteria false or
lists a concrete defect. Consensus = **both** models flag it.

Every instance in `benchmark/external/atmossci_mcq.json` carries an `audit`
field: `{flag: both|one|clean, gpt54:{…}, gemini:{…}, k2_solve:<verdict>}`.

## Raw screening result (stage 1 — before adjudication)

| | templates | % |
|---|---|---|
| flagged by **both** models | **59 / 85** | **69 %** |
| flagged by one model | 19 / 85 | 22 % |
| **clean by both** | **7 / 85** | **8 %** |

Only 8 % of the templates are clean under two independent reviewers — but this is
the *screening* rate, not the defect rate: LLM auditors over-flag, which is why
the pipeline requires the independent solve-check to concur before condemning
anything (see the adjudication note above).

## Consensus defect types (both models agree; a template can carry several)

| consensus defect | templates |
|---|---|
| **ambiguous** (not well-posed) | 34 |
| **not self-contained** (needs an external table/figure/constant) | 28 |
| **answer-key implausible** (wrong magnitude / sign / units) | 11 |

## Independent solve-check (k2)

Over the 85-template pool (in parentheses: restricted to the 66 MCQ10 templates
present at audit time — the scope used in `MCQ_DATASET_AUDIT.md`):

| verdict | templates | meaning |
|---|---|---|
| PASS_K2 | 45 (32) | both blind solutions reproduce the stored key |
| **FAIL_BOTH_AGREE** | **13 (12)** | both agree on a value **≠ the key → key contradicted** |
| REVIEW | 14 (13) | neither reproduces it, and they disagree (hard / ambiguous) |
| PASS_K1 | 13 (9) | only one reproduces the key |

The FAIL_BOTH_AGREE templates are the strongest raw evidence of key errors. Two
of them were later confirmed to be *correct keys in a commensurate unit* (km vs
m) by the unit-aware pass — the value-only solve-check's own false-positive
class, removed at adjudication (`MCQ_DATASET_AUDIT.md` §1.4).

## Worked examples

Worked in full — with the six-model replication — in `docs/results/MCQ_DATASET_AUDIT.md` §2.
The two clearest:
- **MCQ_75** — ground-truth error: key says −3.333 % change in g over
  100,000 km; the inverse-square law gives −99.6 % (the key back-derives from a
  height typo plus a first-order approximation).
- **MCQ_3** — question/answer mismatch: asks for *per-interval* excess
  precipitation but the key stores the *cumulative* series.

## Why this matters (methodological point)

Under multiple choice, a solver selects the *closest listed option*, so an
ambiguous prompt or a wrong key still maps to a "correct letter" and is scored
correct — the defect never surfaces. Requiring the model to emit the **actual
number**, executing its code, and checking it against an **independently
reproduced** ground truth turns "the model got it wrong" into "the answer key /
prompt is wrong." On this set the confirmed damage is substantial: 28 % of the
official MCQ10's templates are defective after conservative adjudication, and on
those problems option-mode accuracy barely moves while code-mode accuracy
collapses (`MCQ_DATASET_AUDIT.md` §4).

## Reproducing

```bash
uv run python -m pipeline.audit_mcq --input benchmark/external/atmossci_mcq.json --model gpt54   --out pipeline/reports/mcq_audit_gpt.json
uv run python -m pipeline.audit_mcq --input benchmark/external/atmossci_mcq.json --model gemini --out pipeline/reports/mcq_audit_gemini.json
# k2 solve-check: pipeline/reports/mcq_k2.json
```

Raw-pool counts in this file recompute from the as-imported 850-instance snapshot
(kept in the maintainers' untracked archive);
per-instance verdicts also travel in the `audit` field of the current 670-problem
`atmossci_mcq.json` (all instances except the later-re-added MCQ_6).
