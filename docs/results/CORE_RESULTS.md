# AtmosCoder-Bench — Core-set Results (code & direct protocols)

*436 problems, 3 runs per model. Code mode: 0 excluded errors. Direct mode: no excluded errors — 7 protocol non-completions (gpt-5.5 (reasoning)) are counted as failures, marked `error_as_fail` in the result files (see [CODE_VS_DIRECT_CASES.md](CODE_VS_DIRECT_CASES.md) §3).*

*Companion results: [Variant robustness (contamination & paraphrase)](VARIANT_RESULTS.md) · [Scaffolding ablation](SCAFFOLDING_ABLATION.md) · [Trap diagnostics](TRAP_RESULTS.md) · [Code-vs-direct case studies](CODE_VS_DIRECT_CASES.md).*

## Setup

- **Core set**: 436 original, textbook-grounded, GT-certified problems (the set formerly labeled `base`).
- **Protocols** (symmetric prompts; identical SYSTEM = "expert in atmospheric science"; the ONLY intended difference is *who executes the final arithmetic*):
  - **code** — model writes an executable `solve()`; Python computes the graded number (the function body is the reasoning vehicle). The solver contract returns `{"value", "unit"}` pairs, so the grader can credit an answer given in a different but commensurate unit.
  - **direct** — model shows its working in prose, then reports each answer as `\boxed{<number> <unit>}`; the model does the arithmetic itself, and the declared unit gives the grader the same unit-reconciliation ability as in code mode.
- **Reasoning models** are marked **(reasoning)** in the model name; unmarked models run with thinking off.
- **Model coverage**: 16 configurations are evaluated under the code protocol; the direct protocol is run on a representative six-model subset spanning the capability range and both settings, sufficient to characterize the code-vs-direct gap. Two domain-specialised models (ClimateGPT-13B / 70B) are additionally evaluated under both protocols as an out-of-distribution reference point (see §Domain-specialised models).

### Metric definitions
- **Accuracy** — the primary metric: fraction of the 436 problems solved, reported as the **mean over the three runs ± one standard deviation** across runs. Standard presentation for stochastic-decoding evaluations. Code mode has no error records; in direct mode the 7 gateway non-completions are counted as failures (they are protocol-attributable — the same model solves those problems under the code protocol).
- **Tokens/run (M)** — mean total tokens to run the full 436-problem set once, in **millions**, averaged over the 3 runs. Tokens are counted **uniformly with a single tokenizer (tiktoken `o200k_base`) from the stored prompt/response/reasoning text**, *not* each provider's reported usage, so counts are comparable across models; `total = prompt + completion + reasoning` as three **disjoint** parts (completion = answer text only). These are o200k-normalized counts, not providers' billed tokens. Reproduce them with `uv run python -m eval.analysis.token_count experiments/core_code` (divide the printed per-model totals by the 3 runs). See Appendix B for the decomposition and the summary-only-reasoning caveat (†, gpt-5.5 (reasoning) and Gemini-3.1-Pro).
- *Secondary reliability metrics* (Appendix A): **pass@3** = solved by ≥1 of 3 runs (capability ceiling); **all@3** = solved by all 3 runs (reliability floor).
- **Standard deviation** is the sample SD (n−1) of the three per-run accuracies, the convention used throughout `docs/results/`.

## Table 1 — Code mode (16 configurations)

