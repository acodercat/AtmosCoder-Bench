# AtmosCoder-Bench — Scaffolding Ablation

*Companion results: [Core-set leaderboard](CORE_RESULTS.md) · [Trap diagnostics](TRAP_RESULTS.md).*

## What this tests

Textbook problems frequently **hand the model knowledge it should be expected to recall** — a
governing formula, a physical constant, a unit conversion, or a restatement of the given data.
When such content is left in the problem statement, a model can reach the answer by *plugging
into what the statement spells out* rather than by *knowing the physics*. This ablation isolates
that confound: for each affected problem we remove the recallable knowledge and measure the
resulting change in accuracy. The design lets us ask, for every model, whether its competence on
the core set reflects domain knowledge or the scaffolding embedded in textbook phrasing.

- **Set**: the **169** core-set problems that contained recallable scaffolding, each in two versions:
  - **with scaffolding** (`original`) — the statement as written.
  - **scaffolding removed** (`stripped`) — the recallable knowledge is deleted while the scenario,
    every problem-specific input and unit, the disambiguating assumptions, and the exact quantity
    asked are preserved verbatim. The stripped statement is exactly the one released in
    `benchmark/core.json`, so this ablation measures a property of the released benchmark, not of a
    side artifact.
- **What is removed** — quantified by a deterministic statement diff of each problem's `original`
  against its `stripped` version over the 169-problem set (categories overlap; a problem may lose
  both):

  | removed from the statement | # problems | share |
  |---|--:|--:|
  | ≥1 numeric value — a constant / standard value | 151 | 89% |
  | ≥1 handed-over formula (a math expression or an equals-relation) | 158 | 93% |
  | wording-only change (no number or formula dropped) | 3 | 2% |

  In total **589 numeric tokens** were deleted (median 3, maximum 15 per problem), and the
  stripped statement is a median of **12 words (61 characters) shorter**.
- **Solvability guarantee**: a rewrite was retained only if a strong reference model, shown *only
  the stripped text*, blindly reproduced the stored ground truth — establishing that the removed
  knowledge is recoverable and the problem remains **well-posed and solvable, only harder**. The
  reference `solve()` and `sub_answers` are unchanged, so grading is identical across the two
  conditions.
- **Protocol**: code mode; **3 runs per model per condition**; 4 models; the identical 169-problem
  set in every cell (fully paired). All four models are run in the non-reasoning setting;
  scaffolding-dependence concerns knowledge recall, which is orthogonal to the reasoning toggle. Per-run accuracy excludes the (zero to one) infrastructure
  errors; per-problem robustness uses a **majority-of-three** rule (a model *solves* a problem in a
  condition iff ≥2 of its 3 runs pass), which suppresses single-run noise in the flip counts.

## Results

**Table 1 — Accuracy with and without scaffolding (code mode, 3 runs, mean ± SD over runs).**
SD is the sample standard deviation (n−1) of the three per-run accuracies, the convention used
throughout `docs/results/`.
Models are ordered from largest to smallest. Δ is the mean accuracy lost when scaffolding is removed.

| model | with scaffolding | scaffolding removed | Δ (scaffolding effect) |
|---|--:|--:|--:|
| gpt-5.5 | 97.8 ± 0.3 | 96.1 ± 0.3 | **+1.8** |
| DeepSeek-V4-pro | 95.1 ± 0.9 | 89.5 ± 2.2 | **+5.5** |
| DeepSeek-V4-flash | 97.2 ± 0.9 | 88.0 ± 2.4 | **+9.3** |
| Qwen-3.5-9B | 87.6 ± 1.8 | 69.0 ± 2.4 | **+18.5** |

**Table 2 — Per-run accuracy (%, n = 169, no excluded errors).**

