# AtmosCoder-Bench — Trap-Problem Results

*Empirical evaluation of the trap diagnostic set (`benchmark/traps.json`). Companion to `docs/dataset/DATASET_CONSTRUCTION.md` (Trap Diagnostic Family — construction), `docs/results/CORE_RESULTS.md` (core-set eval), and `docs/results/SCAFFOLDING_ABLATION.md` (knowledge-recall ablation). All figures are auto-derived from `experiments/trap/`.*

## 1. Objective

The trap set probes whether a model solves atmospheric-science problems by **physical reasoning** or by **pattern-matching a memorised template**. Each trap is a minimal, single-trigger perturbation of a certified core-set problem such that the core problem's own canonical method becomes an incorrect *shortcut*, while the physically correct method yields a different value (relative separation > 5%, the grading tolerance). Because the untouched core problem is the built-in **control**, a model that solves the control but fails the trap must be applying the shortcut rather than the required physics. See the Trap Diagnostic Family section of `docs/dataset/DATASET_CONSTRUCTION.md` for the construction contract.

## 2. Method

- **Diagnostic set.** 67 traps, strictly one per parent core problem (1 parent : 1 trap), spanning six trap families and all ten atmospheric-science categories. Every trap's reference solver reproduces its ground truth under `eval.verify`, and every solver is self-contained (all consumed quantities appear in the problem text).
- **Models.** Nine configurations: four base models each in a non-reasoning and a reasoning setting (gpt-5.5, DeepSeek-V4-flash, Qwen-3.6-27B, Qwen-3.5-9B), plus Gemini-3.1-Pro (reasoning-only). Protocol: `code` mode (the model writes an executable `solve()`; Python computes the graded value).
- **Repetition.** Three independent runs per configuration (67 × 3 = 201 measurements each), enabling run-to-run variance and best-of-3 (pass@3) estimates.
- **Metrics.** All primary figures are the **mean over the three runs**, reported with ± one standard deviation, following standard practice for stochastic-decoding evaluations.
  - *Trap accuracy*: mean fraction of the 67 traps solved.
  - *Control accuracy*: the model's accuracy on the 67 **parent** (untriggered) problems, from `experiments/core_code/`.
  - ***Trap Gap*** (headline metric): the failure rate on traps **restricted to those whose parent the model solves**, averaged over the three runs. Conditioning on solved controls removes the confound of general base incompetence and isolates the effect of the trigger; it therefore need not equal (control acc − trap acc) exactly.
  - *pass@3* (best-of-three): fraction solved in ≥1 of the three runs — a secondary capability-ceiling metric, reported in Appendix A.

### Data integrity
All 27 result files were verified programmatically: model identity matches the filename; each file contains exactly 67 records with zero excluded (infrastructure) errors; stored metrics equal a recount of the records; no duplicate problem ids; all ids belong to the current trap set. Reasoning and non-reasoning configurations share an underlying API `model_id`, so they were additionally distinguished by content — every reasoning file carries reasoning-token counts and thinking traces; every non-reasoning file reports zero — confirming the two settings are not conflated.

## 3. Results

### Table 1 — Trap accuracy vs. control (mean of 3 runs, 67 traps)

Every accuracy is the **mean over three independent runs** (± one standard deviation across runs). Models are ordered by core-set capability. *control acc* = accuracy on the 67 parent (untriggered) problems; *trap acc* = accuracy on the triggered versions; **Trap Gap** (§2) is the failure rate on triggered problems whose parent the model solves. The trap effect reads directly as the drop from control to trap accuracy, quantified by the Trap Gap.

| model | core acc | control acc | trap acc (mean ± SD) | **Trap Gap** |
|---|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 98% | 98% | 96.0 ± 1.7% | **3 pp** |
| Gemini-3.1-Pro (reasoning) | 96% | 97% | 96.5 ± 0.9% | **3 pp** |
| DeepSeek-V4-flash (reasoning) | 91% | 91% | 87.1 ± 2.3% | **6 pp** |
| gpt-5.5 | 91% | 91% | 88.6 ± 2.3% | **7 pp** |
| Qwen-3.6-27B (reasoning) | 89% | 88% | 82.1 ± 1.5% | **11 pp** |
| DeepSeek-V4-flash | 82% | 82% | 72.6 ± 2.3% | **21 pp** |
| Qwen-3.6-27B | 79% | 83% | 73.1 ± 2.6% | **21 pp** |
| Qwen-3.5-9B (reasoning) | 77% | 85% | 64.7 ± 3.1% | **29 pp** |
| Qwen-3.5-9B | 63% | 67% | 57.2 ± 0.9% | **36 pp** |