| model | accuracy (mean ± SD) | Tokens/run (M) |
|---|--:|--:|
| gpt-5.5 (reasoning) | 97.6 ± 0.1 | 0.35 † |
| Gemini-3.1-Pro (reasoning) | 96.0 ± 0.7 | 0.60 † |
| Kimi K2.6 (reasoning) | 93.8 ± 1.4 | 13.61 |
| DeepSeek-V4-pro (reasoning) | 93.3 ± 0.6 | 2.91 |
| Qwen-3.5-397B (reasoning) | 93.2 ± 1.3 | 2.56 |
| DeepSeek-V4-flash (reasoning) | 91.1 ± 0.8 | 1.37 |
| gpt-5.5 | 90.8 ± 1.4 | 0.29 |
| Qwen-3.5-397B | 90.5 ± 0.7 | 0.84 |
| Kimi K2.6 | 90.1 ± 0.3 | 2.37 |
| Qwen-3.6-27B (reasoning) | 88.5 ± 0.6 | 5.43 |
| DeepSeek-V4-pro | 82.6 ± 0.7 | 0.40 |
| DeepSeek-V4-flash | 81.7 ± 1.4 | 0.36 |
| Qwen-3.6-27B | 79.4 ± 0.7 | 0.74 |
| Qwen-3.5-9B (reasoning) | 76.9 ± 1.1 | 12.04 |
| Qwen-3.5-9B | 63.4 ± 1.3 | 1.47 |
| Qwen-2.5-72B | 41.1 ± 1.8 | 0.38 |

† **Token counts are understated for the two configurations whose endpoint returns a summary of the chain of thought rather than the whole of it**, so the o200k recount sees the summary and not the reasoning itself:

- **gpt-5.5 (reasoning)** — `/v1/responses` returns a concise reasoning summary, and only on **65.4%** of attempts (the rest carry no reasoning text at all).
- **Gemini-3.1-Pro (reasoning)** — the native `:generateContent` endpoint returns a *thought summary*; a summary is present on every attempt, but it is still a summary.

The size of the understatement is measurable, because each provider also reports its own token count per call (kept in `attempts[].usage` and never used as a reported number here). Dividing the provider's total by our recount on the core set gives **2.03×** for gpt-5.5 (reasoning) and **1.81×** for Gemini-3.1-Pro (reasoning), against **0.68–1.06×** for every other reasoning configuration — the two summary-only endpoints are separated from the rest by a wide margin, and the flag is set from that measurement rather than from a hard-coded list. Both are **excluded from token-efficiency comparisons** (Findings 3–5). All other models store their full reasoning text (or none).

## Table 2 — Direct mode (6 configurations, unit-carrying protocol)

| model | accuracy (mean ± SD) | Tokens/run (M) |
|---|--:|--:|
| gpt-5.5 (reasoning) | 95.6 ± 0.1 | 0.42 † |
| DeepSeek-V4-flash (reasoning) | 90.2 ± 1.2 | 2.84 |
| gpt-5.5 | 88.1 ± 0.6 | 0.38 |
| Qwen-3.6-27B (reasoning) | 85.5 ± 0.3 | 9.85 |
| DeepSeek-V4-flash | 83.1 ± 0.6 | 0.55 |
| Qwen-3.6-27B | 80.3 ± 1.7 | 1.00 |

## Table 3 — Code vs Direct (models run under both; accuracy, mean of 3 runs)

| model | code acc | direct acc | Δ (code − direct) |
|---|--:|--:|--:|
| Qwen-3.6-27B (reasoning) | 88.5 | 85.5 | +3.1 |
| gpt-5.5 | 90.8 | 88.1 | +2.8 |
| gpt-5.5 (reasoning) | 97.6 | 95.6 | +2.1 |
| DeepSeek-V4-flash (reasoning) | 91.1 | 90.2 | +0.9 |
| Qwen-3.6-27B | 79.4 | 80.3 | −0.8 |
| DeepSeek-V4-flash | 81.7 | 83.1 | −1.5 |
| **mean** | | | **+1.08** |

## Table 4 — Reasoning lift (code mode, paired; Gemini-3.1-Pro/Qwen-2.5-72B have no twin, omitted)

| backbone | non-reasoning acc | reasoning acc | Δ | Extra tokens/run (M) |
|---|--:|--:|--:|--:|
| Qwen-3.5-9B | 63.4 | 76.9 | +13.5 | +10.57 |
| DeepSeek-V4-pro | 82.6 | 93.3 | +10.7 | +2.51 |
| DeepSeek-V4-flash | 81.7 | 91.1 | +9.5 | +1.01 |
| Qwen-3.6-27B | 79.4 | 88.5 | +9.1 | +4.69 |
| gpt-5.5 | 90.8 | 97.6 | +6.8 | +0.06 † |
| Kimi K2.6 | 90.1 | 93.8 | +3.7 | +11.24 |
| Qwen-3.5-397B | 90.5 | 93.2 | +2.7 | +1.72 |

