# AtmosCoder-Bench — Variant Robustness Results (numeric & paraphrase perturbations)

*16 models × 3 runs on the core set and both perturbation families; 0 excluded errors in every analyzed configuration.*

*Companion results: [Core-set results](CORE_RESULTS.md) · [Scaffolding ablation](SCAFFOLDING_ABLATION.md) · [Trap diagnostics](TRAP_RESULTS.md).*

## What this tests

Each core problem is paired with two perturbation families that hold the physics fixed:

- **Numeric variants** (5 per eligible parent; inputs re-sampled, reference answer recomputed by the
  certified solver). A model that memorized a textbook problem's *answer* — or is merely familiar
  with its original number combination — cannot transfer that advantage to the variant, so the
  core-vs-variant gap measures **contamination / memorization**.
- **Paraphrase variants** (5 per parent; wording rewritten, values and answer unchanged, certified
  semantically equivalent). The core-vs-paraphrase gap measures **surface-form (linguistic) sensitivity**.

## Setup

- **Models**: the 16 leaderboard configurations of the core-set evaluation (code protocol). The two
  domain-specialised ClimateGPT references are excluded (incomplete runs; out of scope). Every
  analyzed configuration has 3 complete runs whose id set equals the benchmark id set exactly, with
  zero infrastructure-error records.
- **Sets**: numeric = 1,730 variants (346 numeric-variantable parents × 5); paraphrase = 2,180
  variants (436 parents × 5).
- **Matched-subset rule**: core-set accuracy is always recomputed on the matched parent subset
  (346 parents for numeric comparisons, 436 for paraphrase), so every comparison is fully paired.
- **Outcome rules**: a model *solves a problem* iff ≥2 of its 3 runs pass (majority-of-3, suppressing
  decoding noise); a model *solves a parent at the variant level* iff it solves ≥3 of the parent's 5
  variants. Grading is unchanged (answer-keyed, unit-aware, 5% relative tolerance).
- **Statistics**: Δ = core − variant accuracy on paired parents; exact two-sided McNemar test on
  discordant parent pairs; 95% CI from the analytic paired SE (a seeded 2,000-resample bootstrap
  agrees; both reported in the analysis artifact); **Holm correction across the 16 per-model tests**.
- **Reproducibility**: `uv run python -m eval.analysis.robustness --boot 2000 --json <out>` and
  `uv run python -m eval.analysis.echo_forensics --json <out>` regenerate every number below.
- **Grading notes that matter for offline re-grading.** Two properties of the released data affect
  anyone replaying the stored outputs. (i) **Sub keys are not always positional**: 106 of the 436
  core problems (and their variants) key their sub-answers by the source problem's own labels
  (`'a'`/`'b'`, `'2'`, `'answer'`, a compound like `'sigma_z'`) rather than `"1".."N"`. The code
  prompt asks models to key `"1".."N"`, so on those problems name matching cannot succeed and
  grading falls back to position — which is exact whenever the model returns as many values as the
  key stores. (ii) A **small residue of count mismatches** survives: a model that reports more
  quantities than the key stores is graded on the first, and across the whole corpus 2 records end
  up with the correct value present at a non-matching position. Both are properties of the released
  artifact, not of any particular run.

## Table 1 — Contamination probe: core vs numeric variants (346 matched parents, majority-of-3)

