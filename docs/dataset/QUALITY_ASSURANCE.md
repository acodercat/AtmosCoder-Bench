# Quality Assurance: Why the Problems Are Trustworthy

*A reviewer-facing statement of how AtmosCoder-Bench guards problem quality, and why
using frontier models to help build a benchmark that evaluates frontier models is not
circular. This section is the credibility summary for the whole dataset; §1–§11 of
`DATASET_CONSTRUCTION.md` give the mechanisms in detail.*

## The principle: propose-and-verify

AtmosCoder-Bench is built with a **propose-and-verify** architecture. Frontier models are
used only to **propose** candidate solvers, answers, and rephrasings. **Admission is
decided by criteria that are independent of any model's judgment.** Who proposes an
artifact is irrelevant to its quality; what matters is the chain of acceptance gates it
had to survive — and those gates are deterministic execution, anchoring to a
human-authored reference, cross-vendor independence, and human expert sign-off.

This rests on the standard asymmetry between generation and verification: **checking an
answer is independent of, and stronger than, producing it.** The credibility of the
benchmark therefore lives in the gates, not in the generators.

> **No artifact is admitted on a model's say-so.** Every released problem survives a chain
> of non-model acceptance gates: deterministic execution, reproduction of the textbook's
> own published answer, agreement across models from different developers, and human
> expert sign-off.

## The six pillars

Ordered from strongest to supporting.

**1. Execution-grounded ground truth — independently re-runnable.**
Each answer is *defined* by an executable, standard-library `solve()` whose output any
reader can re-run and confirm. **100% of released solvers reproduce their stored answers**
under `eval.verify` (core 436, numeric variants 1,730, paraphrase variants 2,180 — all at
5% tolerance). The ground truth is not "trust us" or "trust the model"; it is an
independently re-executable fact. This is a *stronger* guarantee than a
human-annotated benchmark, where one can only trust the annotator.

**2. Anchored to a human authority — the textbook's own answer.**
For books with a published answer, the reference is the **textbook's answer**, a
human-authored source vetted by decades of classroom use. All three blind model
solutions must *reproduce* that answer — the textbook defines the truth, the models
only have to match it.

**3. Cross-vendor independence — agreement as evidence, not echo.**
Every problem requires agreement across models from **three different developers**
(Anthropic, OpenAI, Google): against the textbook's answer where one exists, with one
another where none does. Because models from one developer share training data and
methods and thus make *correlated* errors, requiring agreement *across* developers
makes that agreement evidential rather than self-confirming. Solving is **blind** — no
model is ever shown the answer's value.

**4. Adversarial auditing that defaults to rejection.**
Defect auditing is designed to *find* faults — answers hard-coded into a solver, inputs the
code silently ignores, ill-posed or ungradable statements. LLM auditors are known to
**over-flag**, so they are used only to *raise suspects*, never to convict: **every flag is
adjudicated by a human expert**, and confirmed defects are repaired-and-reverified or
removed together with their variants.

**5. Human sign-off on every admitted problem.**
Model agreement only *proposes* a ground truth; before the value is frozen, the agreed
computation is **re-checked by hand** on both routes (*expert verification of ground
truth*), and a human expert then reads the statement, the solver, and the answer of
**every one of the 436 released problems** before admission, on the final released
(de-scaffolded) text (*final expert review*).

**6. Empirical discriminative validity — the reverse check.**
If the problems were model-fabricated and trivially solvable, frontier models would not
fail on them. In practice strong models still fail a substantial fraction and split on
hard items — an outcome incompatible with self-confirming, low-quality content. The
external AtmosSci-Bench comparison set, graded under the same contract, provides an
independent point of reference.

## Who proposes vs. what it must survive

The gates that decide admission are, in the main, **not** model judgment.

| Artifact | Proposed by | Acceptance gate it must survive | Gate is model judgment? |
|---|---|---|---|
| Reference solver | Claude Opus 4.8 (blind) | code must execute **and** its output must reproduce an independent ground truth | **No** — deterministic execution |
| Ground truth (book has an answer) | — | three blind solutions, one per developer, must all match the **textbook's published answer** + hand verification | **No** — textbook + execution |
| Ground truth (no published answer) | Opus 4.8 (blind) | three models from **different developers** independently solve and agree + hand verification | Partly — but cross-vendor + human |
| Problem soundness | — | deterministic structural checks + 3-model suspects → **human adjudication** | **No** — a human decides |
| Numeric / paraphrase variant | Opus 4.8 (rewrite) | deterministic fidelity checks + cross-vendor review + **human spot-audit** | Partly — deterministic + human |
| Difficulty / category label | model (for analysis only) | plays **no role in admission** | n/a |

## Reported quality figures

Only re-verifiable numbers; figures marked *(confirm)* are to be filled from the
construction logs before submission.

- Released solver reproducibility: **100%** (`eval.verify`, all three sets, 5% tolerance).
- Human expert review coverage of admitted ground truth: **436 / 436 (100%)**.
- Verification route split — textbook-anchored vs. cross-model:
  *(confirm split)*.
- Problems removed or repaired in defect auditing: *(confirm counts)*.
- Fraction of variants human spot-audited: *(confirm)*.

## One-paragraph statement (for the paper)

> AtmosCoder-Bench is built with a propose-and-verify architecture: frontier models are
> used only to **propose** candidate solvers, answers, and rephrasings, while admission is
> decided by criteria independent of any model's judgment. Ground truth is
> **execution-grounded** — defined by a standard-library solver whose output any reader can
> re-run and confirm (100% of released solvers reproduce their stored answers under
> `eval.verify`). Every answer is verified **three-way**, by models from three different
> developers solving independently and blind: where the textbook publishes an answer,
> all three must reproduce it; where it does not, all three must agree with one another
> — cross-developer agreement whose uncorrelated errors make it evidential rather than
> self-confirming. Each agreed computation is re-checked by hand before the value is
> frozen. Structural soundness is checked deterministically and adjudicated by a
> **human expert**, who approves every one of the 436 released problems before release. The benchmark's
> discriminative validity is corroborated empirically: frontier models still fail a
> substantial fraction — an outcome incompatible with model-fabricated, trivially-solvable
> content.
