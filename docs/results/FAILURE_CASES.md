# Where (nearly) every model fails — three verified case studies

*Case studies of core-set problems that defeat most or all of the 16 evaluated configurations, selected under an explicit defect-screening protocol so that every failure analyzed here is attributable to the models, not to the dataset. Companion: [Core-set results](CORE_RESULTS.md) · [Code-vs-direct case studies](CODE_VS_DIRECT_CASES.md).*

## Selection protocol

Candidates were the core problems with the lowest pass rate over 16 configurations × 3 runs
(48 measurements each). Each candidate was then screened before acceptance:

1. **Answer-alignment screen** — re-execute every stored solver and test whether the ground-truth
   values appear under a permutation, sign flip, or unit rescaling of the model's outputs (the
   defect classes that produced earlier dataset repairs). Any problem whose failures are explained
   this way is excluded.
2. **Ground-truth re-verification** — the reference answer must be independently derivable
   (closed-form arithmetic reproduced in this document) or convergently validated (multiple
   frontier models reaching it independently), on top of the dataset's standing multi-model
   certification.
3. **Formulation screen** — problems whose model-vs-reference disagreement traces to an
   interpretive reading of the question or to empirical-chart variance are excluded (list and
   reasons in the Appendix).

Three problems survive. They are complementary: two show **structured** failure — most models
converge on the *same* wrong answer, exposing a shared shortcut — and one shows **unstructured**
collapse, where everything below the frontier scatters over dozens of orders of magnitude.

---

## Case 1 — The answer is printed in the problem, and models still return half of it

**`4.5`** (*An Introduction to Atmospheric Physics*; effective gravity; difficulty high) —
solved by **8 of 48 runs**; no configuration solves it in all 3 runs except gpt-5.5 (reasoning).

> *Evaluate Ω²a/g for the Earth. **Show that, at the Earth's surface, the magnitude |g′| of the
> effective gravity is about 0.7% less at the equator than at the poles**, and the maximum angle
> between g′ and a vector pointing towards the centre of the Earth is about 0.1°.*

The expected value — **0.7%** — is stated in the problem itself. Parts 1 and 3 are solved almost
universally (47/47 and 42/47 runs). Part 2 fails in 39 of 47 runs, and the failures are not
noise — they cluster:

| answer cluster | runs | what it is |
|---|--:|---|
| **0.345%** | **27** | Ω²a/g — the centrifugal term evaluated on a **rigid sphere**: exactly **half** the stated answer |
| 0.69% ✓ | 8 | the intended self-consistent calculation |
| 0.87% | 5 | a Clairaut-type coefficient (≈ 5/2 · Ω²a/g) recalled from real-Earth gravimetry |
| 1.01% / other | 7 | miscellaneous (includes 1 run whose part-2 output was ungradable) |

The physics: on a rotating planet whose surface is an **equipotential**, equatorial gravity is
reduced twice over — once by the centrifugal acceleration (−Ω²a, a 0.35% effect) and once because
the equipotential surface itself bulges, placing the equator farther from the centre (another
≈0.35%). To leading order the two contributions are equal, giving Δg/g ≈ 2Ω²a/g = 0.69% — which is
what the reference solver computes by solving for the equipotential shape numerically, and what
the textbook asserts. The majority of models compute the centrifugal term only, i.e. they treat
the Earth as a rigid sphere — a shortcut that contradicts the target value **printed in the very
sentence they are answering**. None of the 27 half-answer runs reconciles its result against the
stated 0.7%.

Two further observations sharpen the case. First, the knowledge is *present but unreliably
retrieved*: Gemini-3.1-Pro, DeepSeek-V4-pro (reasoning), Kimi K2.6 (reasoning) and Qwen-3.6-27B
(reasoning) each produce the correct 0.69% in *some* runs and the halved value in others — the
same model, sampling between the deep treatment and the shortcut. Second, the 0.87% cluster shows
a different failure route: reaching for a memorized real-Earth gravimetric coefficient (Clairaut's
theorem territory) instead of the self-contained model the problem defines.

**Why it matters:** this is a pure test of whether a model *derives from the stated physical
setup* or *pattern-matches a standard formula*. The problem even supplies the answer as a check,
and 39/47 runs fail to use it.