| model | core % | variant % | Δ (pt) | 95% CI (Δ) | McNemar p | discordant (lost/gained) |
|---|--:|--:|--:|--:|--:|--:|
| Qwen-3.5-9B (reasoning) | 85.0 | 82.1 | +2.9 | [+0.0, +5.8] | 0.076 | 18 / 8 |
| **Kimi K2.6 (reasoning)** | 98.8 | 96.5 | **+2.3** | [+0.5, +4.1] | **0.021** † | **9 / 1** |
| Qwen-3.5-397B (reasoning) | 97.7 | 96.0 | +1.7 | [−0.0, +3.5] | 0.11 | 8 / 2 |
| Qwen-3.6-27B (reasoning) | 94.5 | 92.8 | +1.7 | [−0.2, +3.7] | 0.15 | 9 / 3 |
| Qwen-3.5-9B | 72.8 | 71.1 | +1.7 | [−2.4, +5.9] | 0.50 | 30 / 24 |
| gpt-5.5 (reasoning) | 99.4 | 98.0 | +1.4 | [−0.0, +2.9] | 0.12 | 6 / 1 |
| gpt-5.5 | 97.1 | 96.0 | +1.2 | [−1.0, +3.3] | 0.42 | 9 / 5 |
| Qwen-3.5-397B | 95.7 | 94.8 | +0.9 | [−0.6, +2.4] | 0.45 | 5 / 2 |
| DeepSeek-V4-flash | 88.7 | 87.9 | +0.9 | [−2.1, +3.8] | 0.70 | 15 / 12 |
| Gemini-3.1-Pro (reasoning) | 98.6 | 98.0 | +0.6 | [−0.6, +1.7] | 0.62 | 3 / 1 |
| DeepSeek-V4-flash (reasoning) | 95.7 | 96.2 | −0.6 | [−2.4, +1.2] | 0.75 | 4 / 6 |
| Qwen-3.6-27B | 85.5 | 86.1 | −0.6 | [−3.5, +2.3] | 0.85 | 12 / 14 |
| DeepSeek-V4-pro (reasoning) | 96.8 | 97.7 | −0.9 | [−1.8, +0.1] | 0.25 | 0 / 3 |
| Kimi K2.6 | 95.4 | 96.8 | −1.4 | [−3.5, +0.6] | 0.27 | 4 / 9 |
| Qwen-2.5-72B | 43.1 | 44.5 | −1.4 | [−5.6, +2.7] | 0.58 | 24 / 29 |
| DeepSeek-V4-pro | 88.4 | 91.0 | −2.6 | [−5.1, −0.1] | 0.064 | 5 / 14 |

† The smallest p of the 16 tests and the largest one-sided discordance (9 parents solved on the
core set are lost on variants, 1 gained), but it does **not** survive Holm correction
(p_Holm = 0.34). **No configuration does** — the smallest corrected p in the family is Kimi K2.6
(reasoning)'s. Note how little separates this row from significance and how little would restore
it: with 346 paired parents and a 9/1 split, moving a single discordant pair in either direction
shifts the corrected p across the 0.05 line. The signal is not robust at this sample size.

## Table 2 — Linguistic robustness: core vs paraphrase variants (436 parents, majority-of-3)

"5/5" = share of parents whose all five rewordings are solved; "0/5" = none solved; *run-flip* =
share of parents with unstable core-set outcomes across the 3 runs (decoding-noise reference).

| model | core % | para % | Δ (pt) | McNemar p | 5/5 | 0/5 | run-flip |
|---|--:|--:|--:|--:|--:|--:|--:|
| **gpt-5.5 (reasoning)** | 98.6 | 96.8 | **+1.8** | **0.039** | 93.8% | 1.4% | 4.8% |
| gpt-5.5 | 92.2 | 90.4 | +1.8 | 0.10 | 83.7% | 5.0% | 9.2% |
| Qwen-3.5-397B (reasoning) | 94.7 | 92.9 | +1.8 | 0.08 | 87.4% | 3.4% | 7.3% |
| Qwen-3.5-9B (reasoning) | 78.0 | 76.4 | +1.6 | 0.25 | 60.8% | 13.8% | 18.3% |
| Kimi K2.6 (reasoning) | 94.5 | 93.1 | +1.4 | 0.26 | 86.5% | 2.1% | 8.5% |
| Qwen-3.6-27B (reasoning) | 88.3 | 87.2 | +1.1 | 0.38 | 81.0% | 7.1% | 10.8% |
| DeepSeek-V4-flash | 83.9 | 83.0 | +0.9 | 0.60 | 70.0% | 8.3% | 22.0% |
| Gemini-3.1-Pro (reasoning) | 96.3 | 95.6 | +0.7 | 0.51 | 92.7% | 3.0% | 2.8% |
| DeepSeek-V4-flash (reasoning) | 92.0 | 91.7 | +0.2 | 1.00 | 83.5% | 4.4% | 10.8% |
| Qwen-3.5-397B | 92.4 | 92.2 | +0.2 | 1.00 | 83.3% | 4.1% | 12.6% |
| Qwen-2.5-72B | 38.8 | 39.0 | −0.2 | 1.00 | 27.3% | 42.4% | 20.6% |
| DeepSeek-V4-pro (reasoning) | 93.8 | 94.3 | −0.5 | 0.73 | 89.2% | 3.0% | 6.4% |
| Kimi K2.6 | 92.0 | 93.1 | −1.1 | 0.42 | 82.8% | 3.2% | 14.0% |
| Qwen-3.5-9B | 67.4 | 69.0 | −1.6 | 0.48 | 48.4% | 18.8% | 35.6% |
| Qwen-3.6-27B | 80.7 | 82.8 | −2.1 | 0.19 | 69.5% | 9.2% | 20.4% |
| **DeepSeek-V4-pro** | 82.6 | 86.2 | **−3.7** | **0.014** | 75.2% | 8.0% | 14.4% ‡ |

