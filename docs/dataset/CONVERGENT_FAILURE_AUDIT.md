# Convergent-failure audit — behavioral QA over the released set

*A dataset-side quality check that uses the evaluation itself as the auditor: when many
independent configurations fail a problem **with the same wrong value**, the shared value is
evidence about the problem — a convention split, an answer-key artefact, or a shared prior —
whereas scattered failures are evidence about the models. Run 2026-08-01 over the 16 frontier
configurations × 3 runs on the core set; five problems were repaired as a result (see
`pipeline/reports/errata.json`, entries dated 2026-08-01) and re-measured.*

## Method

For every failed code-mode measurement, take the **first sub-answer graded wrong** (the
`details` array is keyed by expected sub, so alignment is already fixed). Cluster these values
per (problem, sub) at ≤2% relative distance. A locus is flagged when **≥6 distinct
configurations** land in one cluster whose value is **>5% from the ground truth** (so ordinary
tolerance edge cases are excluded). The per-locus counts quoted below are the distinct
configurations landing within 0.2% of the stated value — the tighter figure, since each of those
clusters turned out to be an exact analytic value rather than a spread.

Self-validation: the mining independently re-found every previously adjudicated case —
`dn_6.8` (0.470, the Briggs/Martin σ-set split), `4.5` (half of the printed answer), `2.10`
(the 1/T prefactor), `air_167` (sign flip), `air_108` (the "east wind" convention) — before
surfacing anything new.

## Yield

**43 loci on 42 of the 436 problems.** Adjudicating the strongest loci against the statements,
the reference solvers, and the transcripts split them into three classes:

### Grading defects — correct solutions scored wrong (fixed)

| problem | defect | fix (GT value unchanged) |
|---|---|---|
| `jacob_8.2` | single sub keyed `"1"` while the gradable threshold is the problem's own part 3; key-name matching graded the part-1 qualitative indicator (−1) against 1.8. 11 configs converged; transcripts show the threshold computed correctly under key `"3"` | sub rekeyed `"3"`; solver key updated; OCR-lost prime in ε′/ε restored |
| `13.5` | part 3.1 asks two concentrations that are numerically identical (2.68×10⁻⁶ M), the Express-line enumerated only four answers, so models merged them and positional matching graded their correct 3.2 pH against the NO₃⁻ key. 11 configs converged on exactly this | Express-line now enumerates five values; sub keys follow the `1..N` contract |

### Under-pinned statements — two defensible readings, >5% apart (pinned)

| problem | ambiguity | resolution |
|---|---|---|
| `dn_15.19(b)` | forced-ventilation increment (2680 ft³/hr — 11 configs, arithmetic identical to the reference to the decimal) vs. total outdoor flow (= GT 111 ft³/min) | statement pins the total |
| `fp_11.1(b,c)` | required radiative lifetime (GT 1.4 ns) vs. observed lifetime (0.122 ns — 11 configs) | statement names the radiative lifetime; additionally the exact reading of "10% emit" (τ=9/Z) and the textbook's quench-dominated approximation (τ=10/Z) differ by 11%, so both are now accepted values (the dataset's first multi-accept sub) |
| `ry_6.10(2)` | the temperature inversion needs the book-specific closure A ≈ 3.3×10⁻⁵/T cm; σ-based physics lands 4–5% off | closure stated in the problem (precedent: `13.5` states its equilibrium constants); reference solver recentred onto it (280.4 K → 293.3 K against GT 293) |

A companion grader fix: `_UNIT_FACTORS` gained sub-second time units (ms/µs/ns) so
second-declared lifetimes reconcile; a corpus scan replaying `verify_solver` over all
238,119 stored records shows **0 retroactive verdict flips** — the addition matters only in
combination with the new accepted values.

### Model-side shared errors — statement and GT verified correct (kept, documented)

`air_208` (11 configs drop the factor 2 in the cylinder mass balance w = 2·M·Δz/R),
`holton_5` (11 configs apply √(2ν/f) with f→Ω, forgetting f = 2Ω in a rotating tank — exactly √2 off),
`5.3` (14 configs report the displacement amplitude although the statement gives the wind
fluctuation explicitly as peak-to-peak), plus the previously documented `dn_6.8` /
`4.5` / `2.10` / `air_167` / `air_108`. These are findings about models, not defects.

**30 further loci remain unadjudicated** — the 13 above account for the rest — among them the
exact sign flips on `holton_59` / `holton_39` and simple-factor splits on `dn_10.44` /
`dn_10.51` / `p_10`; none was edited.

## Re-measurement

All five repaired problems (and their 25 paraphrase variants) were re-run across every
runnable configuration; `--ids` merge-replace left the other 431 problems byte-identical
(verified record-by-record against pre-edit backups). Run-level passes, before → after:

| problem | core_code (54 runs) | direct (24) | restrictive (12) | paraphrase (240) | solved by (of 16, majority-of-3) |
|---|---|---|---|---|---|
| `jacob_8.2` | 22 → 41 | 18 → 18 | 3 → 6 | 81 → 192 | 7 → 14 |
| `13.5` | 9 → 34 | 9 → 16 | 1 → 7 | 67 → 157 | 2 → 11 |
| `dn_15.19` | 5 → 36 | 0 → 14 | 0 → 7 | 21 → 182 | 2 → 12 |
| `fp_11.1` | 0 → 39 | 0 → 17 | 0 → 9 | 0 → 180 | 0 → 13 |
| `ry_6.10` | 17 → 34 | 9 → 16 | 4 → 7 | 90 → 155 | 5 → 11 |

Roughly 1,000 measurements that had scored correct work as wrong were recovered; each problem
still defeats 2–5 configurations, so discrimination is preserved. The headline consequence:
**exactly one core problem (`dn_6.8`) is now solved by no configuration** (previously two),
and "solved by ≤3 configurations" drops 15 → 12; "solved by all 16" is unchanged at 147.

## Why this audit exists alongside the static audits

A static LLM convention audit (`pipeline/reports/convention_audit.json`) had passed **all** of
these problems — including `dn_6.8` with an explicit `alt_differs_gt5pct: false` (the Briggs
alternative differs by 14.5%) and `dn_15.19` as "follows uniquely" (two readings, 2.5× apart).
Convergent behavioral evidence catches what plausibility review misses, because it observes
what many independent solvers actually do rather than what one reviewer believes they will do.
The two are complementary: the static audit screens cheaply at construction time; the
behavioral audit requires evaluation runs but is the stronger certificate.

## Reproduction

The mining is a ~40-line scan over `experiments/core_code/` (first-failing-sub clustering as
specified above); the adjudications are recorded per problem in `pipeline/reports/errata.json`,
and every re-measured number above regenerates from `experiments/` via the standard analysis
modules.