## Case 2 — A dropped prefactor, 5.5% wrong, and orthogonal to capability

**`2.10`** (*An Introduction to Atmospheric Physics*; saturation vapour density; difficulty
high) — solved by **9 of 48 runs**.

The problem derives ρ_vs(T) = A·e^(−T₁/T)/T (with T₁ = L/R_v ≈ 5417 K), then asks for the
e-folding height of ρ_vs under a constant lapse rate (T₀ = 300 K, Γ = 6.5 K/km). The logarithmic
derivative has two terms:

d ln ρ_vs/dz = −Γ(T₁ − T)/T² ⟹ **H = T₀²/(Γ(T₁ − T₀)) = 2.706 km**

Dropping the 1/T prefactor's contribution (keeping only the exponential) gives
H = T₀²/(Γ·T₁) = **2.556 km** — wrong by 5.5%, just outside the 5% tolerance. Both values
reproduce exactly from the constants above; the reference answer is verified by closed-form
arithmetic, not by trust in the solver.

The 48 runs split almost perfectly in two: **21 runs return 2.553–2.556 km** — bit-for-bit the
dropped-prefactor value — and 22 return the correct 2.70 km; the remainder is garbage from the
two weakest models. The error then **cascades**: the column water content (part 2), rain depth
(part 3) and latent-heat release (part 4) all scale with H, so a single dropped term forfeits the
whole four-part problem.

The most instructive property is that the slip is **orthogonal to capability and to reasoning**:
DeepSeek-V4-pro *(non-reasoning)* passes 3/3 while its *reasoning* twin fails 3/3 with the
dropped-prefactor value; Qwen-3.5-397B (reasoning) fails 3/3; gpt-5.5 and Kimi K2.6 each flip
between the two values across runs. Thinking longer does not protect against an incomplete
derivative — the failure is in symbolic care, not in search depth.

**Why it matters:** a one-term calculus slip, invisible at a glance (the two answers differ by
5.5%), reproduced identically by half the field, and amplified by the problem's multi-part
structure. It is the cleanest observed example of *consensus on a wrong derivation*: the wrong
answers agree with each other to four significant figures.

## Case 3 — Below the frontier, a multiplicative chain collapses without structure

**`ry_7.7`** (*A Short Course in Cloud Physics*; quasi-steady supersaturation; difficulty
high) — solved by **12 of 48 runs**, and those 12 belong almost entirely to the top four
configurations.

> *In a developing cumulus cloud the droplet spectrum is Gaussian (mean radius 4 μm, σ = 0.6 μm)
> and the cloud water content is 0.2 g/m³. Estimate the supersaturation in an updraft of 8 m/s
> (T = 0°C, p = 80 kPa).* Reference answer: **0.52%**.

Reaching 0.52% requires a genuinely long multiplicative chain with no single canonical formula to
recall: saturation vapour pressure at 0°C → supersaturation production/consumption coefficients
(Q₁, Q₂) → diffusional growth denominator (F_k + F_d, thermal + vapour terms) → droplet number
concentration from the LWC *via the third moment of the Gaussian spectrum* (⟨r³⟩ = r̄³ + 3r̄σ²) →
quasi-steady balance Q₁w = Q₂C. The reference value is convergently validated: gpt-5.5
(reasoning), Gemini-3.1-Pro and DeepSeek-V4-pro (reasoning) reach 0.498–0.529% independently in
9 of their 9 runs.

Everything below that tier does not converge on a wrong value — it disintegrates:

- 36 failing runs produce **essentially no repeated value**: the largest identical-answer cluster is the
  3 degenerate near-zero outputs, and **no non-zero value repeats even once**;
- failing answers span **more than 40 orders of magnitude** (1.7×10⁻²⁰ to 5.6×10²⁰), plus one negative
  supersaturation and two exact zeros;
- the same model lands in different decades on different runs (e.g. Qwen-3.6-27B: 5.6×10²⁰, 7143,
  1.4×10⁶).

This is the opposite failure signature of Cases 1–2. There, a shared shortcut produces *agreeing*
wrong answers; here, each run makes a *different* slip (unit conversion in e_s, a mis-assembled
F_k, the spectrum moment, the balance equation) and the multiplicative structure amplifies
whatever goes wrong first. A per-step error rate compounds through ~8 sequential quantities, so
mid-tier models — accurate on any individual step — almost never complete the chain intact.