## Accuracy by category (code mode, 16 configurations)

Per-category accuracy over the 10-class subject taxonomy (`benchmark/core.json`;
*Observation and modeling* merges remote sensing and NWP/data-assimilation). Each cell is
a configuration's accuracy on that category as **mean ± SD across the 3 runs** (per run:
problems solved ÷ problems in the category), in percent; the final column repeats the
overall code-mode accuracy of Table 1. Rows are the **16 frontier configurations** (the
two domain-specialised ClimateGPT models are excluded, as in Finding 1), ordered by
overall accuracy. Per-cell run-to-run SD is small for the large categories but larger for
the small ones (median 3.0 pt, up to 14.3 pt), so single-cell differences within a
category should be read against it. Column headers (ordered easiest → hardest by
cross-model mean): Rad = Atmospheric radiation · Clim = Climate dynamics · Thermo = Atmospheric thermodynamics · BL = Boundary layer · Dyn = Atmospheric dynamics · Obs = Observation and modeling · Chem = Atmospheric chemistry · AQ = Air quality · Aero = Atmospheric aerosols · Cloud = Cloud physics. Category sizes (n): Rad 25 · Clim 19 · Thermo 89 · BL 32 · Dyn 116 · Obs 14 · Chem 51 · AQ 37 · Aero 24 · Cloud 29.

| model | Rad | Clim | Thermo | BL | Dyn | Obs | Chem | AQ | Aero | Cloud | overall |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 100±0.0 | 100±0.0 | 99±0.6 | 96±3.6 | 99±0.5 | 98±4.1 | 96±2.0 | 94±1.6 | 97±2.4 | 95±4.0 | 97.6±0.1 |
| Gemini-3.1-Pro (reasoning) | 96±0.0 | 98±3.0 | 96±0.6 | 96±1.8 | 98±1.3 | 93±0.0 | 93±1.1 | 96±1.6 | 97±2.4 | 93±0.0 | 96.0±0.7 |
| Kimi K2.6 (reasoning) | 97±2.3 | 96±3.0 | 97±1.3 | 91±3.1 | 97±2.2 | 88±8.2 | 89±3.0 | 90±3.1 | 88±7.2 | 90±6.0 | 93.8±1.4 |
| DeepSeek-V4-pro (reasoning) | 96±4.0 | 95±0.0 | 97±0.6 | 95±1.8 | 95±0.5 | 93±0.0 | 88±2.0 | 86±4.7 | 89±2.4 | 91±5.3 | 93.3±0.6 |
| Qwen-3.5-397B (reasoning) | 97±2.3 | 95±0.0 | 96±1.1 | 92±3.6 | 94±1.5 | 90±8.2 | 93±1.1 | 90±1.6 | 83±4.2 | 94±2.0 | 93.2±1.3 |
| DeepSeek-V4-flash (reasoning) | 93±6.1 | 93±6.1 | 95±0.6 | 91±3.1 | 94±0.5 | 86±14.3 | 86±3.4 | 87±1.6 | 85±2.4 | 87±4.0 | 91.1±0.8 |
| gpt-5.5 | 92±0.0 | 96±3.0 | 95±1.7 | 91±3.1 | 91±3.0 | 90±8.2 | 86±1.1 | 86±2.7 | 86±6.4 | 92±5.3 | 90.8±1.4 |
| Qwen-3.5-397B | 92±4.0 | 95±5.3 | 92±1.9 | 94±3.1 | 93±1.3 | 90±4.1 | 88±3.0 | 86±2.7 | 88±0.0 | 82±4.0 | 90.5±0.7 |
| Kimi K2.6 | 92±4.0 | 91±3.0 | 91±0.6 | 89±1.8 | 92±3.1 | 93±0.0 | 87±3.0 | 86±3.1 | 94±2.4 | 83±6.0 | 90.1±0.3 |
| Qwen-3.6-27B (reasoning) | 97±2.3 | 100±0.0 | 92±0.0 | 88±3.1 | 88±0.5 | 86±0.0 | 85±1.1 | 85±4.1 | 83±0.0 | 82±5.3 | 88.5±0.6 |
| DeepSeek-V4-pro | 85±2.3 | 88±6.1 | 88±1.7 | 92±1.8 | 85±2.2 | 95±4.1 | 79±3.0 | 68±3.1 | 79±4.2 | 63±8.0 | 82.6±0.7 |
| DeepSeek-V4-flash | 87±2.3 | 82±3.0 | 88±3.9 | 84±3.1 | 80±2.2 | 76±4.1 | 82±5.2 | 76±8.1 | 85±2.4 | 69±10.3 | 81.7±1.4 |
| Qwen-3.6-27B | 87±6.1 | 82±8.0 | 82±0.6 | 86±4.8 | 79±0.9 | 79±0.0 | 82±5.2 | 77±6.8 | 68±2.4 | 63±2.0 | 79.4±0.7 |
| Qwen-3.5-9B (reasoning) | 89±6.1 | 86±8.0 | 85±2.3 | 81±6.2 | 78±1.3 | 81±8.2 | 72±2.3 | 73±0.0 | 58±4.2 | 54±8.7 | 76.9±1.1 |
| Qwen-3.5-9B | 77±2.3 | 75±6.1 | 71±6.2 | 71±1.8 | 64±1.8 | 64±7.1 | 54±4.1 | 56±4.1 | 47±4.8 | 51±4.0 | 63.4±1.3 |
| Qwen-2.5-72B | 68±6.9 | 68±5.3 | 49±2.3 | 53±3.1 | 34±1.5 | 52±4.1 | 29±3.9 | 31±5.6 | 28±4.8 | 29±2.0 | 41.1±1.8 |

