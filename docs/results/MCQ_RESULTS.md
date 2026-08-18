# AtmosCoder-Bench — MCQ Results

External MCQ set: the official **AtmosSci-Bench MCQ10 (N = 670)** — 67 templates × 10 symbolic-perturbation instances (`benchmark/external/atmossci_mcq.json`). Evaluated two ways:

- **Code mode** — the AtmosCoder protocol: the model writes a `solve()` function whose numeric output is graded at 5 % relative tolerance (the option list is *not* shown). Accuracy = passed / (passed + failed); every run finished with 0 errors (the self-repair loop cleared all format/execution failures).
- **Option mode** — the source AtmosSci-Bench protocol: the model sees the four options and answers with a letter, graded on `\boxed{A/B/C/D}` (MCQEvaluator, source framework). 670/670 responses, 0 null, for every reported model.

Both modes run over the identical 670-problem set, so code and option are strictly paired and directly comparable to the published AtmosSci-Bench MCQ10 numbers.

> **Dataset caveat.** A multi-model audit of this external set found 19 genuinely defective templates within MCQ10 (190 problems), 9 with keys two independent solvers contradict; see `MCQ_DATASET_AUDIT.md` for the audit, examples, and clean-subset (N = 480) numbers. Tables below use the full 670 unless noted.
>
> **Excluded model.** DeepSeek-V4-flash-reasoning is excluded from both modes. Its option run was invalid: 201/850 responses (in the pre-restriction 850 run) were empty because the thinking chain consumed the entire 16,384-token generation budget (`reasoning_tokens = 16384` on every one of them), leaving zero tokens for the answer; the source evaluator silently scores these truncations as wrong. With no valid option arm, its code arm is dropped too so the paired comparison stays symmetric.

## Table 1 — Code mode (write and execute a solver)

| Model | Reasoning | Accuracy | Passed / Graded | Output tok/problem* |
|---|:---:|---:|---:|---:|
| gemini-3.1-pro | Y | 60.0% | 402 / 670 | 327 (+ hidden thinking) |
| deepseek-r1 | Y | 53.0% | 355 / 670 | 1,261 |
| gpt-5.5 | N | 49.6% | 332 / 670 | 358 |
| deepseek-v4-flash | N | 43.3% | 290 / 670 | 638 |
| deepseek-v3 | N | 27.2% | 182 / 670 | 305 |
| qwen-2.5-72b | N | 19.3% | 129 / 670 | 447 |

\* o200k recount of stored response text across all attempts (self-repair included).

**Tolerance robustness (± 5 % → ± 10 % → ± 20 %).** Re-grading each run at looser tolerances with the unit-aware offline re-grader (`eval.analysis.accuracy`, which replays the runner's full grading rule from stored per-sub values and units; verified to reproduce the runner's 5 % pass counts exactly on all 220 result files):

| Model | ± 5% | ± 10% | ± 20% | 5→20 gain |
|---|--:|--:|--:|--:|
| gemini-3.1-pro | 60.0% | 61.0% | 61.9% | +1.9 |
| deepseek-r1 | 53.0% | 54.6% | 55.7% | +2.7 |
| gpt-5.5 | 49.6% | 50.6% | 53.0% | +3.4 |
| deepseek-v4-flash | 43.3% | 44.0% | 45.8% | +2.5 |
| deepseek-v3 | 27.2% | 28.1% | 29.6% | +2.4 |
| qwen-2.5-72b | 19.3% | 20.0% | 21.9% | +2.7 |

Quadrupling the tolerance moves accuracy by only 1.9–3.4 points and leaves the ranking unchanged. The failures are therefore **not** tolerance artifacts (answers that landed just outside 5 %) — they are substantive derivation errors, consistent with the ~100 % median error of code failures documented in the mechanism analysis below. The 5 % headline is not a knife-edge.

## Table 2 — Option mode vs code mode (all 670 problems, every model we ran in code)

Every model from Table 1, with its option-mode accuracy alongside. The three models we ran in option mode ourselves use our in-house numbers (strictly paired — same 670 set, same grader); the other three use the option accuracy published by the AtmosSci-Bench authors on the same MCQ10 set. Both option sources are on N = 670.

| Model | Reasoning | Option (pick A/B/C/D) | Code (compute the number) | Δ (option − code) | Option source |
|---|:---:|--:|--:|--:|:---|
| gemini-3.1-pro | Y | 94.5% (633/670) | 60.0% | **+34.5** | in-house |
| deepseek-r1 | Y | 88.51% | 53.0% | **+35.5** | paper ‡ |
| gpt-5.5 | N | 80.1% (537/670) | 49.6% | **+30.6** | in-house |
| deepseek-v4-flash | N | 88.1% (590/670) | 43.3% | **+44.8** | in-house |
| deepseek-v3 | N | 63.28% | 27.2% | **+36.1** | paper ‡ |
| qwen-2.5-72b | N | 57.01% | 19.3% | **+37.8** | paper ‡ |

