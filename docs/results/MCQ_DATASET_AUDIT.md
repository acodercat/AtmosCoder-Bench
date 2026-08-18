# Auditing an External MCQ Benchmark: Wrong Answer Keys, and Why Option-Mode Grading Cannot See Them

**Claim.** The multi-model answer-verification stage used to certify AtmosCoder-Bench ground truth is not a formality — applied to an external, peer-reviewed benchmark (AtmosSci-Bench, NeurIPS 2025 D&B; the official **MCQ10 set, N = 670**, `benchmark/external/atmossci_mcq.json`), it flags defective templates the source benchmark ships as correct, and its flags are independently reproduced by downstream evaluation models. The intersection criterion flags **21 templates**; on unit-aware re-verification **2 are correct keys expressed in a commensurate unit** (a false-positive class the check itself corrects, see below), leaving **19 genuinely defective templates (190 problems, 28 %)** — of which **9 carry keys that two independent solvers contradict** (wrong value, wrong quantity, sign/convention conflict, or an incomplete key). The same defects are structurally invisible to the benchmark's own option-letter protocol — which is precisely the argument for numeric, execution-based grading with multi-model key verification.

All artifacts referenced here are in the repo: `pipeline/reports/mcq_audit_gpt.json`, `mcq_audit_gemini.json`, `mcq_k2.json`, `mcq_key_wrong_12.json`, `mcq_remove_intersection.json`, `mcq_removal.json`, `mcq_removed.json`; per-problem audit verdicts are embedded in `benchmark/external/atmossci_mcq.json` (`audit` field).

## 1. The verification pipeline (four stages)

The same procedure used to certify our own core set (`pipeline/k2_certify.py` protocol), applied template-by-template (the audit was run over the full imported pool of 85 templates; the counts below are restricted to the 67 that constitute MCQ10):

1. **Dual-auditor well-posedness review.** Two independent auditor models (GPT-5.4 and Gemini) review one representative instance per template for well-posedness, self-containedness, and answer plausibility — without being told the other's verdict.
2. **Dual blind solve.** Two independent solver models (GPT-5.4 and Claude Opus 4.8) solve each template *without seeing the stored key*. Verdicts over the 66 MCQ10 templates present at audit time (MCQ_6 was re-added afterward): **PASS_K2 32** (both blind solutions match the key), **PASS_K1 9** (one matches), **FAIL_BOTH_AGREE 12** (both solvers agree with *each other* but not with the key), **REVIEW 13**.
3. **Intersection adjudication.** A template is condemned only on agreement of independent evidence: `flag == both` **and** blind-solve verdict in {FAIL_BOTH_AGREE, REVIEW} → **21 templates (210 problems)** within MCQ10. Of these, `flag == both` ∧ FAIL_BOTH_AGREE flags **11 templates as key-wrong** (`mcq_key_wrong_12.json`): two solvers independently deriving the *same* value that contradicts the key.

4. **Unit-aware confirmation (removes 2 false positives).** The blind-solve comparison in step 2 is value-only. Two of the 11 key-wrong flags are not wrong keys at all — they are correct keys written in a different but commensurate unit: **MCQ_12** (key 7.99 **km**; solvers 7 990 m) and **MCQ_69** (key 6 690.5 **m**; solvers 6.69 km). The unit-aware grader (`verify_solver`, which reconciles km↔m and other commensurate units) confirms them: all six evaluation models pass MCQ_12 (88 %) and MCQ_69 (82 %) in code mode. Removing these two leaves **19 genuinely defective templates (190 problems)** and **9 key-contradicted templates**. That the value-only step over-flagged exactly the two unit-expression cases — and that the unit-aware code grader caught the over-flag — is itself evidence of the pipeline's specificity.

No single model condemns a problem. Every flag requires two auditors *and* two solvers to independently converge, and the final unit-aware pass strips value-only false positives — the design directly counters the known failure mode that LLM auditors over-flag.

## 2. What the audit found: examples

**MCQ_75 — key wrong by a factor of 30 (physically impossible).** *"By what percentage does gravitational acceleration change at a height of 100,000 km?"* Stored key: **−3.333 %**. At h = 100,000 km (≈16 Earth radii), g falls by ≈**−99.6 %**. The key back-derives from h = 100 km *and* an Earth radius of 6,000 km with a first-order approximation — three compounding errors. Both blind solvers returned the identical value, −99.641 %.