| model | condition | run 1 | run 2 | run 3 | mean ± SD |
|---|---|--:|--:|--:|--:|
| gpt-5.5 | with scaffolding | 97.6 | 98.2 | 97.6 | 97.8 ± 0.3 |
| gpt-5.5 | scaffolding removed | 96.4 | 95.9 | 95.9 | 96.1 ± 0.3 |
| DeepSeek-V4-pro | with scaffolding | 95.3 | 95.9 | 94.1 | 95.1 ± 0.9 |
| DeepSeek-V4-pro | scaffolding removed | 91.1 | 90.5 | 87.0 | 89.5 ± 2.2 |
| DeepSeek-V4-flash | with scaffolding | 98.2 | 97.0 | 96.4 | 97.2 ± 0.9 |
| DeepSeek-V4-flash | scaffolding removed | 87.6 | 90.5 | 85.8 | 88.0 ± 2.4 |
| Qwen-3.5-9B | with scaffolding | 87.6 | 89.3 | 85.8 | 87.6 ± 1.8 |
| Qwen-3.5-9B | scaffolding removed | 66.3 | 70.4 | 70.4 | 69.0 ± 2.4 |

**Table 3 — Paired outcome shifts (majority-of-3, 169 problems).**

| model | both solved | lost (scaffolded✓ → stripped✗) | gained | both failed |
|---|--:|--:|--:|--:|
| gpt-5.5 | 161 | 4 | 2 | 2 |
| DeepSeek-V4-pro | 151 | 10 | 4 | 4 |
| DeepSeek-V4-flash | 151 | 14 | 1 | 3 |
| Qwen-3.5-9B | 115 | 37 | 4 | 13 |

The *lost* column—problems a model solves with the scaffolding but not once it is removed—is the
model's **scaffolding-dependent set**; it grows monotonically as model scale falls (4 → 10 → 16 → 37).
The small *gained* counts (≤4) are consistent with residual stochasticity and confirm the effect is
overwhelmingly one-directional.

## Findings

**1. Scaffolding dependence increases as model scale decreases.** Ordering the models from largest
to smallest — gpt-5.5, DeepSeek-V4-pro, DeepSeek-V4-flash, Qwen-3.5-9B — the accuracy removed by
de-scaffolding grows monotonically: **+1.8, +5.5, +9.3, +18.5** points, a ten-fold range, with
the smallest (9B) model losing the most and the frontier model the least. The lost-problem counts in
Table 3 follow the same order (4, 10, 14, 37). A benchmark that leaves formulas and constants in the
problem statement therefore over-credits smaller models most, precisely at the low end of the scale
where discrimination is hardest.

**2. The strongest model is essentially unaffected.** gpt-5.5 loses **1.8 ± 0.6** points, within run
noise, and its scaffolding-dependent set is 4 of 169. It already commands the standard relations
and constants, so the scaffolding is redundant for it; the residual difficulty of the core set for
frontier models lies elsewhere (in the hard tail of the core set), not in
knowledge recall. Model scale and scaffolding-dependence are thus **decoupled at the frontier and
tightly coupled below it**.

**3. De-scaffolding roughly doubles model separation.** Across the four models the accuracy spread
(max − min) widens from **10.3 points with scaffolding to 27.0 points without** (2.6×). Converting
"apply the supplied relation" into "recall the relation, then apply it" is what exposes the
capability differences that the textbook phrasing had masked.

**4. Dependence concentrates in a compact, identifiable set of problems.** Under the majority-of-3
rule, **45 of 169 problems** are broken (solved → unsolved) for at least one model when scaffolding
is removed; the distribution over the number of models broken is {1 model: 32, 2: 8, 3: 3, 4: 2}.
Five problems break for ≥3 of the 4 models (`air_220`, `air_228`, `air_264`, `air_346`, `p_10`) and
two break for all four (`air_220`, `p_10`); these items become discriminative only once the
handed-over relation is withdrawn.

## Two regimes of de-scaffolding

The effect of removing scaffolding depends on *what* is removed. Two paired examples (full
statements, `original` vs `stripped`; per-problem *solve rate* = fraction of the four models that
reproduce the ground truth under the majority-of-3 rule) delineate the regimes.

### (a) Accuracy-neutral for universally-held knowledge — `air_102` (potential temperature)

*Removed:* the Poisson relation Θ = T (P₀/P)^{R_d/C_p} and the exponent R_d/C_p = 0.28571 — canonical
first-course thermodynamics.