### Category summary (aggregated across the 16 configurations)

**Macro** is the unweighted mean of the 16 configurations' per-category accuracies; **SD**
is the spread across those 16 configurations; **config range** is the weakest and
strongest single configuration on that category.

| category | n | macro acc | SD (across configs) | config range (weakest–strongest) |
|---|--:|--:|--:|--:|
| Atmospheric radiation | 25 | 90.4 | 8.3 | 68.0 – 100.0 |
| Climate dynamics | 19 | 90.1 | 9.1 | 68.4 – 100.0 |
| Atmospheric thermodynamics | 89 | 88.4 | 12.7 | 48.7 – 99.3 |
| Boundary layer | 32 | 86.7 | 10.9 | 53.1 – 95.8 |
| Atmospheric dynamics | 116 | 85.0 | 16.4 | 34.5 – 98.6 |
| Observation and modeling | 14 | 84.7 | 12.0 | 52.4 – 97.6 |
| Atmospheric chemistry | 51 | 80.6 | 16.9 | 29.4 – 96.1 |
| Air quality | 37 | 79.2 | 16.6 | 30.6 – 96.4 |
| Atmospheric aerosols | 24 | 78.5 | 19.1 | 27.8 – 97.2 |
| Cloud physics | 29 | 76.1 | 19.4 | 28.7 – 95.4 |

Unweighted mean across the ten categories: **84.0%** (macro); the corresponding
problem-weighted mean of the 16 configurations' overall accuracies is **84.4%**.

