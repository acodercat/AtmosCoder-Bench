# AtmosCoder-Bench — Cross-domain Generalization Results

*131 problems across four non-atmospheric environmental domains, 5 models, code protocol, single run, 0 excluded errors.*

*Companion results: [Core set](CORE_RESULTS.md) · [Variant robustness](VARIANT_RESULTS.md) · [Scaffolding ablation](SCAFFOLDING_ABLATION.md) · [Trap diagnostics](TRAP_RESULTS.md).*

## Purpose

The core benchmark is atmospheric. This suite tests a different claim: **that the construction method — not the subject matter — is what produces a discriminative benchmark.** The identical pipeline (OCR → self-contained-numeric extraction → blind multi-model consensus ground truth → anti-hardcode audit → machine verification) was applied to four new environmental domains, and the same model family was evaluated under the same code protocol.

## Setup

- **Dataset**: `benchmark/cross_domain/{hydrology,environmental_chemistry,ecology,soil}.json` — 131 problems, every one machine-verified at 5 % relative tolerance (`eval.verify --input`, 100 %).
- **Protocol**: `code` — the model writes an executable `solve()`; Python computes the graded number. Identical to the core-set code protocol.
- **Models**: five non-reasoning configurations chosen to overlap with the core-set table, so the two are directly comparable.
- **Metric**: accuracy = passed / (passed + failed); no excluded errors occurred in any run.
- **Runs**: single run per model (the core set uses 3), so figures carry roughly ±1–2 points of decoding noise.

| domain | n | source |
|---|--:|---|
| Hydrology | 37 | MIT OCW 1.72 Groundwater Hydrology, 1.731 Water Resource Systems, 1.060 Engineering Mechanics II (CC BY-NC-SA) |
| Environmental chemistry | 21 | MIT OCW 1.85 Water & Wastewater Treatment, 1.061 Transport Processes, 1.77 Water Quality Control (CC BY-NC-SA) |
| Ecology / biogeochemistry | 19 | MIT OCW 1.018J Ecology I, 1.020 Ecology II, 12.007 Geobiology, 7.014 Biology (CC BY-NC-SA) |
| Soil / geotechnical | 54 | Das, *Principles of Geotechnical Engineering*, 9th ed. |

Ground truth is blind multi-model consensus (author Opus 4.8; independent witnesses gpt-5.5-reasoning and DeepSeek-V4-pro-reasoning), admitted only on position-by-position agreement within tolerance, then passed through the anti-hardcode / dead-input audit. Where the source ships an answer key, stored answers were additionally cross-checked against it (§Finding 4).

## Table 1 — Accuracy by model and domain

| model | Hydrology (37) | Env. chemistry (21) | Ecology (19) | Soil (54) | **Overall (131)** | Tokens |
|---|--:|--:|--:|--:|--:|--:|
| gpt-5.5 | 94.6 | 90.5 | 89.5 | 94.4 | **93.1** | 80 k |
| Kimi K2.6 | 94.6 | 95.2 | 78.9 | 94.4 | **92.4** | 417 k |
| DeepSeek-V4-flash | 86.5 | 81.0 | 89.5 | 96.3 | **90.1** | 92 k |
| Qwen-3.6-27B | 75.7 | 95.2 | 89.5 | 94.4 | **88.5** | 178 k |
| Qwen-2.5-72B | 37.8 | 14.3 | 57.9 | 50.0 | **42.0** | 107 k |

*Tokens: o200k-normalized totals for one pass over all 131 problems (prompt + completion + reasoning, disjoint), counted from stored text rather than provider-reported usage. The DeepSeek-V4-flash figure was previously quoted as 128 k, which was that provider's own count and so did not match the basis this footnote declares; it is 92 k on the uniform recount, and the four other rows are unchanged.*

---

## Finding 1 — The suite reproduces the core benchmark's model ordering

This is the result the suite exists to produce. Core-set figures are the code-protocol, 3-run means from [CORE_RESULTS.md](CORE_RESULTS.md).

**Δ is the difference of the two displayed (1-dp) values**, so it can be checked against this table directly; recomputing from raw counts differs by at most 0.1 pt.

| model | Core (436, atmospheric) | Cross-domain (131) | Δ |
|---|--:|--:|--:|
| gpt-5.5 | 90.8 ± 1.4 | 93.1 | +2.3 |
| Kimi K2.6 | 90.1 ± 0.3 | 92.4 | +2.3 |
| DeepSeek-V4-flash | 81.7 ± 1.4 | 90.1 | +8.4 |
| Qwen-3.6-27B | 79.4 ± 0.7 | 88.5 | +9.1 |
| Qwen-2.5-72B | 41.1 ± 1.8 | 42.0 | +0.9 |

**The ordering is preserved exactly** — all five models keep their core-set rank — and the two anchors reproduce almost exactly: the strongest model moves +2.3 points and the weakest +0.9. Qwen-2.5-72B scoring **42.0 % in hydrology, environmental chemistry, ecology and soil mechanics after scoring 41.1 % in atmospheric science** is the sharpest single piece of evidence: a model's score is set by the construction protocol, not by the field.

The mid-range models gain ~10 points, consistent with the cross-domain suite being somewhat easier on average — it is drawn from course problem sets and an undergraduate textbook rather than graduate atmospheric monographs. Easier, but not saturated: see Finding 2.

## Finding 2 — Discriminative without being saturated, and with no dead items

Three numbers characterise the suite's resolving power:

- **51-point spread** between weakest and strongest model (42.0 → 93.1).
- **27 % of problems split the strong four** — 35 of 131 are solved by some strong models and missed by others. These are what actually separate the leaders; the remaining 96 are solved by all four.
- **Zero problems are failed by all four strong models.**