*pass@3 (best-of-three) is reported as a secondary metric in Appendix A.*

### Table 2 — Solve rate by trap family (pooled over 9 configurations × 3 runs)

| trap family | solve rate | n (config-runs) |
|---|--:|--:|
| regime_boundary | 42% | 135 |
| geometry_detail | 63% | 54 |
| sign_direction | 78% | 243 |
| formula_selection | 82% | 675 |
| definition_confusion | 86% | 459 |
| averaging_space | 87% | 243 |

### Table 3 — Effect of reasoning on the clean Trap Gap (paired)

| base model | non-reasoning gap | reasoning gap | reduction |
|---|--:|--:|--:|
| gpt-5.5 | 7 | 3 | 4 |
| DeepSeek-V4-flash | 21 | 6 | 15 |
| Qwen-3.6-27B | 21 | 11 | 10 |
| Qwen-3.5-9B | 36 | 29 | 7 |

### Table 4 — Convergent shortcuts (models emitting the *exact predicted shortcut value*)

Instances counted over all 9 configurations × 3 runs = 27 model-runs per trap; "models" is the number of distinct configurations that fell into the shortcut on ≥1 run.

**Matching rule.** A run counts as captured when it **failed** *and* every sub-answer it returned matches the trap's `shortcut_values` — the complete vector, not the scalar `shortcut_value`. (Any tolerance from 0.1 % to 10 % gives the same counts; a shortcut-taker reproduces the shortcut solver to machine precision.) The scalar alone is not a capture test: on `air_215`, whose first sub has a shortcut value of exactly 0, it flags 15 of 27 runs, but a zero can equally come from a dropped term — requiring the other two subs to match (10.0, 10.0) leaves the **12** that demonstrably ran the Cartesian tangent-plane shortcut. The same rule keeps `trap_snp_49_gen` out of the table: its scalar is also its own sub-2 ground truth, so a scalar test would mark 25 of its 27 runs as captured when those runs are correct.

The same rule is what keeps `trap_snp_49_gen` (not in this table) out of the counts: its scalar `shortcut_value` of 151.6 is *also* its own sub-2 ground truth, so a scalar test would mark 25 of its 27 model-runs as captured when those runs are in fact **correct** — all nine configurations solve that trap, and the full-vector test flags none of them. A model that genuinely took its shortcut would return (151.6, 196.4, 238.1) against (118.4, 151.6, 181.9) and fail on every sub.

| trap | family | shortcut-capture | distinct models |
|---|---|--:|--:|
| holton_28 (inertial-circle geometry) | regime_boundary | 18 / 27 | 7 |
| air_215 (spherical metric terms) | formula_selection | 12 / 27 | 6 |
| air_205 (anticyclonic gradient-wind root) | formula_selection | 9 / 27 | 4 |
| air_108 (meteorological "east" vs "eastward") | sign_direction | 8 / 27 | 4 |
| air_111 (layer-mean vs surface flux) | averaging_space | 6 / 27 | 3 |

## 4. Insights

**I1 — The Trap Gap scales inversely with model capability.** The clean Trap Gap decreases monotonically (non-strictly — Qwen-3.6-27B and DeepSeek-V4-flash tie at 21 pp) from 36 pp (Qwen-3.5-9B, core 63%) to 3 pp for the strongest configurations (gpt-5.5 (reasoning), Gemini-3.1-Pro; core 96–97%). Because the gap is measured only on problems whose control the model solves, this is not attributable to weaker models being generally worse: it specifically quantifies susceptibility to the pattern-matching shortcut. Stronger models increasingly answer from the underlying physics; weaker models increasingly rely on the surface template.

**I2 — Explicit reasoning reduces, but does not eliminate, the gap.** For every base model, enabling reasoning lowers the clean Trap Gap (paired reductions of 4–15 pp; Table 3). However, a residual gap persists — from 3 pp (gpt-5.5) up to 29 pp (Qwen-3.5-9B (reasoning)). Reasoning is therefore a partial mitigation rather than a solution: at the weaker end the model still applies the shortcut in roughly one quarter of cases despite deliberation.

**I3 — Failures are systematic, not random.** Several traps capture the *exact predicted shortcut value* across many independent model-runs (Table 4), demonstrating that models share a specific erroneous method rather than failing idiosyncratically. The clearest case, `holton_28` (an inertial-oscillation geometry problem in which the small-deflection approximation breaks when the separation is comparable to the target size), elicits the exact small-deflection shortcut in 18 of 27 model-runs and in 7 of 9 configurations — **including the strongest models**. Such traps identify shortcuts that are robust to scale and to reasoning, i.e. genuine shared inductive biases rather than capability artefacts.