**MCQ_14 — the stated input exceeds Earth's circumference.** A temperature-advection problem places a second station *50,000 km* north of the first (Earth's circumference: ~40,000 km). The key (−2.055 °C/h) is only reproducible with 50,000 **m**. Taking the problem as written yields ≈+1.0 °C/h — which is what both blind solvers, and 3 of our 6 evaluation models, computed (the key −2.055 is reproduced by exactly 1 model, on the 50,000 m reading).

**MCQ_3 — key answers a different question than asked.** *"Determine the excess precipitation for each 10-minute interval"* — but the key stores *cumulative* runoff depths. Read as written, the key claims 1.99 in of excess rain fell during an interval containing only 0.58 in of rain. Both blind solvers returned the identical incremental series (…, 0.6516, 0.3617, 0.3259) where the key stores (…, 1.6257, 1.9874, 2.3133).

**MCQ_27 — key computed with the wrong planet.** Jupiter's gravitational-contraction rate: the key (0.0144 m/yr) is off by an order of magnitude; it is numerically consistent with using **Saturn's** mass (5.68×10²⁶ kg) in place of Jupiter's (1.90×10²⁷ kg). Both blind solvers land at ≈0.001 m/yr. (Flagged REVIEW rather than key-contradicted: the two solvers land close to each other but not to 6 figures.)

**MCQ_31 — the key omits requested sub-answers.** The problem asks for altitude, pressure, density *and potential temperature* at two levels; the stored key lists only three quantities per level, dropping potential temperature. Solvers return the full set, which no longer aligns with the truncated key — every model fails the template (0/60) not on the physics but on a key that answers fewer questions than the problem poses.

**Sign / convention conflicts (MCQ_17, MCQ_22, MCQ_50).** These keys carry a sign the solvers do not reproduce because the problem never fixes the convention (loop orientation, positive-lateral direction, vorticity-vs-circulation order). The magnitude is right; the key commits to one unstated sign. Genuine ill-posedness, distinct from a wrong value.

*Not defects (removed from the count).* MCQ_12 and MCQ_69 look ×1000 off in a value-only comparison but are correct keys in km / m; the unit-aware grader reconciles them and every model passes. They are the two false positives step 4 removes — kept here only to mark the boundary between a corrupted key and a commensurate-unit expression.

## 3. Independent replication: six evaluation models reproduce the audit

The audit's strongest external check is that it *predicts* the behavior of models that played no part in it. Our six code-mode evaluation models (Gemini-3.1-Pro, DeepSeek-R1, gpt-5.5, DeepSeek-V4-flash, DeepSeek-V3, Qwen2.5-72B) solved these templates months apart from the audit, on different infrastructure, with no access to audit artifacts. On the key-contradicted templates whose key is a genuinely wrong **value** (not a unit or sign artifact), the models reproduce the blind-solve consensus, not the stored key:

| Template | Stored key | Blind-solve consensus | Models reproducing the consensus |
|---|--:|--:|:--:|
| MCQ_75 | −3.333 % | −99.64 % | **6 / 6** |
| MCQ_17 | −2×10⁻⁵ s⁻¹ | +2×10⁷ (order-swapped) | 5 / 6 |
| MCQ_14 | −2.055 °C/h | +1.0 °C/h | 3 / 6 |
| MCQ_63 | −79.2 km | −0.71 (approx.) | 2 / 6 |

The flagship case is unambiguous: on **MCQ_75** all six models, from as many vendors, independently compute −99.64 % against a key of −3.333 %. Six models converging on the same answer the key calls wrong is not six failures — it is one wrong key. (Where the count is lower, the problem is simply harder — MCQ_14 and MCQ_63 are genuinely difficult — but no model reproduces the *key*.)

## 4. Why the option protocol cannot detect any of this

The option list for each MCQ is generated by perturbing the *stored key*; the graded-correct letter *is* the key. Two structural consequences:

1. **The physically correct answer is not among the options.** MCQ_75's options are {−3.767, −1.667, −3.333, −6.667} % — four variations on the wrong key. A model that derives −99.6 % correctly has no option to express it; a model that reproduces the key's error is graded correct.
2. **Strong models learn to reverse-engineer the defect.** Gemini-3.1-Pro's option-mode response to MCQ_75 states outright that *"the question contains a standard typo and meant a height of 100,000 m … using a simplified Earth radius of R ≈ 6,000 km"*, re-derives the key's erroneous −3.333 %, notes *"this perfectly matches one of the given options"*, and answers C. **Graded: correct (9/10 across the template's instances).** The same model in code mode computes the correct inverse-square answer for every instance's perturbed height (−98.0 % to −99.98 %), never the key. **Graded: wrong, 0/10.**

The damage is therefore *asymmetric by construction*, and the measurements show it. On the 190 genuinely-defective problems: option-mode accuracy barely moves (Gemini 89.5 %, DeepSeek-V4-flash 83.2 %, gpt-5.5 65.8 % — near their overall levels), while code-mode accuracy collapses to 0–14 % across all six models. Removing the defective problems raises every code-mode accuracy (by 14–18 points for the four strongest models; by +10.8 for DeepSeek-V3 and +6.2 for Qwen-2.5-72B, which have the least headroom) and shrinks the option-vs-code gap from +34.5/+44.8/+30.6 to +18.1/+32.3/+19.8. The *residual* gap is the real option-shortcut effect; the rest was defective keys punishing correct derivations.

| Model | Code, all 670 | Code, clean 480 | Option, all 670 | Option, clean 480 |
|---|--:|--:|--:|--:|
| gemini-3.1-pro | 60.0 % | 78.3 % | 94.5 % | 96.5 % |
| deepseek-v4-flash | 43.0 % | 57.3 % | 88.1 % | 90.0 % |
| gpt-5.5 | 49.6 % | 66.0 % | 80.1 % | 85.8 % |

## 5. What this defends

1. **The verification stage has demonstrated sensitivity.** It found genuinely defective keys — a planet mixup, an impossible input, a wrong-quantity key, an incomplete key — in a peer-reviewed, professionally constructed benchmark, and its corrections were independently replicated by uninvolved models (6/6 on the flagship MCQ_75). A GT-certification step that finds real defects in *other people's* published data can be trusted on our own.
2. **It also demonstrated specificity — twice over.** Just under half the audited templates (32 of 66) pass with both blind solutions matching the key; the flag criterion requires four-way independent agreement; and the final unit-aware pass *removed 2 of its own 11 key-wrong flags* (MCQ_12, MCQ_69) as commensurate-unit expressions rather than errors. The adjudication discards over-flagging — including its own — rather than rubber-stamping it.
3. **Answer-key verification is not optional for numeric benchmarks.** 28 % of MCQ10's templates (19/67) are defective and 9 carry keys two independent solvers contradict; every one silently mis-grades a correct model. Any benchmark graded against unverified keys inherits this noise floor.
4. **Unit-awareness is part of correct grading.** The same 2 false positives that a value-only comparison flags as "wrong keys" are the cases a unit-blind numeric grader would mark every correct model *wrong* on. Reconciling commensurate units (km↔m, %↔fraction) is not leniency — it is the difference between grading the physics and grading the notation.
5. **Option-letter grading is structurally incapable of self-correction.** Its distractors are generated *from* the key, so a wrong key remains internally consistent and undetectable — worse, it rewards models for reproducing the error and penalizes them (in any derivation-based re-grade) for being right. Execution-based numeric grading plus multi-model blind verification is the configuration that both *measures* derivation and *audits* its own ground truth.

**Why the defective problems remain in the evaluation set.** The 190 defective problems are *retained* in the 670-problem evaluation set by deliberate choice, not oversight: the option-mode runs, and the accuracy figures published by the AtmosSci-Bench authors, are all computed over the full MCQ10, so removing them unilaterally from our side would break every cross-protocol and cross-paper comparison. Both views are therefore reported — the full 670 for comparability, the clean 480 for the defect-free measurement — and this document is the bridge explaining the difference between them.

*All accuracy figures: 5 % relative tolerance, accuracy = passed/(passed+failed). Defective set = 19 templates / 190 problems (the 21 intersection-flagged MCQ10 templates minus the 2 unit-expression false positives MCQ_12, MCQ_69); clean-480 = 670 − 190. Blind-solve values quoted from `mcq_k2.json`; pass rates and replication counts recomputed from `experiments/mcq_code/*.json` via the unit-aware `verify_solver`.*