**Finding 8 — A stable difficulty ordering across categories, widest at the bottom.**
The categories separate into an easier cluster — radiation, climate dynamics, thermodynamics,
boundary layer, dynamics, observation/modeling (macro 84.7–90.4%) — and a
harder cluster — chemistry, air quality, aerosols, cloud physics (macro 76.1–80.6%). The
gap between the easiest and hardest category is **14.3 pt** at the macro level. The
harder categories are also the **most model-discriminating**: cloud physics (SD 19.4),
aerosols (19.1), and chemistry (16.9) show the widest spread across configurations, and
their config ranges span 60+ points (cloud physics 28.7–95.4), whereas radiation
(SD 8.3) and climate dynamics (SD 9.1) are comparatively saturated for every
configuration. The ordering is consistent with the qualitative/multi-step character of
chemistry, aerosol, and cloud-microphysics problems versus the more formulaic
dynamics/thermodynamics computations; the two largest categories (dynamics n=116,
thermodynamics n=89) sit in the easier cluster, so the aggregate accuracy is not an
artifact of category size. The **easy/hard cluster split is the robust claim**; the fine
ordering *within* a cluster should not be over-read, as four categories are small
(Observation and modeling n=14, Climate dynamics n=19, Atmospheric aerosols n=24,
Atmospheric radiation n=25) and their macro values sit within one another's
cross-configuration spread. The per-model breakdown is the matrix at the top of this
section.

## Key findings

1. **Frontier saturation.** gpt-5.5 (reasoning) (97.6%) and Gemini-3.1-Pro (96.0%) approach the ceiling, and the field concentrates in a short hard tail: of the 436 problems, 147 (34%) are solved by all 16 configurations (majority-of-3-runs), whereas only 12 are solved by at most three and one (`dn_6.8`) by none. The strongest configuration still misses 6 problems, so model separation is driven by this small hard tail rather than by broad differences across the set. (This saturation statistic is computed over the 16 frontier configurations; the two domain-specialised models of §Domain-specialised models solve almost nothing and are excluded.)
2. **With answer encoding equalized, code and direct are nearly tied on accuracy — and where the difference resolves at all, it favours code.** Under the unit-carrying direct protocol the mean gap is **+1.08 pt** (range −1.5 to +3.1; Table 3). Only **three of the six** configurations separate the protocols by more than their own run-to-run scatter — Qwen-3.6-27B (reasoning) +3.1, gpt-5.5 +2.8, gpt-5.5 (reasoning) +2.1, each against a pooled SD of 0.2–1.5 — and all three favour code. The other three sit inside the noise (|Δ| ≤ 1.5 against pooled SD 1.4–1.9), two of them nominally favouring prose. The honest reading is therefore *near-tied, with no resolvable case in which prose beats code*, rather than a genuinely model-dependent sign. Code's real advantages therefore lie elsewhere: in **completion robustness** and in **token cost** (Finding 5). On completion, the direct protocol could not deliver three of the computationally deepest problems for gpt-5.5 (reasoning) — `air_139` and `ry_4.6` in all three runs, `ca_15.1` in one, 7 records in total, counted as failures — because the in-band derivation exceeds serving limits, while the same model solves all three in code mode. Genuine prose-specific failure modes exist (equation truncation, magnitude-for-sign substitution, shortcut-for-iteration substitution) but are model-specific rather than universal.
3. **Reasoning helps the weakest backbone most and saturates at the top**: the largest lift goes to Qwen-3.5-9B (+13.5, the only sub-70% backbone) and the smallest two to the strongest pair (+2.7 Qwen-3.5-397B, +3.7 Kimi K2.6). The trend is directional, not monotone — the second-largest lift (+10.7) belongs to the mid-tier DeepSeek-V4-pro, and gpt-5.5 gains +6.8 from the top of the table — so read it as "least accurate backbones benefit most on average", not as a rank correspondence. Measured on the seven paired backbones (Table 4); Gemini-3.1-Pro and Qwen-2.5-72B lack a matched twin and are excluded. The gain costs roughly **3.1–8.2× more tokens** (reasoning/non-reasoning total, Table 4; gpt-5.5 excluded — only a summary of its reasoning is returned, †).
4. **Token efficiency**: among non-reasoning configurations, gpt-5.5 is the efficiency leader (90.8% @ 0.29M). Among reasoning configurations, **the cheapest fully-counted one is DeepSeek-V4-flash (reasoning)** (91.1% @ 1.37M). Gemini-3.1-Pro (reasoning) appears cheaper still (96.0% @ 0.60M) and is the more accurate of the two, but **0.60M is a lower bound**: its endpoint returns only a thought summary, and its provider-reported total is 1.81× larger (≈1.09M). It therefore still sits below DeepSeek-V4-flash (reasoning) on either accounting, but the margin quoted from our own recount is not the real one, so it carries the dagger and is excluded from the efficiency ranking alongside gpt-5.5 (reasoning), whose count is understated by 2.03× on the same measurement (†). At the opposite extreme, **Kimi K2.6 (reasoning)** is the most token-intensive configuration in the set (13.61M/run — more than any other, including the small qwen reasoning models) for a mid-frontier 93.8%; its reasoning setting adds +11.24M tokens for a +3.7 pt gain over the already-competitive Kimi K2.6 (90.1%).
5. **Direct costs more tokens than code, never fewer.** Across the six models run under both protocols, direct spends on average **1.55× the tokens of code** (models with in-band reasoning text ~1.9×; DeepSeek-V4-flash (reasoning) 2.08×, Qwen-3.6-27B (reasoning) 1.81×; the smallest ratio is gpt-5.5 (reasoning) at 1.20×, but both of its counts are understated — † — making gpt-5.5 at 1.31× the smallest fully-counted ratio). Code offloads the arithmetic to Python and stays compact, whereas direct must verbalize all working and compute in prose — output length scales with the computational depth of the problem. Combined with Finding 2, the honest protocol comparison is: **near-equal accuracy, higher cost, and a completion-failure mode on the hardest problems** — which together still motivate the executable protocol as the primary evaluation setting.
6. **Reliability (Appendix A).** Strong reasoning models are consistent across runs (gpt-5.5 (reasoning) code pass@3 99.5 / all@3 94.7); the flakiest is Qwen-3.5-9B (pass@3 79.1 vs all@3 43.6, a 36-pt spread). Under the direct protocol, reliability is close to code-mode levels: the pass@3 ceiling is lower than code for five of the six models (the exception, Qwen-3.6-27B, edges its code ceiling 89.4 vs 89.0), while all@3 is lower for only **three** of the six (gpt-5.5, gpt-5.5 (reasoning), Qwen-3.6-27B (reasoning)) and is *higher* in direct for the other three — most sharply for DeepSeek-V4-flash (69.5 → 75.9), the model that is also 1.5 pt more accurate in direct (Table 3). Direct's capability ceiling is thus generally lower, but its run-to-run consistency is not uniformly worse.

