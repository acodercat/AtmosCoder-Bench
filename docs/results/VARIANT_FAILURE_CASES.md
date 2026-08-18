# Solved on the original, lost on the variants — case studies

*Core problems that the field solves in its original form and then fails once the problem is
perturbed. The two perturbation families are analysed **separately**: numeric variants (same text,
different input values) and paraphrase variants (same values and same answer, reworded text).
Companion: [Variant robustness](VARIANT_RESULTS.md) · [Core-set failure cases](FAILURE_CASES.md).*

## Outcome rule and selection protocol

The outcome rule is the one used throughout this corpus:

- a model **solves a problem** iff ≥ 2 of its 3 runs pass (majority-of-3);
- a model **keeps a parent under a family** iff it solves ≥ 3 of that parent's 5 variants;
- a parent is **lost** by a model that solves the original but keeps < 3 of the 5 variants.

Candidates were ranked by the fraction of *core-solving* configurations that lose the parent, then
screened before acceptance — the same defect screen as `FAILURE_CASES.md`, plus two checks specific
to the variant families:

1. **Answer-order screen** — a failure whose returned values are the correct set in a different
   order is a grading-alignment artifact, not a reasoning failure, and is excluded.
2. **Ground-truth precision screen** — a variant whose stored answer is too coarse to discriminate
   at 5 % tolerance cannot separate a right answer from a wrong one, and is excluded.
3. **Formulation screen** — problems whose model-vs-reference disagreement traces to an
   interpretive reading, a missing constant, or a choice of empirical parameterization are excluded
   (listed in the appendix).

Three cases survive, and they were chosen to span the three *distinct* mechanisms the two families
expose — unstable physics, a misapplied memorised formula, and clerical unit transfer — rather than
to be the three largest effects. All counts below are recomputed from `experiments/` over 16
configurations × 3 runs.

---

## Case 1 (numeric) — `air_149`: the potential-temperature correction survives one instance, not five

**Bulk Richardson number** (*Practical Meteorology*). Given two levels, compute
Ri_B = g·Δθ·Δz / (T̄_v · (ΔU² + ΔV²)) and compare with Ri_c = 0.25. The statement fixes the
reference temperature explicitly ("use the layer-averaged virtual temperature in Kelvin"), so the
only physics the solver must supply is that static stability is set by the **potential**-temperature
difference, Δθ = ΔT + Γ_d·Δz — not by ΔT.

| | core | numeric variants | paraphrase variants |
|---|--:|--:|--:|
| configurations solving the original | **11 / 16** | — | — |
| of those, keeping the parent (≥ 3/5) | — | **6 / 11** | 10 / 11 |

**Five of the eleven configurations that solve the original lose it under numeric perturbation** —
including gpt-5.5 (reasoning), Kimi K2.6 (reasoning), Qwen-3.5-397B (reasoning) and
Qwen-3.6-27B (reasoning), each at 3/3 on the original.

The failures are not scattered. On every variant the largest failing cluster is one specific value —
exactly the Γ_d-free result — and on three of the five it is as large as the whole passing set:

| variant | Δz (km) | reference Ri_B | dominant wrong value | runs on the wrong value | runs passing (of 48) |
|---|--:|--:|--:|--:|--:|
| `air_149_v1` | 0.141 | −0.416 | **−0.483** | 20 | 17 |
| `air_149_v3` | 0.525 | +1.137 | **+0.613** | 18 | 19 |
| `air_149_v6` | 0.435 | −0.214 | **−0.549** | 21 | 19 |
| `air_149_v4` | 2.095 | +0.934 | −0.888 (minority) | 6 | 32 |
| `air_149_v7` | 0.941 | +1.335 | −0.370 (minority) | 7 | 27 |

*Wrong-value counts group answers within 1 % of the quoted value (the count is unchanged for any
band from 0.2 % to 2 %); the small spread comes from models using g = 9.8 vs 9.81 m s⁻².*

On `v1`, `v3` and `v6` the wrong value is held by about as many runs as the reference — more on
`v1` (20 vs 17) and `v6` (21 vs 19), slightly fewer on `v3` (18 vs 19) — so the field is split
roughly in half; on `v4` and `v7`, where the Γ_d term dominates Δθ because the layer is thick, the
reference wins comfortably (32 vs 6, 27 vs 7). Each dominant wrong value reproduces to four figures
by replacing Δθ with ΔT in the same solver — e.g. on `v3`,
9.8·11.145·525/(252.15·200.09) = 1.136 (reference) versus 9.8·6·525/(252.15·200.09) = 0.612.

The decisive evidence is that **the same model writes both physics**. Kimi K2.6 (reasoning), which
solves the original 3/3:

```python
# core (PASS)                                     # variant v1 (FAIL)
numerator = g * dz_m * (dT_K + (g/cp) * dz_m)     Ri = (g * dz * dT) / (T_avg_K * (dU**2 + dV**2))
```

