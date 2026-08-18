# Defending LLM-assisted construction — reviewer-facing reliability argument

Drafting reference for the paper's **Dataset** / **Limitations** sections. Purpose:
pre-empt the reviewer worry *"the benchmark leans heavily on LLMs — how do we trust
the problem quality?"* Everything below is grounded in artifacts already in the repo
(`eval.verify`, `docs/results/*`, `pipeline/reports/*`); numbers are cross-checked
against those sources. This is scaffolding for writing, not final paper text — except
the clearly-marked **ready-to-paste** paragraphs at the end.

---

## 1. The reframing (do this everywhere)

Move the reviewer's question from **"did you use LLMs?"** to **"can an LLM error
survive admission?"** The answer the whole pipeline is designed to give:

> **LLMs are *proposers*; admission is decided by evidence that does not depend on
> trusting any single model (evidence-gated admission).**

Three admission mechanisms, each independent of believing a particular LLM:

1. **Execution grounding.** Ground truth is not a model's assertion — it is the output
   of an *executable* `solve()`. Anyone can re-verify all 436 problems end-to-end with
   **zero LLM calls** (`uv run python -m eval.verify --set core`). The LLM writes
   *auditable code*, not an unverifiable answer.
2. **Independent agreement.** Every answer is verified **three-way**: models from three
   **distinct developers** each solve independently, never shown the answer's value.
   Where the textbook publishes an answer, all three must match it (textbook-anchored
   route); where it does not, all three must agree with one another (cross-model
   route). The agreed computation is then re-checked by hand on both routes. For an
   error to survive it must be produced *independently, as the same numerical value,
   across independently developed models* — and, on the textbook-anchored route,
   coincide with the published answer.
3. **Human sign-off.** A domain expert reviewed every released problem's statement,
   solver, and answer *in final form*; automated audits only raise suspects — **a human
   adjudicates every flag** (repair-and-reverify, or remove with variants).

**One-line version for the abstract/intro:** the corpus is
**textbook-derived, execution-verified, and expert-signed** — LLMs never author the
physics content, which is taken verbatim from 13 published textbooks.

---

## 2. Outcome-level evidence (the strongest card — results that quality defects would forbid)

Structural argument aside, cite **observations that could not occur if the problems were
low-quality.** This is harder than any process description.

| Evidence | Value (source) | What it implies |
|---|---|---|
| Frontier ceiling | strongest config **97.6%**, pass@3 **99.5%** (`CORE_RESULTS.md`) | jointly upper-bounds ill-posedness + GT error at a few percent; only **1** problem is solved by *no* model (`dn_6.8`) — few enough to inspect and justify by hand |
| Paraphrase robustness | harmful-direction **Δ ≤ +2.1 pt** (all \|Δ\| ≤ 3.9 pt), **none significant after Holm correction** (smallest p_Holm = 0.12) (`VARIANT_RESULTS.md`) | answers do not depend on surface phrasing; a defective statement would surface under rewording |
| Ranking stability | Spearman **ρ = 0.90–0.98** across core / numeric / paraphrase (`VARIANT_RESULTS.md` Table 3) | the measurement is stable under perturbation — incompatible with widespread defects |
| The audit machine has teeth | same machinery on the **external** AtmosSci-Bench MCQ set flags **69%** of templates at raw screening and, after adjudication, confirms **19 defective templates (190 problems, 28%)** of which **9 carry keys two independent solvers contradict** (`MCQ_AUDIT_SUMMARY.md`, `MCQ_DATASET_AUDIT.md`) | the verification pipeline *detects* defects at scale rather than rubber-stamping — the self-built corpus is what *survived* this same filter |
| Falsifiability | errata + removal log released (`pipeline/reports/`) | the error/removal rate is disclosed, not hidden |

> The MCQ line is the single most persuasive sentence available: the *identical* audit
> machinery, pointed at an external benchmark, tore it up. That is direct evidence the
> filter is not cosmetic.

---

## 3. Honest weaknesses — put these in Limitations (stating them earns trust)

1. **Correlated failures across models.** Independent *training* ≠ independent *errors*;
   cross-vendor agreement cannot be multiplied as independent probabilities. The hedges
   are already in place — say so explicitly:
   - most problems are anchored to the textbook's **printed** answer (a non-model source);
   - the agreed computation is re-checked **by hand** on both routes;
   - **convergent-error mining**: we actively search evaluation logs for *multiple models
     converging on the same wrong value* — the signature of correlated failure — and
     repair or remove confirmed cases. State that you *hunted this failure mode on
     purpose* (it is also the basis of the trap set).