‡ The largest paraphrase shift, and the smaller of the two uncorrected p < 0.05 among the 16
paraphrase tests (the other: gpt-5.5 (reasoning) +1.8, p = 0.039) — but **no paraphrase result survives Holm correction**: this row's own
p = 0.0139 is the smallest of the 16 and corrects to p_Holm = 0.22. It also points in the
*opposite* direction: the model is *better* on rewordings than on the original textbook text, and
its numeric Δ is likewise negative (−2.6). This is a surface-form parsing weakness on original
phrasing, not contamination; LLM-generated rewordings are systematically cleaner than textbook
prose.

## Table 2b — Robustness spectrum: solving progressively more of a problem's variants

A purely descriptive view that keeps the **denominator at the number of core parents** and asks how
many of a problem's five variants the model solves (each variant = majority-of-3 runs, as
throughout). The threshold is a strictness dial: **≥3/5 is the lenient bar** — the same one used for
"variant %" in Tables 1–2, comparable in leniency to the core "≥2 of 3 runs" rule — and 5/5 is the
strict "all re-instantiations solved" bar.

**Read these columns down, not against `core`.** A core "solve" aggregates 3 runs while 5/5
aggregates 15, so the strict columns sit mechanically below core even with no real fragility
(≈ −10 pt at a per-run rate of 0.9, before any brittleness); the core-minus-5/5 difference is
therefore *not* a fragility measure and is deliberately omitted. The clean, aggregation-fair
robustness/contamination result is the paired test in Table 1, not this spectrum.

*Reproduce: `uv run python -m eval.analysis.threshold_accuracy`.*

### Numeric variants (346 parents)

| model | core % | ≥3/5 | ≥4/5 | 5/5 |
|---|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 99.4 | 98.0 | 98.0 | 95.4 |
| Gemini-3.1-Pro (reasoning) | 98.6 | 98.0 | 97.1 | 96.0 |
| DeepSeek-V4-pro (reasoning) | 96.8 | 97.7 | 96.5 | 92.8 |
| Kimi K2.6 (reasoning) | 98.8 | 96.5 | 95.4 | 91.0 |
| Qwen-3.5-397B (reasoning) | 97.7 | 96.0 | 95.4 | 91.3 |
| DeepSeek-V4-flash (reasoning) | 95.7 | 96.2 | 94.5 | 91.3 |
| gpt-5.5 | 97.1 | 96.0 | 93.6 | 92.2 |
| Qwen-3.5-397B | 95.7 | 94.8 | 91.6 | 87.0 |
| Kimi K2.6 | 95.4 | 96.8 | 95.4 | 90.8 |
| Qwen-3.6-27B (reasoning) | 94.5 | 92.8 | 90.2 | 87.6 |
| DeepSeek-V4-pro | 88.4 | 91.0 | 87.9 | 82.1 |
| Qwen-3.6-27B | 85.5 | 86.1 | 80.3 | 74.3 |
| DeepSeek-V4-flash | 88.7 | 87.9 | 83.8 | 77.5 |
| Qwen-3.5-9B (reasoning) | 85.0 | 82.1 | 78.6 | 67.1 |
| Qwen-3.5-9B | 72.8 | 71.1 | 63.0 | 52.3 |
| Qwen-2.5-72B | 43.1 | 44.5 | 37.3 | 31.2 |

### Paraphrase variants (436 parents)

