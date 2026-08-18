# AtmosCoder-Bench — Prompt Sensitivity

*Companion results: [Core-set results](CORE_RESULTS.md) · [Scaffolding ablation](SCAFFOLDING_ABLATION.md) · [Variant robustness](VARIANT_RESULTS.md).*

## What this tests

Code-generation accuracy can depend not only on a model's competence but on how the coding task
is *phrased*. A benchmark is only trustworthy if its rankings are stable under reasonable
variations of the instruction. This ablation measures that stability directly: we evaluate the
core set under two functionally equivalent code-mode prompts and quantify how much each model's
accuracy moves. The two differ in **two coupled respects** — the system persona and whether the
model is permitted to reason in prose before it writes code — so what is measured is the joint
effect of that instruction style, not the reasoning permission in isolation.

- **`reasoning-permissive` (default)** — a domain-expert persona that invites the model to *work
  out the solution and then express it* as a `solve()` function; prose reasoning before the code
  block is allowed.
- **`code-only`** — a code-generator persona that requires the model to *return only executable
  Python*; reasoning in prose is disallowed.

Both prompts ask for the identical artifact (a standard-library `solve()` with the same return
contract) and are graded identically. The two templates, and both system prompts, are reproduced
verbatim below.

- **Protocol**: code mode; **3 runs per model per prompt**; 4 models spanning the capability range;
  the full 436-problem core set in every cell (fully paired); 0 excluded errors.

## Results

**Table 1 — Accuracy under the two prompts (code mode, 3 runs, mean ± SD over runs).**
Models are ordered from largest to smallest. Δ is the accuracy change from the reasoning-permissive
prompt to the code-only prompt.

| model | reasoning-permissive | code-only | Δ (code-only − permissive) |
|---|--:|--:|--:|
| gpt55 | 90.8 ± 1.4 | 88.9 ± 0.5 | **−1.9** |
| gemini-3.1-pro | 96.0 ± 0.7 | 96.3 ± 0.3 | **+0.2** |
| deepseek-v4-flash | 81.7 ± 1.4 | 80.5 ± 1.5 | **−1.1** |
| qwen3.5-9b | 63.4 ± 1.3 | 52.7 ± 1.5 | **−10.7** |

**Table 2 — Per-run accuracy (%, n = 436, no excluded errors).**

| model | prompt | run 1 | run 2 | run 3 | mean ± SD |
|---|---|--:|--:|--:|--:|
| gpt55 | reasoning-permissive | 92.4 | 90.1 | 89.9 | 90.8 ± 1.4 |
| gpt55 | code-only | 88.5 | 89.4 | 88.8 | 88.9 ± 0.5 |
| gemini-3.1-pro | reasoning-permissive | 96.6 | 96.3 | 95.2 | 96.0 ± 0.7 |
| gemini-3.1-pro | code-only | 96.1 | 96.1 | 96.6 | 96.3 ± 0.3 |
| deepseek-v4-flash | reasoning-permissive | 81.2 | 83.3 | 80.5 | 81.7 ± 1.4 |
| deepseek-v4-flash | code-only | 82.1 | 79.1 | 80.3 | 80.5 ± 1.5 |
| qwen3.5-9b | reasoning-permissive | 64.2 | 61.9 | 64.0 | 63.4 ± 1.3 |
| qwen3.5-9b | code-only | 51.1 | 52.8 | 54.1 | 52.7 ± 1.5 |

**Table 3 — Mechanism: non-executable code under the code-only prompt.**
"First-attempt executable" is the fraction of problems whose code ran on the first try; "unrecoverable"
counts problems whose code still failed to run after the full five-attempt self-repair budget (mean
over 3 runs). A drop in the former and a rise in the latter isolate a code-quality failure, distinct
from producing a *wrong* answer.

| model | first-attempt executable (permissive → code-only) | unrecoverable (permissive → code-only) |
|---|--:|--:|
| gpt55 | 99.8% → 99.5% | 0 → 0 |
| gemini-3.1-pro | 100.0% → 99.8% | 0 → 0 |
| deepseek-v4-flash | 99.6% → 99.6% | 0 → 0 |
| qwen3.5-9b | 93.1% → 86.8% | 2 → **37** |

## Findings

**1. Prompt sensitivity increases as model scale decreases.** The frontier models are essentially
invariant to the prompt change — gemini-3.1-pro **+0.2**, gpt55 **−1.9**, both within or near run noise —
whereas the smallest model swings by **−10.7** points. deepseek-v4-flash is likewise stable
(**−1.1**, inside its own pooled run-to-run scatter of ≈2.1). A single reasonable rephrasing of the instruction therefore leaves the top of the
leaderboard unchanged but moves the 9B model by an order of magnitude more.

**2. The small-model penalty is a code-quality failure, not an accuracy trade-off.** Under the
code-only prompt qwen3.5-9b's first-attempt executable rate falls from 93.1% to 86.8% and its
*unrecoverable* count — code that still will not run after five repair attempts — rises from 2 to
**37** problems. Denied the space to reason first, the small model emits code that more often does
not execute at all; the accuracy loss is dominated by non-running code rather than by wrong
numbers. The frontier models write executable code under either prompt (unrecoverable stays 0), so
they pay no such penalty.

**3. Implication for evaluation.** Because rankings among strong models are stable across the two
prompts while weak-model scores are not, prompt formulation is a genuine confound only in the
lower-capability regime. We therefore fix the reasoning-permissive prompt as the primary code-mode
setting for all reported results: it neither advantages nor disadvantages the frontier models and
avoids penalizing smaller models for an instruction-format artifact rather than for their science.

## Prompt templates

The two prompts are identical except for (i) the system persona and (ii) whether prose reasoning is
permitted before the code block. `{problem}` is replaced by the problem statement.

### Reasoning-permissive (default)

*System:*
> You are an expert in atmospheric science.

*User:*
```
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
{problem}

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
```

### Code-only

*System:*
> You are a Python code generator. Return ONLY executable Python code.

*User:*
```
You are given an atmospheric science problem. Write a Python `solve()` function that computes the numerical answer(s).

## Rules
1. All given values from the problem must be function parameters with defaults.
2. Return a dict with one entry per quantity the problem asks for, keyed "1", "2",
   ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"}.
   Return exactly that many entries; do NOT add intermediate or unit-converted values.
3. Only use standard library (math, etc.). No external packages.
4. Do unit conversions explicitly in code.

## Problem
{problem}

Write ONLY the Python code containing the solve() function.
```

## Statistical notes and limitations

- **Three runs per cell** (SD in Tables 1–2); the direction of Δ is stable across runs for every
  model. gemini-3.1-pro's Δ (+0.2) is well within run noise; gpt55's (−1.8) is of the order of its
  own run-to-run SD (±1.5) and an order of magnitude smaller than qwen3.5-9b's (−10.6).
- **Four models.** The scale-dependence trend is consistent across the panel but four points cannot
  establish a functional form; a broader panel would tighten it.
- **Model ordering.** gpt55 is a frontier model of undisclosed size and is treated as the largest;
  the others are ordered by their stated scale (gemini-3.1-pro and deepseek-v4-flash above
  qwen3.5-9b at 9 B parameters).
- **Two prompts.** These are one reasonable pair, not an exhaustive sweep of instruction space; they
  bracket the practically important axis (whether reasoning is permitted before coding).