*with scaffolding:*
> Find the potential temperature θ for air at P = 70 kPa with T = 10 °C. Use the equation
> Θ = T·(P₀/P)^{R_d/C_p}, where P₀ = 100 kPa, R_d/C_p = 0.28571, and temperatures are in Kelvin.
> Express your answer in °C.

*scaffolding removed:*
> Find the potential temperature θ for dry air at P = 70 kPa with T = 10 °C, referenced to a
> standard pressure of P₀ = 100 kPa. Treat the air as an ideal gas undergoing a dry adiabatic
> process. Express your answer in °C.

| condition | solve rate |
|---|:-:|
| with scaffolding | 4/4 (100%) |
| scaffolding removed | 4/4 (100%) |

Because the potential-temperature relation and the R_d/C_p exponent are universally held, removing
them imposes no measurable penalty — every model supplies them from parametric memory. De-scaffolding
does not, in itself, render a problem unsolvable: it deletes only knowledge a competent solver is
expected to possess, and the item remains well-posed (confirmed by the blind-recovery acceptance gate).

### (b) Discriminative for standard-but-non-trivial knowledge — `p_10` (Gaussian-plume dispersion)

*Removed:* the crosswind-integrated ground-level dosage relation
D_CWI = 2 Q_T / (√(2π) σ_z u), replaced by the qualitative cue "a continuous Gaussian-plume
dispersion model with reflection at the ground".

*with scaffolding:*
> A ground-level release of 2000 g of fluorescent particles is made during Class C stability with a
> wind speed of 5 m s⁻¹. The crosswind-integrated ground-level dosage along the 8-km arc is
> 8.2 × 10⁻¹ g s m⁻². What is the effective vertical dispersion parameter σ_z? The
> crosswind-integrated dosage for a ground-level source is D_CWI = 2 Q_T / (√(2π) σ_z u).
> Express your answer in m.

*scaffolding removed:*
> A ground-level release of 2000 g of fluorescent particles is made during Class C stability with a
> wind speed of 5 m s⁻¹. The crosswind-integrated ground-level dosage along the 8-km arc is
> 8.2 × 10⁻¹ g s m⁻². Assuming a continuous Gaussian-plume dispersion model with reflection at the
> ground, what is the effective vertical dispersion parameter σ_z? Express your answer in m.

| condition | solve rate |
|---|:-:|
| with scaffolding | 4/4 (100%) |
| scaffolding removed | 0/4 (0%) |

Withdrawing the dosage relation collapses the solve rate from 4/4 to 0/4: all four models apply the
supplied formula correctly, but none reconstructs it from the qualitative Gaussian-plume cue. The
problem remains solvable — the blind-recovery gate recovers it — so the failures isolate a genuine
gap in dispersion-modeling knowledge rather than an arithmetic or reading error. Under scaffolding
the four models are indistinguishable (all 4/4); de-scaffolding is what separates knowing the physics
from executing a handed-over relation.

**Together**, the two cases delineate the mechanism: for universally-held relations de-scaffolding is
accuracy-neutral (a), whereas for standard-but-non-trivial relations it converts a saturated,
non-discriminative item into a discriminative one (b). This is why removing handed-over knowledge
widens model separation and does so most for the weakest models — they carry the largest set of
type-(b) relations they can *apply* but not *recall*.

## Statistical notes and limitations

- **Three runs per cell** (SD reported in Table 1); the direction and ordering of Δ are stable
  across runs, and the paired flip counts use a majority-of-3 rule to suppress single-run noise.
- **Four models.** The trend is monotone across the four models ordered by scale, but four points
  cannot establish a functional form; broadening the model panel would tighten the relationship.
- **Model ordering.** gpt-5.5 is a frontier model of undisclosed size and is treated as the largest;
  the others are ordered by their stated scale (DeepSeek-V4-pro above DeepSeek-V4-flash; Qwen-3.5-9B at
  9 B parameters is the smallest). The monotone trend holds under this ordering.
- **Scope.** The ablation covers the 169 scaffolded problems, not the full 436-problem core set;
  the remaining problems contained no recallable scaffolding to remove. Every conclusion here is
  therefore about the scaffolded subset, not about the core set as a whole.