**Why it matters:** it isolates *compositional* failure. No step of `ry_7.7` is exotic; the
difficulty is executing eight of them consecutively without one silent error. The pass/fail
boundary sits exactly at the frontier tier, making it the single most capability-discriminating
problem in the core set that survives all defect screens.

---

## What the three cases say together

| | Case 1 (`4.5`) | Case 2 (`2.10`) | Case 3 (`ry_7.7`) |
|---|---|---|---|
| failure signature | consensus wrong answer (27× the same value) | consensus wrong answer (21× the same value) | unstructured scatter (>40 orders of magnitude) |
| mechanism | conceptual shortcut: rigid-sphere physics for an equipotential-surface problem | symbolic slip: dropped prefactor in a logarithmic derivative | compounding of small errors through a long multiplicative chain |
| does reasoning help? | partially — frontier reasoning models find the full treatment *in some runs* | no — reasoning twins fail where non-reasoning twins pass | yes — only the frontier tier survives |
| self-check available? | yes — the target value is printed in the problem; unused | yes — the derivation is fully prescribed by the problem's own formula | no — no stated target |

Two structural lessons for evaluating (and training) scientific reasoning follow. First,
**consensus is not correctness**: in Cases 1 and 2 an ensemble/majority vote over 16 models would
*canonicalize* the wrong answer (27 vs 8 and 21 vs 22 runs). Second, the three failure modes —
shortcut substitution, symbolic carelessness, and compositional fragility — are *dissociable*:
reasoning post-training mitigates the third, only partially mitigates the first, and does nothing
for the second.

## Appendix — candidates examined and excluded, with reasons

For transparency: the remaining lowest-pass-rate problems were examined and *not* used, because
their failures are not cleanly attributable to model reasoning.

| problem | pass/48 | reason excluded |
|---|--:|---|
| `fp_11.1` | 39 | "lifetime of the excited state" admitted two readings (observed lifetime 1/k_q vs the radiative lifetime the 10%-yield condition implies); the statement now names the radiative lifetime and both derivations are accepted **[repaired 2026-08-01** — see `pipeline/reports/errata.json` and `docs/dataset/CONVERGENT_FAILURE_AUDIT.md`; count updated to the post-repair measurement**]** |
| `dn_6.8`, `dn_6.12` | 2, 10 | Gaussian-plume problems graded against one analytic fit of the Pasquill–Gifford–Turner *charts*; failing models use other published fits of the same charts — empirical-fit variance, not physics error |
| `dn_15.19` | 36 | part (b) formulation admitted two readings of which flow the added ventilation replaces; the statement now pins the total outdoor flow **[repaired 2026-08-01** — see `pipeline/reports/errata.json` and `docs/dataset/CONVERGENT_FAILURE_AUDIT.md`; count updated to the post-repair measurement**]** |
| `jacob_10.9` | 3 | several sub-answers expect exactly 0.0 and models return varying sub-answer counts — answer-cardinality matching risk, excluded conservatively |
| `air_201` | 19 | the reference accepts both signs of a quantity whose direction the problem states in words rather than by a coordinate convention, so sign-convention disagreements are not model errors here |
| `ry_4.6` | 4 | 11-sub-answer chain with heterogeneous per-sub causes, with no single model-attributable mechanism |
| `air_346`, `3.4` | 9, 9 | models return more quantities than the answer key stores (output-contract violations documented in the dataset-repair log) |
| `jacob_10.6` | 5 | pivotal sub-answer misses by 6.5% against a 5% tolerance — too close to the grading boundary to present as a clean failure |
| `13.5` | 34 | failures concentrated in a duplicated-value sub-answer pair; the Express-line now enumerates five values and keys follow the `1..N` contract **[repaired 2026-08-01** — see `pipeline/reports/errata.json` and `docs/dataset/CONVERGENT_FAILURE_AUDIT.md`; count updated to the post-repair measurement**]** |

All counts in this document are recomputed from `experiments/core_code/` (16 configurations × 3
runs); per-model per-run values for every table are reproducible from the stored `details` fields.