and Qwen-3.6-27B (reasoning) writes `N2 = (g/T_avg) * (lapse_rate + Gamma_d)` on the original, then
on `v3` deliberates about sign conventions in comments and never applies Γ_d at all.

**Why it matters.** The original instance credits the model with a piece of physics it does not hold
stably: re-instantiating the same problem with different numbers recovers the Γ_d-free shortcut in
roughly half the field. Note the asymmetry across families — the same parent is almost untouched by
rewording (10/11 keep it), so this is a property of *re-derivation*, not of *reading*.

## Case 2 (numeric) — `holton_5`: a √2 that appears only when the numbers change

**Ekman-layer depth and spin-down time** (*An Introduction to Dynamic Meteorology*). For a tank
rotating at Ω, δ_E = √(2ν/f) with f = 2Ω, i.e. δ_E = √(ν/Ω).

| | core | numeric variants | paraphrase variants |
|---|--:|--:|--:|
| configurations solving the original | **8 / 16** | — | — |
| of those, keeping the parent (≥ 3/5) | — | **6 / 8** | 7 / 8 |

The run-level signature is the cleanest in the corpus: on **all five** variants the largest failing
cluster sits at exactly **√2 × the reference value**.

| variant | reference δ_E (cm) | dominant wrong value | ratio | runs |
|---|--:|--:|--:|--:|
| `holton_5_v4` | 0.09719 | 0.1375 | 1.415 | 19 |
| `holton_5_v5` | 0.08557 | 0.1210 | 1.414 | 23 |
| `holton_5_v6` | 0.09532 | 0.1348 | 1.414 | 19 |
| `holton_5_v7` | 0.10153 | 0.1436 | 1.414 | 16 |
| `holton_5_v9` | 0.08083 | 0.1143 | 1.414 | 22 |

The mechanism is explicit in the generated code — the model recalls the textbook formula correctly
and then substitutes the wrong symbol into it:

```python
# Qwen-3.6-27B (reasoning), holton_5_v4 (FAIL)
# Formula: delta_E = sqrt(2 * nu / Omega)
delta_E = math.sqrt(2 * nu / omega)     # f replaced by Omega -> exactly sqrt(2) too large
```

**Why it matters.** This is *memorised-formula* failure rather than derivation failure: the formula
is right, the Coriolis parameter of a rotating tank (f = 2Ω) is not. A benchmark with one
instance per problem cannot separate "recalled δ_E = √(ν/Ω)" from "recalled √(2ν/f) and substituted
f = Ω"; five instances make the √2 visible as a fixed multiplicative offset.

## Case 3 (paraphrase) — `ry_12.5`: identical physics, reworded, and the unit bookkeeping collapses

**Depletion of cloud water by rain collection** (*A Short Course in Cloud Physics*). An exponential
drop-size distribution (N₀ = 0.08 cm⁻⁴), a linear fallspeed law (k = 4×10³ s⁻¹) and a rain rate in
mm h⁻¹ must be combined into a decay constant; after 5 min the answer is **M/M₀ = 45 %**. The
problem mixes CGS and practical units, so the whole difficulty is unit bookkeeping through a
derived expression.

The five paraphrases are faithful rewordings: all five retain every given quantity (N₀ = 0.08 cm⁻⁴,
k = 4×10³ s⁻¹, R = 10 mm h⁻¹, t = 5 min), ask for the same ratio in the same units, and introduce
nothing the parent lacks — checked mechanically against the parent's fact set and by reading each.

| | core | paraphrase variants | numeric variants |
|---|--:|--:|--:|
| configurations solving the original | **13 / 16** | — | — |
| of those, keeping the parent (≥ 3/5) | — | **9 / 13** | 12 / 13 |

**Four of the thirteen configurations that solve the original lose it under rewording alone** —
gpt-5.5 (3/3 → 1/5 variants), gpt-5.5 (reasoning) (2/3 → 2/5), Kimi K2.6 (reasoning) (2/3 → 2/5) and
Qwen-3.5-9B (2/3 → 1/5) — while the *numeric* family leaves the same parent almost intact (12/13).

The failures converge on **M/M₀ ≈ 0.0028 %** — a four-order-of-magnitude over-estimate of the
depletion, produced by carrying the b-parameter or the rain rate in the wrong unit system. That
value appears **23 times across the paraphrases but only twice in 48 runs on the original**, which
is what makes it paraphrase-induced rather than a standing property of the problem.

**Why it matters.** It is the mirror image of Cases 1–2. There, re-instantiating the numbers exposed
a physics substitution; here the numbers are *identical* and only the prose moves, yet the unit
bookkeeping — the part of the solution that is pure clerical transfer from the statement — breaks.
It isolates a failure that no numeric perturbation can reach.

---

## A fourth mechanism worth citing (run-level, not parent-level): `p_10`