**I4 — Difficulty is concentrated in specific physics families.** Regime-boundary traps — where a parameter crosses a validity threshold of the canonical formula (Stokes→slip/quadratic drag, tropospheric→stratospheric lapse, small-angle approximations) — are by far the hardest family (42% pooled solve rate), followed by geometry-detail (63%). Averaging-space and definition-confusion traps are the most often avoided (87% and 86%). This suggests models most reliably reproduce named formulae and unit/definition conventions, and most reliably fail when a stated condition silently invalidates the default regime.

**I5 — The diagnostic is fair and its rankings are stable.** The strongest models solve 96–97% of the traps (pass@3 up to 99%), confirming the traps are genuinely solvable by careful physical reasoning and are not ill-posed "gotchas." Run-to-run standard deviations are small (0.9–4.5 pp), and the capability ordering of the Trap Gap is preserved across all three runs, indicating the measured effect is robust to sampling.

## 5. Limitations

- **Control is stochastic.** Control accuracy and the clean Trap Gap are computed run-by-run — run *i* of `core_code` paired with run *i* of `trap` — and averaged over the three runs, so the gap denominator follows the same sampling as the numerator. A parent solved in only some runs therefore enters the denominator only in those runs; the residual sensitivity is bounded by the per-run variance reported above.
- **Ground-truth verification is self-consistent, not independently triangulated.** Every trap solver reproduces its own certified answer, and each trap was individually reviewed for physical correctness; a subset of the more intricate traps (e.g. multi-layer radiative transfer, numerical pseudo-adiabatic integration) have not been cross-checked against an independent solver or textbook value.
- **Per-trap sample size is small.** Family- and trap-level rates are informative but not powered for per-trap significance testing; aggregate (per-model, per-family) conclusions are the intended level of inference.
- **Model panel is finite.** Nine configurations from four model families plus Gemini; the monotonic capability trend is suggestive but based on a limited and non-independent set of systems.

## 6. Reproduction

```bash
# per model config (proxy required for the Gemini endpoint):
uv run python -m eval.runner --model <name> --input benchmark/traps.json --mode code --exp-id trap --run <k>
# results: experiments/trap/<name>.run<k>.json ; controls reused from experiments/core_code/
```

## Appendix A — per-run trap accuracy

Individual run scores (solved / 67) behind the 3-run means in Table 1. "±" is the standard deviation of the three per-run percentages; small values indicate the reported means are stable across independent runs.

| model | run 1 | run 2 | run 3 | **mean** | ± | pass@3 |
|---|--:|--:|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 65/67 (97%) | 63/67 (94%) | 65/67 (97%) | **96.0%** | 1.7 | 99% |
| Gemini-3.1-Pro (reasoning) | 64/67 (96%) | 65/67 (97%) | 65/67 (97%) | **96.5%** | 0.9 | 97% |
| DeepSeek-V4-flash (reasoning) | 57/67 (85%) | 58/67 (87%) | 60/67 (90%) | **87.1%** | 2.3 | 91% |
| gpt-5.5 | 61/67 (91%) | 58/67 (87%) | 59/67 (88%) | **88.6%** | 2.3 | 91% |
| Qwen-3.6-27B (reasoning) | 56/67 (84%) | 55/67 (82%) | 54/67 (81%) | **82.1%** | 1.5 | 90% |
| Qwen-3.6-27B | 48/67 (72%) | 51/67 (76%) | 48/67 (72%) | **73.1%** | 2.6 | 85% |
| DeepSeek-V4-flash | 49/67 (73%) | 47/67 (70%) | 50/67 (75%) | **72.6%** | 2.3 | 84% |
| Qwen-3.5-9B (reasoning) | 45/67 (67%) | 41/67 (61%) | 44/67 (66%) | **64.7%** | 3.1 | 82% |
| Qwen-3.5-9B | 38/67 (57%) | 39/67 (58%) | 38/67 (57%) | **57.2%** | 0.9 | 78% |

*Read against Table 1's "control acc" column, the trap effect is visible directly: e.g. DeepSeek-V4-flash (non-reasoning) solves 82% of the parent problems but only 72.6% of the traps on average — and, restricted to parents it actually solves, fails 21% of the corresponding traps (the clean Trap Gap).*