| model | core % | ≥3/5 | ≥4/5 | 5/5 |
|---|--:|--:|--:|--:|
| gpt-5.5 (reasoning) | 98.6 | 96.8 | 95.9 | 93.8 |
| Gemini-3.1-Pro (reasoning) | 96.3 | 95.6 | 94.7 | 92.7 |
| Qwen-3.5-397B (reasoning) | 94.7 | 92.9 | 91.7 | 87.4 |
| Kimi K2.6 (reasoning) | 94.5 | 93.1 | 91.5 | 86.5 |
| DeepSeek-V4-pro (reasoning) | 93.8 | 94.3 | 92.9 | 89.2 |
| Qwen-3.5-397B | 92.4 | 92.2 | 88.5 | 83.3 |
| gpt-5.5 | 92.2 | 90.4 | 86.9 | 83.7 |
| Kimi K2.6 | 92.0 | 93.1 | 90.1 | 82.8 |
| DeepSeek-V4-flash (reasoning) | 92.0 | 91.7 | 89.7 | 83.5 |
| Qwen-3.6-27B (reasoning) | 88.3 | 87.2 | 83.7 | 81.0 |
| DeepSeek-V4-flash | 83.9 | 83.0 | 79.1 | 70.0 |
| DeepSeek-V4-pro | 82.6 | 86.2 | 81.0 | 75.2 |
| Qwen-3.6-27B | 80.7 | 82.8 | 77.1 | 69.5 |
| Qwen-3.5-9B (reasoning) | 78.0 | 76.4 | 70.9 | 60.8 |
| Qwen-3.5-9B | 67.4 | 69.0 | 61.7 | 48.4 |
| Qwen-2.5-72B | 38.8 | 39.0 | 33.9 | 27.3 |

The strict bar tightens, but essentially does not reorder, the leaderboard: rank agreement with the
core ordering stays high at every threshold (numeric Spearman ρ = 0.90 / 0.95 / 0.93 for ≥3/≥4/5;
paraphrase 0.93 / 0.96 / 0.98), so 5/5 is a stricter restatement of core capability rather than an
independent signal. The one visible deviation is consistent with Table 1: Kimi K2.6 (reasoning),
whose numeric core accuracy (98.8) is within noise of gpt-5.5 (reasoning)'s 99.4, falls to 91.0 at
5/5 where its tier peers hold 92.8–96.0. The spectrum is included as an illustrative consistency
view; the load-bearing robustness and contamination conclusions are Tables 1–2 and the echo
forensics below.

## Table 3 — Leaderboard stability across the three sets (16 models)

| comparison | Spearman ρ | Kendall τ |
|---|--:|--:|
| core vs numeric | 0.896 | 0.785 |
| core vs paraphrase | 0.913 | 0.807 |
| numeric vs paraphrase | 0.980 | 0.937 |

## Table 4 — Reasoning twins: does thinking reduce the contamination gap? (numeric Δ, pt)

| backbone | Δ non-reasoning | Δ reasoning | reasoning − non |
|---|--:|--:|--:|
| Kimi K2.6 | −1.4 | +2.3 | **+3.8** |
| Qwen-3.6-27B | −0.6 | +1.7 | +2.3 |
| DeepSeek-V4-pro | −2.6 | −0.9 | +1.7 |
| Qwen-3.5-9B | +1.7 | +2.9 | +1.2 |
| Qwen-3.5-397B | +0.9 | +1.7 | +0.9 |
| gpt-5.5 | +1.2 | +1.4 | +0.3 |
| DeepSeek-V4-flash | +0.9 | −0.6 | −1.4 |

*(The last column is computed from unrounded Δ values, so it can differ from the displayed
difference by 0.1.)* In **6 of 7** pairs the reasoning configuration shows the larger gap; the
exception is DeepSeek-V4-flash (+0.9 non-reasoning, −0.6 reasoning — the reasoning arm is the one
slightly *better* on variants, and both sit well inside noise). The pattern is that enabling thinking tends to amplify the
familiarity advantage rather than replace recall with derivation, but it is a tendency across a
small panel, not a law.

## Answer-echo forensics: from aggregate gaps to per-problem evidence

A failed variant answer is an **echo** when it matches the *parent's* textbook answer within 5% on
every graded *discriminative* sub — a sub where the parent's and the variant's expected answers
verifiably differ by more than 5% (minimum observed gap 6%, median 14%), so an unchanged answer can
never be counted. Records with no discriminative sub are excluded as uninformative.

**Failure taxonomy over all 83,040 variant instance-runs (10,430 failures, 12.6%):**