Every model scores **+30 to +45 points** higher when picking a letter than when computing the answer, on the identical problems.

‡ Paper option numbers: Chen et al., *AtmosSci-Bench* (arXiv:2502.01159; NeurIPS 2025 D&B), Table 2, overall accuracy on MCQ10 (N = 670), models `DeepSeek-R1`, `DeepSeek-V3`, `Qwen2.5-72B-Instruct-Turbo`. Our code runs use `deepseek/deepseek-r1`, `deepseek/deepseek-chat`, `qwen/qwen-2.5-72b-instruct` on the identical 670-problem set. **The three in-house rows are the strictly paired result** (same set, same grader, both modes run here); the three paper rows are cross-source corroboration — the option side uses the authors' letter-match grader rather than our 5 %-tolerance numeric check, and the paper gives no versioned API identifiers, so serving-stack differences cannot be fully excluded. That the two kinds of row land in the same +30–45 band is itself the point: the inflation is not an artifact of our harness.

## Findings

**1. Multiple-choice inflates measured competence by 30–45 points.** Every dual-mode model scores dramatically higher when allowed to pick a letter than when required to compute the answer to the *same* problems. Option-mode accuracy saturates (80–95 %) where code-mode accuracy still spreads the field (43–60 %).

**2. The inflation replicates against independently published numbers, and is strikingly uniform.** The three Table 2 rows whose option side comes from the AtmosSci-Bench paper (R1, V3, Qwen2.5-72B) all inflate by essentially the same amount — +35.5, +36.1, +37.8, a spread of only 2.3 points — despite spanning a reasoning model (R1, 88.5 % option as published), a chat model (V3, 63.3 %) and an open-weight 72-B (Qwen2.5, 57.0 %). The penalty for removing the options is close to constant across a 31-point span of option-mode ability, and it sits inside the same +30–45 band as the three in-house paired rows. This is not an artifact of our harness: those option numbers are the original authors' own measurement.

**3. MCQ does not just inflate — it re-ranks models.** DeepSeek-V4-flash beats gpt-5.5 by 8 points in option mode (88.1 vs 80.1) but *loses* to it by 6.6 points in code mode (43.0 vs 49.6). A leaderboard built on option accuracy would order these two models incorrectly with respect to their actual quantitative ability.

**4. Selection without derivation, quantified.** Cross-tabulating the two modes per problem: of the problems a model *cannot compute* (code-mode fail), it nonetheless picks the correct letter 66–89 % of the time — against a 25 % random baseline:

| Model | Both correct | Only option correct | Only code correct | Both wrong | Code-fail rescued by options |
|---|--:|--:|--:|--:|--:|
| gemini-3.1-pro | 395 | 238 | 7 | 30 | 238/268 = **89%** |
| deepseek-v4-flash | 281 | 309 | 9 | 71 | 309/380 = **81%** |
| gpt-5.5 | 314 | 223 | 18 | 115 | 223/338 = **66%** |

The options themselves carry most of the signal: elimination, back-substitution, and plausibility ranking let a model "solve" problems it demonstrably cannot derive. The converse cell is tiny (7–18 problems computed correctly but mis-selected), confirming the asymmetry is real shortcut usage, not noise.

**5. Option mode is also *more expensive*, not just easier.** Per problem, answering by letter consumes more output tokens than writing a solver (same model, same problems), because prose elimination reasons through all four options where code states one derivation:

| Model | Code output tok/problem† | Option output tok/problem† | Ratio |
|---|--:|--:|--:|
| gemini-3.1-pro | 1,793 (327 visible + thinking) | 2,812 | 1.6× |
| deepseek-v4-flash | 638 | 1,402 | 2.2× |
| gpt-5.5 | 358 | 466 | 1.3× |

† Both columns are the model's full output budget, thinking included. The code side is the repo's own o200k recount of the stored text throughout: for gemini it is completion + reasoning over the 670 problems (327 visible + 1,466 thinking = 1,793 per problem, i.e. the same 1,412,349 − 210,927 prompt that the provider reports for this run); the two non-thinking models store no reasoning text, so their code figure is the recount of the stored `solve()` text alone. The deepseek-v4-flash figure was previously quoted as 709, which was that provider's own count rather than the recount used everywhere else in this table; it is 638 on the uniform basis, which raises its ratio from 2.0× to 2.2×.

So the code protocol is simultaneously the **stricter** measurement (no option shortcuts), the **cheaper** one (fewer output tokens), and the more **operationally robust** one on this benchmark's runs (the one truncation collapse observed — DeepSeek-V4-flash-reasoning — happened in option mode, where the source framework has no repair loop; the code protocol's self-repair loop cleared every format/execution failure, 0 errors across all six models).