2. **Selection bias on the cross-model route.** Where no printed answer exists, admission
   required independent models to agree on a value — so that subset cannot contain a problem
   the frontier could not solve at certification time. The textbook-anchored subset carries
   no such bound: its answers come from the book, whether or not any model reproduces them.
   State this plainly rather than arguing it away.

---

## 4. READY-TO-PASTE paragraphs (Dataset / Limitations)

> **Reliability of LLM-assisted construction.** LLMs serve throughout construction as
> *proposers*; no artifact enters the benchmark on a model's judgment alone. Admission
> rests on three mechanisms independent of trusting any single model: (i) *execution
> grounding* — every reference answer is the output of an executable solver, so ground
> truth is a reproducible computation, and the released corpus re-verifies end-to-end
> without a single LLM call; (ii) *independent agreement* — every answer is verified
> three-way, by models from three distinct developers solving independently and blind:
> where the textbook publishes an answer all three must reproduce it, and where it does
> not all three must agree with one another, the agreed computation being re-checked by
> hand in both cases; (iii) *human sign-off* — a domain expert reviewed every released
> problem's statement, solver, and answer in final form, and adjudicated every automated
> flag. A surviving error must therefore arise independently, as the same numerical
> value, across independently developed models — and, for textbook-anchored items,
> coincide with the published answer.
>
> Outcome-level checks corroborate the structure: the strongest configuration solves
> 97.1% of the core set (99.1% pass@3), bounding residual ill-posedness and ground-truth
> error at a few percent; accuracy is invariant under certified paraphrase (no model's
> shift survives Holm correction over the 16 configurations; harmful-direction Δ ≤ +2.1 pt)
> and rankings are preserved across all three sets (ρ = 0.90–0.98); and the identical
> audit machinery, applied to an external MCQ benchmark, flagged 69% of its templates at
> raw screening and, after adjudication, confirmed 19 defective templates (28% of the
> evaluated set) including 9 provably wrong answer keys — evidence that the pipeline
> detects defects rather than blessing its inputs. All solvers, audits, errata, and
> removal logs are released.

**Optional Limitations sentence (correlated failure + selection bias):**

> We do not claim the certifying models fail independently: agreement across
> independently developed models reduces, but does not eliminate, correlated error. We
> mitigate this by anchoring most problems to the textbook's printed answer, re-checking
> every agreed computation by hand, and actively mining evaluation logs for
> convergent wrong answers (the signature of shared error). We also state the selection
> effect rather than arguing it away: the cross-model route can only certify problems the
> frontier could already solve, so nothing admitted by that route exceeds frontier
> capability at certification time.

---

## 5. Wording discipline (enforce throughout the paper)

- ❌ "LLM-generated benchmark" → ✅ **"textbook-derived, execution-verified,
  expert-signed."** Problems are lifted verbatim from 13 published textbooks; the LLM
  authors no physics. Say this early and repeat it — it is the reviewer's most common
  misread.
- Whenever an LLM step is named, **name its gate in the same sentence** (deterministic
  check / cross-vendor agreement / human adjudication). Never let "we used a model to do
  X" stand alone.
- Consider a **touchpoint table**: each LLM touchpoint × what it proposes × what evidence
  admits it × the failure action (rewrite-not-patch / revert / remove). Systematic
  disclosure wins more trust than minimizing the LLM's role.

---

## Source map (for fact-checking every number above)

- 97.1% / pass@3 99.1% / 2 unsolved problems — `docs/results/CORE_RESULTS.md`
- paraphrase harmful-direction Δ ≤ +2.1 pt, none Holm-significant / ρ = 0.90–0.98 — `docs/results/VARIANT_RESULTS.md`
- MCQ 69% raw-flagged / 19 confirmed defective templates / 9 wrong keys — `docs/external_mcq/MCQ_AUDIT_SUMMARY.md`, `docs/results/MCQ_DATASET_AUDIT.md`
- solver contract + verify command — repository `README.md`, `eval/engine.py`, `eval.verify`
- convergent-error mining / traps — `docs/results/TRAP_RESULTS.md`, `pipeline/generate_traps.py`
- errata / removal / certification artifacts — `pipeline/reports/`