That last number matters more than it looks. An item no capable model can solve is usually not a hard item but a broken one — ill-posed, under-specified, or carrying wrong ground truth. Reaching zero was not automatic: it is the state the suite arrived at *after* the repair pass in Finding 4, and it is the cleanest available evidence that no known-defective problems remain.

## Finding 3 — Domain difficulty depends on who is asking

Ranking domains by mean accuracy gives different answers for weak and strong models, and the gap itself is the informative quantity.

| domain | all 5 models | strong 4 | Qwen-2.5-72B | weak–strong gap |
|---|--:|--:|--:|--:|
| Environmental chemistry | 75.2 | 90.5 | 14.3 | **76** |
| Hydrology | 77.3 | 87.2 | 37.8 | 49 |
| Soil | 85.6 | 94.4 | 50.0 | 44 |
| Ecology | 81.1 | 86.8 | 57.9 | 29 |

**Environmental chemistry is the most discriminative domain in the suite** — a 76-point gap between the weak model and the strong average, versus 29 for ecology. Its problems are long multi-step reactor and treatment calculations in which one mis-chained intermediate destroys the final number, so partial competence earns nothing. Ecology sits at the other extreme: its problems are mostly short budget and rate calculations that a weaker model can still get right, which compresses the field (86.8 % strong vs 57.9 % weak).

For benchmark design the implication is that **ecology-style short-budget problems are poor discriminators and environmental-chemistry-style multi-step chains are excellent ones** — worth knowing when choosing what to mine from a new domain.

## Finding 4 — Consensus ground truth failed systematically in one cluster, and evaluation is what caught it

This is the most consequential methodological result here.

Machine verification confirms only that a stored solver reproduces its own stored answer; it is structurally blind to a *wrong* answer. Multi-model consensus at construction time is meant to cover that gap, but three models sharing one reading of an under-specified problem will agree — confidently and identically.

That is exactly what happened. Every problem drawn from one 1.85 activated-sludge design assignment carried ground truth that **disagreed with the course's own answer key**:

| id | consensus GT | official key |
|---|--:|--:|
| `env_38` (sludge age) | 2.637 d | 51 h |
| `env_39` (reactor biomass) | 7580 | 6288 |
| `env_40` (effluent COD) | 3.906 | 4.7 |
| `env_41` (utilization rate) | 0.0495 | 1.43 |
| `env_43` (recycle ratio) | 1.715 | 1.08 |
| `env_44` (wasting rate) | 6.93 × 10⁻⁵ | 2.5 × 10⁻⁴ |

The cause is a genuine defect in the problems, not in the models: these parts require the course's own conventions for the "design safety factor", the substrate-utilization rate *U*, and the Metcalf & Eddy F/M definition — none of which appear in the problem text. One of them says so explicitly ("use the definition given in lecture, not the textbook"). When an author model was asked to re-derive them **against the official value**, it could not do so for five of the six: the official answer is genuinely unreachable from the statement. All seven problems from that cluster were removed.

Two diagnostics made this visible, and both are cheap enough to run before freezing any set:

1. **Divergence among an independent model population.** A hard-but-well-posed problem makes models converge — on the right answer, or on the same wrong one. An under-specified problem makes them scatter. `env_40` drew five answers spanning six orders of magnitude; by contrast `env_36`, from the same assignment, had every strong model land exactly on the official value. Divergence, not difficulty, is the ambiguity signal.
2. **The answer key, where one exists.** Cross-checking all stored answers against available keys found this cluster and essentially nothing else: of the other checked problems, mismatches were unit or rounding conventions (fraction vs percent, N vs kN, mm/s vs cm/s, a textbook's rounded intermediates), not errors. The soil and hydrology sets came through clean.

The failure was therefore **localised, not systemic** — one under-specified assignment, caught and removed. But the general lesson stands: *consensus ground truth needs an independent-population check before a set is frozen*, and `eval.verify` passing at 100 % says nothing about whether the answers are right.

## Finding 5 — Near-identical accuracy at 5× the token cost

gpt-5.5 and Kimi K2.6 finish within 0.7 points of each other (93.1 vs 92.4) while Kimi K2.6 spends **417 k tokens against gpt-5.5's 80 k** — a 5.2× difference for statistically indistinguishable accuracy. Qwen-3.6-27B and DeepSeek-V4-flash tie on accuracy (88.5 vs 90.1, within a point) while Qwen-3.6-27B spends 1.9× the tokens. Accuracy alone ranks these models; accuracy per token separates them sharply, and the ordering is not the same.

---

## Dataset provenance and repairs

The set reached its current state through one defect review and one answer-key repair pass. Eight problems were removed permanently:

- `env_42` — requires a lecture-only F/M definition absent from the text.
- `eco_25` — trophic topology comes from a food-web figure the solver never sees.
- `env_38`, `env_39`, `env_40`, `env_41`, `env_43`, `env_44` — official answer unreachable from the problem statement (Finding 4).

Two problems were repaired rather than dropped: `env_25`'s stored answers were reordered to the official key's order, and its values replaced with the key's. Removed ids are held in a permanent exclusion list so that later expansion passes cannot reintroduce them.

## Reproducing

```bash
# evaluate one model on one domain
uv run python -m eval.runner --model gpt55 \
  --input benchmark/cross_domain/hydrology.json \
  --exp-id cross_domain/hydrology --mode code

# re-verify every stored solver reproduces its answer
uv run python -m eval.verify --input benchmark/cross_domain/soil.json -t 0.05
```

Results live at `experiments/cross_domain/{domain}/{model}.json` in the standard `{metrics, results}` format, with per-attempt logs and per-sub-answer expected/actual details for offline re-grading at other tolerances.