**6. Reasoning still dominates code mode.** Within the DeepSeek family, R1 (reasoning) beats V3 (chat) by +25.8 points (53.0 vs 27.2); the overall code-mode top two are the two reasoning models. Computing the answer is exactly the regime where chain-of-thought pays, and where a 72-B open-weight chat model (19.3 %) is exposed.

## Why does code fail where option succeeds? — a mechanism analysis

Finding 4 counts the "rescue" cells (code fails, option succeeds); this section dissects *why*, restricted to the **clean 480** (genuinely-defective templates excluded, so the key is correct and a code failure is a real failure). Clean rescue cases: 94 (gemini), 166 (deepseek-v4-flash), 113 (gpt-5.5).

**These are not near-misses.** If option mode merely rescued computations that landed just outside the 5 % tolerance, the story would be uninteresting. It does not: **88/94, 146/166, 105/113** of the clean rescues are genuine derivation failures — the code answer is off by **>15 %, with a median relative error of ~100 %** (i.e. wrong by a factor of two or more, a dropped term, or a sign error). Only 6–14 per model are tolerance near-misses (the remaining 6 for DeepSeek-V4-flash never produced a runnable answer). The model that "passes" in option mode has, when forced to compute, produced a badly wrong number.

Three mechanisms account for the rescues:

**1. Snap-to-nearest-option — the model derives the *same wrong value* in both modes, then picks the closest listed choice.** This is the most directly evidenced mechanism, because it can be caught verbatim in the response. Direct proof: in **29 % of far-wrong single-sub rescues (42 % for deepseek-v4-flash, 27 % for gpt-5.5, 7 % for gemini-3.1-pro; 51 of 175 pooled), the code's wrong value literally reappears in the option-mode response** — the model computed the same number, saw it was not an option, and snapped to the nearest one. The rate is strongly model-dependent: gemini's low share reflects that it far-misses on only 41 single-sub rescues in the first place. The clearest instance, gpt-5.5 on **MCQ_13_5** (pressure-tendency from a moving ship):

> *"= −606.9 − 1191.4 ≈ **−1798.3 Pa/h**. This value is not listed among the options. However, … the closest listed physically reasonable option is **−584.5 Pa/h**."* → `\boxed{A}`, graded **correct**.

In code mode the identical derivation returns −1798.28 against a key of −584.5 → a 208 % error → **FAIL**. The model never derived −584.5 in either mode; the option list simply contained it, and the model matched to it. Selection substituting for derivation, verbatim.

**2. Grading-surface asymmetry on multi-part problems.** ~50 % of clean rescues are multi-sub problems, and in **~62 % of those the code got at least one sub-answer right** (64 % gemini, 60 % flash, 65 % gpt-5.5). Code mode requires *every* asked quantity within tolerance; the single option letter is keyed to one headline value. A model that nails 3 of 4 sub-answers but blows the 4th fails the whole problem in code mode, yet its one-letter option answer is scored correct. This is a coarser grading surface, not better reasoning.

**3. Tolerance near-miss (minor).** The 6–14 residual cases per model are computations just outside 5 % that round to the keyed option.

**Upshot.** Option-mode "rescue" is accounted for by (1) snapping a wrong derivation onto the nearest of four printed numbers — demonstrable verbatim in 51 of the 175 far-wrong single-sub rescues (14 % of all 373 clean rescues, and up to 42 % of one model's single-sub far-misses) — and (2) a one-letter grading surface that hides partial-answer failures, the larger bucket at ~32 % of all clean rescues. Neither reflects the model being able to *compute* the answer. The rescues are not latent competence the code protocol misses; they are the option format supplying the answer the model could not derive. This is the mechanistic core of Findings 1–4: MCQ measures recognition-among-given-choices, code measures derivation.

*Recompute: clean rescue set = code-fail ∧ option-pass ∧ not on a genuinely-defective template (the 19-template / 190-problem set, unit-expression false positives excluded); error bins from stored `details` (expected vs actual per sub); value-reappearance test matches the code sub-answer against all numbers parsed from the option response — plain, scientific and LaTeX `\times 10^{n}` forms — within 2 % (raising the match tolerance to 5 % moves the pooled rate 29 % → 31 %).*

---

*Set note: our 670 = the official MCQ10. Every answer is a solver-computed numeric target (the AtmosSci-Bench MCQ answer parsed into `{value, unit}` sub-answers). One template, MCQ_6, carries two non-numeric sub-answers (flow-type classifications) that numeric grading cannot score; it is graded on the two explicitly-requested numeric quantities (discharge, inlet velocity). All code runs use the current system prompt ("You are an expert in atmospheric science."). Pre-restriction 850-problem originals and the old-prompt code arm are archived under `backups/mcq_850_pre670_20260721/` and `experiments/_mcq_code_oldprompt850/`.*