| failure type | count | share of failures |
|---|--:|--:|
| other wrong (far from both answers) | 8,768 | 84.1% |
| near-miss (within 15% of the variant's answer) | 769 | 7.4% |
| ungradable (no runnable answer) | 492 | 4.7% |
| no discriminative sub (uninformative) | 228 | 2.2% |
| **echo (= parent's answer)** | **173** | **1.7%** (0.21% of all runs) |

Echoes split by mechanism: **92 strict-memorization** (the model also solves the parent on the core set —
it demonstrably knows this problem and reproduces its answer instead of computing the variant's) and
81 *attractor* echoes (core-set unsolved; typically the model ignores the perturbed inputs and re-derives
from memorized standard constants — value anchoring, not per-problem leakage). Echoes are heavily
concentrated: 49 of 346 parents, with the top five accounting for 53% of all echo runs.

### Final per-problem contamination verdict (the released dataset)

Aggregating strict-memorization evidence per problem over the 16 models:

| verdict | n | criterion |
|---|--:|---|
| **confirmed leaked** | **12** | ≥2 independent models show strict memorization |
| suspect | 20 | exactly 1 model does |
| clean | 314 | no strict evidence in 16 models × 3 runs × 5 variants |

Confirmed problems (n models echoing): `air_89` (12), `snp_45` (5), `air_299` (4), `6.9` (3),
and `p_101`, `snp_50`, `air_385`, `air_304`, `jacob_4.8`, `holton_33`, `air_231`, `air_380`
(2 each). Example (`air_89`): parent answer 680.5 W·m⁻², variant answer 741.3 — twelve models output
680.5 on the perturbed variant. By source book the twelve split *Practical Meteorology* 6,
*Atmospheric Chemistry and Physics* 2, *Introduction to Atmospheric Chemistry* 2,
*Atmospheric Science: An Introductory Survey* 1, *An Introduction to Dynamic Meteorology* 1 —
i.e. concentrated in the freely-downloadable textbooks, which is the expected shape if the
leakage path is textbook → web → training data. None of the twelve appears in the external
AtmosSci-Bench MCQ set (checked by problem-text match), so a public-benchmark intermediary is
not supported by the evidence here.

### Exclusion check — does the gap survive removing every flagged problem?

| model | all 346 parents | excl. 12 confirmed | excl. all 32 flagged |
|---|--:|--:|--:|
| Kimi K2.6 (reasoning) | +2.3 (p=0.021) | +2.4 (p=0.021) | **+2.2 (p=0.039)** |
| Qwen-3.5-9B (reasoning) | +2.9 (p=0.076) | +2.7 (p=0.11) | +1.9 (p=0.29) |
| gpt-5.5 (reasoning) | +1.4 (p=0.13) | +1.5 (p=0.13) | +1.6 (p=0.13) |
| Qwen-3.5-397B (reasoning) | +1.7 (p=0.11) | +1.5 (p=0.18) | +1.6 (p=0.18) |
| Qwen-3.6-27B (reasoning) | +1.7 (p=0.15) | +1.5 (p=0.23) | +1.3 (p=0.34) |

The largest gap is essentially unchanged (+2.3 → +2.2 for Kimi K2.6 (reasoning), and its
uncorrected p stays below 0.05 throughout): identifiable per-problem leakage does **not** explain
the contamination signal.

## Key findings

1. **The benchmark is contamination-resistant.** After multiple-comparison correction **no** model
   shows a significant core-vs-variant gap (smallest p_Holm = 0.34); the model ranking is stable
   across the original set and both perturbation families (ρ = 0.90–0.98, Table 3); and variant
   failures remain overwhelmingly gradable-but-wrong: mean self-repair attempts are essentially
   unchanged for **14 of the 16** configurations (all within ±3 % of their core-set value). The one
   clear exception is **Kimi K2.6 (reasoning)** (1.40 core → 1.57 numeric → 1.60 paraphrase), which is
   also the model carrying the largest residual gap in Finding 2 — so its gap must be read with that
   in mind. (The reverse outlier, Qwen-3.6-27B (reasoning), needs *fewer* attempts on variants,
   1.16 → 1.06.) For the rest, the perturbations stress the physics, not the code generation — the
   numeric variants measure what they claim to measure.
2. **The strongest residual signal is Kimi K2.6 (reasoning)** (+2.3 pt, 9/1 discordance,
   uncorrected p = 0.021; p_Holm = 0.34) — while its non-reasoning twin runs the other way (−1.4).
   Qwen-3.5-9B (reasoning) is second (+2.9, p = 0.076). Both are **suggestive, not established**:
   at 346 paired parents a single discordant pair moves the corrected p across the 0.05 line, and
   one did — see the Table 1 footnote. A second reason to read Kimi K2.6 (reasoning) cautiously: it
   is the one configuration whose self-repair rate rises on variants (Finding 1), and part of its
   gap tracks that rather than physics. Recomputing its numeric comparison on **gradable runs only**
   — dropping runs whose code never produced an answer, on both sides — moves it from **+2.3 pt
   (p = 0.021, 9/1)** to **+1.7 pt (p = 0.070, 7/1)**: roughly a quarter of the residual gap comes
   from a higher ungradable rate on variants (48.5 % of its variant failures vs 29.6 % on the core
   set), not from wrong physics. The remaining +1.7 pt is already non-significant uncorrected, so it
   cannot survive Holm either. The honest statement is that the reasoning arms of Kimi K2.6 and the
   Qwen-3.x family lean consistently toward a familiarity advantage, with none of the individual
   tests surviving correction.
3. **Reasoning tends to amplify familiarity rather than replace it** (6 of 7 twins, Table 4), and
   the residual gap concentrates where derivation is hardest (high-difficulty parents +2.8 pt vs
   medium −0.3; atmospheric dynamics +1.6, the largest category by problem count).
4. **Mechanistically, what signal exists is distributional familiarity, not answer recall.** Literal
   echoes of the parent's answer account for only 0.21% of all variant runs (1.7% of failures), and
   excluding every problem with any strict-memorization evidence leaves the largest gap essentially
   unchanged (+2.3 → +2.2 for Kimi K2.6 (reasoning)). *Per-problem leakage and distribution-level
   familiarity are distinct phenomena and must be reported separately; only variant-based evaluation
   addresses the latter.*
5. **Twelve problems carry direct, convergent leakage evidence** and are released as a flagged list
   (with per-run, per-sub evidence records); they concentrate in the freely-downloadable source
   textbooks (6 of 12 from *Practical Meteorology*) and none of them appears in the external
   AtmosSci-Bench MCQ set.
6. **Paraphrase robustness holds for every model** (harmful-direction Δ ≤ +1.8 pt, none significant
   after Holm correction; smallest p_Holm = 0.22), and paraphrase-induced instability is
   commensurate with run-to-run decoding noise: the share of parents with mixed paraphrase outcomes
   (neither 5/5 nor 0/5, Table 2) is 0.9–1.5× the model's own run-flip rate for 15/16 models; the
   sole exception, Gemini-3.1-Pro (reasoning) (1.58×), has the *lowest* mixed share of all (4.4%, computed from
   the unrounded 5/5 and 0/5 shares, so it can differ by 0.1 pt from subtracting the rounded cells of
   Table 2) against an
   exceptionally low run-flip base (2.8%). The largest paraphrase shift, DeepSeek-V4-pro
   (−3.7 pt, uncorrected p = 0.014), is *improved* by rewording — a parsing weakness on original
   textbook prose, not a robustness failure. Per-parent 5/5 consistency tracks capability
   monotonically (93.8% for gpt-5.5 (reasoning) down to 27.3% for Qwen-2.5-72B).

## Statistical notes and limitations

- **Multiple comparisons.** Per-model tests are Holm-corrected across the 16 configurations within
  each family of tests; family-level statements (Qwen-3.x) use a sign test across configurations.
- **Outcome rules.** Majority-of-3 (problems) and ≥3/5 (parents) suppress decoding noise; the
  bootstrap and analytic CIs agree throughout. Instance-level (per-run, per-variant) accuracies show
  the same ordering and are stored in the analysis artifact.
- **Echo detection is conservative.** Only failed answers, only on subs where parent and variant
  answers verifiably differ (>5%); 228 uninformative failures are excluded rather than classified.
  Three borderline judgements (answer within 5% of both values when the gap is near the threshold,
  on non-listed parents) do not affect the confirmed list.
- **Attribution limits.** Strict memorization identifies problems whose answers a model reproduces;
  it cannot identify *where* the model saw them. The source-book concentration is an observed
  association, not a traced provenance: no confirmed problem matches an AtmosSci-Bench MCQ problem
  by text, so a public-benchmark intermediary is not supported by the evidence here. The attractor
  echoes (81) are evidence of value-anchoring behavior, not of
  per-problem leakage.
- **Scope.** Numeric conclusions cover the 346 numeric-variantable parents; the 90 core-only
  problems are perturbation-unsafe by construction and are probed only by paraphrase.
- **Artifacts.** `pipeline/reports/contamination_final.json` (per-problem verdicts + exclusion
  check), `pipeline/reports/echo_evidence.json` (173 per-run, per-sub evidence records),
  `pipeline/reports/echo_blacklist.json` (confirmed list with per-model attribution); analysis code
  `eval/analysis/robustness.py`, `eval/analysis/echo_forensics.py`.