## Domain-specialised models (ClimateGPT-13B / 70B)

ClimateGPT-13B and -70B are domain-adapted decoder models derived from **Llama-2** by continued pre-training on ~4.2 B tokens of curated climate-science text, then instruction-tuned for retrieval-augmented climate question answering (eci-io / EQTY Lab; [arXiv:2401.09646](https://arxiv.org/abs/2401.09646), [HF 13b](https://huggingface.co/eci-io/climategpt-13b) / [70b](https://huggingface.co/eci-io/climategpt-70b)). They are optimized for climate QA, **not** for code generation or numerical problem solving, and are reported here as an out-of-distribution reference rather than as leaderboard entries.

| model | code acc | direct acc | Δ (code − direct) | code-mode ungradable* |
|---|--:|--:|--:|--:|
| ClimateGPT-70B | 3.1 ± 0.4 | 4.1 ± 0.2 | **−1.1** | 53% (668/1268) |
| ClimateGPT-13B | 0.8 ± 0.7 | 3.7 ± 0.5 | **−2.8** | 70% (911/1297) |

\* fraction of code-mode failures (summed over the 3 runs) that never produced runnable code returning an answer (vs. producing a runnable but wrong answer). Under the direct protocol the corresponding ungradable fraction is ≤ 10% for both models (70B: 23/1254 = 2%, 13B: 119/1260 = 9%).

**Finding 7 — For a model that cannot code, the executable protocol imposes a code-generation tax, and the code-vs-direct ordering reverses.** Both ClimateGPT models score near zero (0.8–4.1%): the benchmark's textbook computations are out of reach for climate-QA-specialised Llama-2 derivatives, which is itself evidence that the task measures quantitative reasoning rather than climate-domain knowledge. More informatively, **direct exceeds code for both models — the opposite of the majority frontier ordering (Finding 2) — and the mechanism is explicit in the failure modes.** Under the code protocol, 70% of ClimateGPT-13B's failures and 53% of ClimateGPT-70B's are *ungradable* — the model never emits runnable code that returns an answer — whereas under the direct protocol almost all failures are gradable-but-wrong (≤ 10% ungradable). The code protocol therefore couples two abilities, physics and program synthesis; for a weak coder the second dominates, and removing the code-generation requirement (direct) recovers the few problems the model can reason through in prose. This is the strong-form version of the pattern in Finding 2: delegating arithmetic to Python is a net benefit only for models that can reliably write the program. **The sign of the code-vs-direct gap is thus capability-dependent, not a fixed property of the protocols** — a consideration when interpreting either protocol as the "harder" setting.

## Appendix A — per-run accuracy and reliability metrics

Per-run accuracy (single-run % solved) behind the 3-run means in Tables 1–2; "±" is the standard deviation of the three runs. **pass@3** = solved in ≥1 run; **all@3** = solved in all 3 runs.

### Code mode

| model | run1 | run2 | run3 | mean | ± | pass@3 | all@3 |
|---|--:|--:|--:|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 97.5 | 97.7 | 97.7 | 97.6 | 0.1 | 99.5 | 94.7 |
| Gemini-3.1-Pro (reasoning) | 96.6 | 96.3 | 95.2 | 96.0 | 0.7 | 97.2 | 94.5 |
| Kimi K2.6 (reasoning) | 94.3 | 95.0 | 92.2 | 93.8 | 1.4 | 97.7 | 89.2 |
| DeepSeek-V4-pro (reasoning) | 93.1 | 92.9 | 94.0 | 93.3 | 0.6 | 96.3 | 89.9 |
| Qwen-3.5-397B (reasoning) | 94.0 | 91.7 | 93.8 | 93.2 | 1.3 | 96.1 | 88.8 |
| DeepSeek-V4-flash (reasoning) | 91.1 | 92.0 | 90.4 | 91.1 | 0.8 | 96.1 | 85.3 |
| gpt-5.5 | 92.4 | 90.1 | 89.9 | 90.8 | 1.4 | 94.7 | 85.6 |
| Qwen-3.5-397B | 90.4 | 91.3 | 89.9 | 90.5 | 0.7 | 95.9 | 83.3 |
| Kimi K2.6 | 89.9 | 90.4 | 89.9 | 90.1 | 0.3 | 96.1 | 82.1 |
| Qwen-3.6-27B (reasoning) | 89.2 | 88.3 | 88.1 | 88.5 | 0.6 | 94.0 | 83.3 |
| DeepSeek-V4-pro | 83.3 | 81.9 | 82.8 | 82.6 | 0.7 | 89.9 | 75.5 |
| DeepSeek-V4-flash | 81.2 | 83.3 | 80.5 | 81.7 | 1.4 | 91.5 | 69.5 |
| Qwen-3.6-27B | 80.3 | 79.1 | 78.9 | 79.4 | 0.7 | 89.0 | 68.6 |
| Qwen-3.5-9B (reasoning) | 77.5 | 75.7 | 77.5 | 76.9 | 1.1 | 85.6 | 67.2 |
| Qwen-3.5-9B | 64.2 | 61.9 | 64.0 | 63.4 | 1.3 | 79.1 | 43.6 |
| Qwen-2.5-72B | 42.9 | 41.1 | 39.2 | 41.1 | 1.8 | 52.5 | 31.9 |

### Direct mode (unit-carrying protocol)

| model | run1 | run2 | run3 | mean | ± | pass@3 | all@3 |
|---|--:|--:|--:|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 95.6 | 95.4 | 95.6 | 95.6 | 0.1 | 96.3 | 94.3 |
| DeepSeek-V4-flash (reasoning) | 89.0 | 91.3 | 90.4 | 90.2 | 1.2 | 94.5 | 86.2 |
| gpt-5.5 | 87.8 | 88.8 | 87.6 | 88.1 | 0.6 | 92.4 | 83.3 |
| Qwen-3.6-27B (reasoning) | 85.3 | 85.8 | 85.3 | 85.5 | 0.3 | 91.3 | 78.2 |
| DeepSeek-V4-flash | 82.6 | 83.0 | 83.7 | 83.1 | 0.6 | 89.4 | 75.9 |
| Qwen-3.6-27B | 80.5 | 81.9 | 78.4 | 80.3 | 1.7 | 89.4 | 70.0 |

## Appendix B — token usage (per-run mean over the 436-problem set, thousands)

Mean tokens to run the full core set once, averaged over the 3 runs, counted uniformly with **tiktoken `o200k_base`** from the stored text (not provider usage). **completion** = answer/response text only (**excludes** reasoning); **reasoning** = stored reasoning-field text (0 = none stored: thinking off, or the provider did not echo it); **total** = prompt + completion + reasoning (three **disjoint** parts). o200k-normalized counts, not billed tokens. † gpt-5.5 (reasoning) and Gemini-3.1-Pro (reasoning): the endpoint returns a summary of the reasoning rather than the reasoning itself → the reasoning column, and therefore the total, is understated (measured against the providers' own counts: 2.03× and 1.81× respectively; see the Table 1 footnote).

### Code mode — tokens

| model | completion (k) | reasoning (k) | total (k) |
|---|--:|--:|--:|
| Kimi K2.6 (reasoning) | 4376.7 | 7012.2 | 13605.7 |
| Qwen-3.5-9B (reasoning) | 3900.2 | 5337.1 | 12040.9 |
| Qwen-3.6-27B (reasoning) | 1141.9 | 3749.2 | 5425.5 |
| DeepSeek-V4-pro (reasoning) | 636.1 | 1728.1 | 2910.0 |
| Qwen-3.5-397B (reasoning) | 208.4 | 2189.0 | 2563.1 |
| Kimi K2.6 | 1912.3 | 0.0 | 2365.3 |
| Qwen-3.5-9B | 1051.6 | 0.0 | 1467.3 |
| DeepSeek-V4-flash (reasoning) | 182.7 | 1014.4 | 1369.6 |
| Qwen-3.5-397B | 668.8 | 0.0 | 839.3 |
| Qwen-3.6-27B | 529.5 | 0.0 | 737.7 |
| Gemini-3.1-Pro (reasoning) | 134.6 | 320.2 † | 602.6 † |
| DeepSeek-V4-pro | 233.6 | 0.0 | 404.1 |
| Qwen-2.5-72B | 192.7 | 0.0 | 384.3 |
| DeepSeek-V4-flash | 206.8 | 0.0 | 357.0 |
| gpt-5.5 (reasoning) | 124.4 | 80.4 † | 353.9 † |
| gpt-5.5 | 143.3 | 0.0 | 292.7 |

### Direct mode — tokens (unit-carrying protocol)

| model | completion (k) | reasoning (k) | total (k) |
|---|--:|--:|--:|
| Qwen-3.6-27B (reasoning) | 2297.4 | 7357.1 | 9845.4 |
| DeepSeek-V4-flash (reasoning) | 391.0 | 2293.1 | 2842.2 |
| Qwen-3.6-27B | 847.5 | 0.0 | 997.7 |
| DeepSeek-V4-flash | 398.1 | 0.0 | 548.2 |
| gpt-5.5 (reasoning) | 173.8 | 102.1 † | 424.8 † |
| gpt-5.5 | 232.2 | 0.0 | 382.3 |