`p_10` (Gaussian-plume crosswind-integrated dosage, σ_z = 2Q_T/(√(2π)·D_CWI·u)) does not lose
enough parents to qualify as a case (12/13 keep it under paraphrase, 11/13 under numeric), but its
failures are unusually interpretable: the dominant wrong answer is **exactly half** the reference
(194.6 vs 389.2 m), i.e. the **ground-reflection factor of 2 is dropped** — even though every
paraphrase retains the phrase "with reflection at the ground". That value occurs 52 times across
the paraphrases against 8 of 48 runs on the original. The same problem is the discriminative example
in [SCAFFOLDING_ABLATION.md](SCAFFOLDING_ABLATION.md); together the two results say the reflection
factor is the specific piece of knowledge that is fragile — to removing the handed-over formula, and
to rewording the statement around it.

## What the two families catch, and what they do not

The three cases are complementary, and the contrast is the point of running both families:

| | what perturbing the **numbers** exposes | what perturbing the **wording** exposes |
|---|---|---|
| `air_149` | the model's choice of physics is not stable across instances (6/11 keep it) | almost nothing (10/11 keep it) |
| `holton_5` | a memorised formula applied with the wrong symbol, visible as a fixed √2 offset | almost nothing (7/8 keep it) |
| `ry_12.5` | almost nothing (12/13 keep it) | unit bookkeeping collapses (9/13 keep it) |

Neither family subsumes the other: the first two are invisible to rewording because the *derivation*
is what fails, and the third is invisible to renumbering because the *transcription* is what fails.
A benchmark with one instance per problem sees none of them — it records only that the model
produced the textbook number once.

**A counter-observation worth stating with them.** The most direct form of contamination — the model
answering a perturbed problem with the *parent's* stored answer — is real but rarely decisive.
`air_89` (noon insolation on a black surface, parent answer 680.5 W m⁻², variant answers
498.8–880.3) draws a strict memorisation echo from **12 of the 16 configurations across 23 runs**,
the largest such signal in the corpus, and yet **not one configuration loses the parent**: the echo
appears on a minority of runs and the ≥3-of-5 rule absorbs it. That is why none of the case studies
above is a memorisation case, and it is consistent with the aggregate result that no configuration
shows a Holm-significant core-vs-variant gap. Answer recall is detectable at the level of individual
runs; it is not what moves the leaderboard.

## Appendix — candidates examined and excluded

| parent | family | signal | reason excluded |
|---|---|--:|---|
| `snp_72`, `p_11`, `11.1`, `snp_12` | paraphrase | 0–1 lost | each states its required answer order explicitly, and none loses enough parents to qualify |
| `air_263`, `air_202` | paraphrase | 26 records | flagged by the same sweep but **not** defects: their paraphrases already pin the required order explicitly (`air_202`'s keys are symbolic), so the permuted answers are genuine model errors — kept in the data, not used as cases because the mechanism is answer-assembly rather than physics |
| `jacobson_38` | numeric | 5/15 lost | perturbation produced physically implausible inputs (θ_v = 211–422 K, p = 747–1400 hPa) and reference velocities of 10³–10⁴ m s⁻¹ |
| `snp_6` | numeric | 4/12 lost | two of the four requested quantities are phrased "show that …", so models return fewer values than the key stores — answer-cardinality risk |
| `ca_3.9` | paraphrase | 6/10 lost | interpretive: whether the given d50/σ_g describe the distribution **by mass** (reference) or **by number** (models applying a Hatch–Choate conversion); the paraphrases spell out "geometric standard deviation", which cues the second reading |
| `snp_45` | paraphrase | 5/10 lost | two independent reasons: the convergent wrong value (0.857 × reference) is a different Cunningham slip-correction parameterization — a constant-convention difference, not a derivation error — and the problem is on the confirmed-leakage list |
| `air_296` | paraphrase | 38 runs | the reference needs ρ_air, which the statement does not supply (it supplies only ρ_water); the convergent wrong value is exactly ρ_water/ρ_air = 837 × the reference |
| `6.9` | both | 3/8 lost each family | on the confirmed-leakage list, and its loss (3 of the 8 configurations that solve it) is not distinctive. Its statement names the graded quantity and asks for exactly one value; the residual failures are genuine wrong answers (110 of 134 return a single value) |
| `air_154`, `jacob_6.4`, `jacob_6.8`, `snp_94`, `fp_6.1`, `fp_7.1`, `ry_14.2` | paraphrase | 1–3 lost of 8–12 solving | failure concentrated in a non-leading sub-answer with heterogeneous per-sub causes — no single attributable mechanism |

## Reproducing

```bash
uv run python -m eval.analysis.robustness --boot 2000 --json <out>   # per-model core vs variant
uv run python -m eval.verify --set variants_numeric -t 0.05          # dataset re-verification
uv run python -m eval.verify --set variants_paraphrase -t 0.05
```

Per-run evidence is in `experiments/{core_code,variants_numeric_code,variants_paraphrase_code}/`:
`details` holds expected-vs-actual per sub-answer and `attempts[].response` the verbatim solver
quoted above.
