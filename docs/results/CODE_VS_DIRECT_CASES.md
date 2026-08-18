# Code vs direct — what the protocol gap is made of

*Core set (436 problems), six models evaluated under both protocols, 3 runs each. Verbatim quotes are from stored `attempts[].response` fields.*

*Companion: [Core-set results](CORE_RESULTS.md).*

## Setup

Both protocols see the same problem and the same system prompt; they differ only in *who executes the final arithmetic*.

- **code** — the model writes an executable `solve()` returning `{"value", "unit"}` per quantity; Python computes the graded number.
- **direct** — the model shows its working in prose and reports each answer as `\boxed{<number> <unit>}`; the number and its unit are parsed and graded.

Both declare a unit with every answer, so the grader reconciles commensurate units (e.g. 0.12 m against a stored 4.7 inches) symmetrically in either protocol; the comparison isolates the reasoning vehicle, not the answer format.

## Headline

| model | code | direct | gap (code − direct) |
|---|--:|--:|--:|
| Qwen-3.6-27B (reasoning) | 88.5 | 85.5 | +3.1 |
| gpt-5.5 | 90.8 | 88.1 | +2.8 |
| gpt-5.5 (reasoning) | 97.6 | 95.6 | +2.1 |
| DeepSeek-V4-flash (reasoning) | 91.1 | 90.2 | +0.9 |
| Qwen-3.6-27B | 79.4 | 80.3 | −0.8 |
| DeepSeek-V4-flash | 81.7 | 83.1 | −1.5 |
| **mean** | | | **+1.08** |

**The two protocols are near-tied on accuracy** (+3.1 to −1.5). Only three of the six configurations separate them by more than their own run-to-run scatter, and all three favour code; the other three — including the two whose sign nominally favours prose — sit inside the noise. Those margins are 2–3 points on a 436-problem set, so this is not evidence that the code protocol is a broadly better *reasoning* vehicle; its real advantages are elsewhere — completion robustness on the hardest problems (§1) and token cost (§2) — while genuine reasoning-mechanism differences exist but are model-specific (§3). A residual set of direct-only failures traces to positional answer-matching against dataset entries whose answer key is shorter than the question (§4), a dataset property rather than a reasoning result.

---

## §1 Direct's structural burden: on the deepest problems the derivation cannot be delivered

**Under the direct protocol the derivation is the output, so its length scales with the computational depth of the problem — and on the deepest problems it exceeds what a serving stack will return. Code output is a short program regardless of depth.**

Three problems — `air_139` (3 sub-answers), `ry_4.6` (2,074-character statement, **11 sub-answers**), `ca_15.1` (single answer, high difficulty) — defeated **gpt-5.5-reasoning** under the direct protocol in 7 of their 9 problem-runs. `air_139` and `ry_4.6` failed to complete in **all three** runs; `ca_15.1` completed and passed in runs 1–2 and failed to complete in run 3. Every one of those 7 non-completions terminated in a mid-generation disconnect:

- ~15 invocations ≈ **100 API calls** per problem, across high-concurrency, low-concurrency, and fully-isolated conditions (a dedicated single request ran 7 min 23 s through six internal retries and still died);
- by contrast, three transient infrastructure failures on other problems (`air_145`, `snp_49`, `dn_15.2` — gateway-overload 503s) were each rescued by **one isolated retry in under two minutes**, cleanly separating "bad luck" from "cannot complete."

The same model solves all three under the code protocol (majority-of-3), cheaply:

```
                       code (gpt-5.5-reasoning, 3 runs)     direct (3 runs)
air_139                PASS PASS PASS   5.5–5.7k tokens      disconnect ×3
ry_4.6                 PASS PASS PASS   9.0–16.4k tokens     disconnect ×3
ca_15.1                fail PASS PASS   4.9–7.9k tokens      PASS PASS disconnect
```

In code mode an 11-part problem still returns ~40 lines of Python; the arithmetic happens in the interpreter. In direct mode the model must emit every derivation step in-band, and its reasoning trace on precisely the hardest problems grows past the serving limit. An answer that cannot be delivered is a failure, not an exclusion: these 7 records (all gpt-5.5-reasoning) are **counted as failures** in the direct accuracy, lowering it from 96.1/95.9/96.3 (were they excluded) to **95.6 ± 0.1**.

## §2 Direct costs more tokens, never fewer

The same structural burden shows up as tokens. Under identical o200k accounting on both sides (from [CORE_RESULTS.md](CORE_RESULTS.md) Appendix B):

| model | direct M/run | code M/run | ratio |
|---|--:|--:|--:|
| DeepSeek-V4-flash (reasoning) | 2.84 | 1.37 | **2.1×** |
| Qwen-3.6-27B (reasoning) | 9.85 | 5.43 | **1.8×** |
| DeepSeek-V4-flash | 0.55 | 0.36 | 1.5× |
| Qwen-3.6-27B | 1.00 | 0.74 | 1.4× |
| gpt-5.5 | 0.38 | 0.29 | 1.3× |
| gpt-5.5 (reasoning) | 0.42 | 0.35 | 1.2× |

Direct is never cheaper, and for models whose reasoning is billed in-band it costs about **twice** as much. Combined with §1 and the near-equal accuracy of the headline table, the honest summary is: **equal accuracy, higher cost, and a completion-failure mode on the hardest problems** — which together motivate the executable protocol as the primary evaluation setting.

## §3 Genuine reasoning-mechanism differences

Cases where the failure is in the reasoning itself, each verified in the logs with reproducible arithmetic. They share a theme: **prose reasoning substitutes something it can do for the exact computation it cannot — a closed-form guess for an equation with no closed form, a truncated relation for the full one, a magnitude for a signed value, a memorized shortcut for an iterative procedure — whereas code implements the exact computation, because a loop or an exact expression costs nothing extra to write.**

### §3.1 `snp_49` — an implicit equation, and what truncating the iteration looks like

This case illustrates the mechanism most legibly, but — unlike §3.2–§3.4 — **it is not a protocol-level effect**: `snp_49` grades 13/18 in code against 12/18 in direct, and 4/6 against 5/6 at the problem level, so read it as a picture of *how* prose fails when it fails, not as evidence that prose cannot do it. *Spherical particles carrying 2, 3, or 4 elementary charges have the same electrical mobility as a singly-charged 100 nm particle; find their diameters.* Equal mobility gives n·Cc(D)/D = Cc(D₀)/D₀, where the Cunningham slip correction Cc(D) itself depends on D — an **implicit equation in D with no closed-form solution**. Stored answers: **151.6 / 196.4 / 238.1 nm**.

Under the code protocol the models that root the equation numerically land on the exact values:

```python
def cunningham(D_nm): ...                     # Cc(D)
def mobility_difference(D, n):
    return n*cunningham(D)/D - cunningham(D0)/D0
while mobility_difference(hi, n) > 0.0: ...    # bracket, then
for _ in range(100): ...                       # bisection → 151.5 / 196.3 / 237.9 ✓
```

But the iteration is not free in code either: **the two Qwen configurations write the same single-pass approximation into their programs that they write in prose** — Qwen-3.6-27B (reasoning) returns 160.7 / 160.3 in code mode runs 1–2 against 160.0 in prose, and non-reasoning Qwen never lands it (0/3). Writing a program does not by itself supply the method; it only removes the arithmetic barrier for a model that already has one.

Under the direct protocol all four models below write the correct Cc formula, then — unable to iterate in prose — each stops at a *different* single-pass approximation. In **run 1**, three of the four miss, with no two agreeing:

```
gpt-5.5                        178.7   254.1   328.1     (0 iteration steps in the trace)
DeepSeek-V4-flash (reasoning)  161.8   219.7   275.9     (0)
Qwen-3.6-27B (reasoning)       160.0   216.0   270.0     (mentions iterating, does not)
gpt-5.5 (reasoning)            151.7   196.6   238.6  ✓  (the one that carried it through)
```

The first sub-answer alone spreads **151.7–178.7 nm across the four models in that run** — the three misses are not *wrong* derivations but *truncated* ones, each halting where prose arithmetic runs out. The mechanism is real but **run-unstable rather than problem-fatal**: in other runs most of the same models do carry a few fixed-point iterations through in prose and land the answer, so at the problem level `snp_49` grades code 4/6 vs direct 5/6 (majority-of-3) — the truncation shows up as run-to-run flakiness (e.g. DeepSeek-V4-flash (reasoning) F/P/P, Qwen-3.6-27B (reasoning) F/P/P), not as a deterministic prose failure. `10.3` (a five-part stratospheric Chapman-cycle chain, code 16/18 vs direct 13/18 at the instance level) and `ry_8.1` (continuous-collection drop growth, 13/18 vs 9/18) show the same shape with a persistent instance-level deficit.

**Trend, not yet a significant law.** Partitioning all 436 problems by whether the reference solver contains a numerical loop (`while`, or a counted `for … in range` loop — a proxy for "the solution must be executed, not written"), the mean code−direct gap is **+2.6 pt on the 17 iteration problems vs +0.4 pt on the other 419** — a 7× concentration in the expected direction. With only 17 iteration problems (and a 6-model panel) the difference is not statistically separable from zero (Welch t = 0.82, df = 7, p ≈ 0.44), so this is reported as a mechanism with a directional trend, not a demonstrated quantitative law; the per-case evidence above is the load-bearing part.

### §3.2 `holton_56` — prose truncates the dispersion relation

*Derive the Rossby wave speed for a homogeneous ocean (depth 4 km, 45°, wavelength 10,000 km).* Stored answer **−24.31 m s⁻¹**, from the full dispersion relation c = −β/(k² + f₀²/gH).

DeepSeek-V4-flash in direct mode fails all three runs, converging on **41.0**, verbatim:

> \[ c = \frac{\beta}{k^2} = \frac{1.618\times10^{-11}}{3.94784\times10^{-13}} \approx 40.98\ \text{m/s}. \] … \[ \boxed{41.0\ \text{m/s}} \]

It uses **c = β/k²** — dropping both the stratification term f₀²/gH and the sign. The dropped term is not negligible: at the given wavelength gk² = 3.87×10⁻¹² and f₀²/H = 2.66×10⁻¹², so f₀²/gH *dominates* k²; the problem supplies the wavelength precisely so this can be checked. Keeping both terms yields −24.3 m s⁻¹.

The same model under the code protocol writes the full relation and passes, 3/3:

```python
c = -beta / (k**2 + f**2/(g*depth))      # → -24.3115
```

**This is more than one anecdote.** Across all direct responses, those containing approximation language (*negligible*, *neglect*, *much smaller than*, *to first order*, `≪`, *long-wave limit*) are enriched among failures:

| direct outcome | responses | contain approximation language |
|---|--:|--:|
| passed | 6,837 | 337 (**4.9 %**) |
| failed | 1,004 | 169 (**16.8 %**) |

(Population: all direct records across the six models × 3 runs, excluding the 7 non-completions; a record counts if any of its stored responses contains one of the listed markers, case-insensitive.) Failures are **3.4× as likely** to contain approximation language (two-proportion z = 14.3, p < 10⁻⁴). The test is correlational — approximating may be a symptom of a hard problem rather than a cause — but the direction is consistent with the mechanism and it is a population-level signal, not a single case.

**Scope caveat:** `holton_56` itself is not a universal failure. gpt-5.5-reasoning evaluates the full relation in prose and passes 3/3; the failure is model-specific.

### §3.3 `air_167` — prose reports magnitudes; the code contract forces a committed sign

*Fickian moisture flux toward a cloud droplet: given the gradient (part a, +7.5), find the kinematic flux (part b).* Stored answer **−1.5 × 10⁻⁴** — Fick's law, F = −D·∂r/∂z, flux *down* the gradient.

Four of six models fail part (b) in **all three runs, all twelve answers identically +1.5 × 10⁻⁴** — right magnitude, dropped sign; the two gpt-5.5 variants report the signed value 6/6. The smoking gun is in Qwen-3.6-27B's *code* attempt, where the model narrates its own choice:

```python
# Kinematic moisture flux using Fickian diffusion: F = -D * dr/dx
# The flux is down the gradient, so we take the magnitude
kinematic_flux = diffusivity_m2_per_s * dr_dx     # sign dropped → fail
```

It writes Fick's law *with* the minus sign in the comment, then deliberately reports the magnitude. Across protocols, **sign survival is 14/18 code runs vs 6/18 direct runs**: the code contract — one committed numeric value per quantity — suppresses the magnitude-reporting habit (the reasoning variants of DeepSeek and Qwen keep the sign 3/3 in code while dropping it 3/3 in prose), though it does not eliminate it. The within-model asymmetry between modes is the observation: the same model commits to the signed value when writing a program and defaults to a magnitude when writing prose.

### §3.4 `air_154(b)` — prose reaches for the wrong shortcut; code iterates

*Fog formation: to what altitude must a surface layer (20 °C, RH 68 %) be lifted to form upslope fog?* Stored answer **0.7628 km** (the lifting condensation level).

Direct-mode failures (gpt-5.5: 0.61; both Qwen variants: 0.62) all made the same physics error, verbatim from Qwen:

> z_LCL = ΔT / Γ_d = 6.08 K / 9.8 K km⁻¹ ≈ **0.620 km**

Dividing the dew-point depression by the **dry-adiabatic lapse rate alone** — forgetting that the dew point also falls with height (≈ 2 K km⁻¹), so the closure rate is ≈ 8 K km⁻¹, i.e. the standard z ≈ 0.125 km per K, giving 0.76 km. The same models under the code protocol get it right by two different routes:

```python
# gpt-5.5 (code, PASS): exact treatment — numerical root-finding on saturation
def f_lcl(z_m): ...
while f_lcl(hi) > 0: ...

# Qwen-3.6-27B-reasoning (code, PASS): the correct standard formula
z_LCL_m = 125.0 * delta_T
```

The pair is the point: **in prose the model cannot iterate, so it substitutes a memorized one-liner — and picks the wrong one; in code it either implements the correct standard formula or simply iterates the exact condition**, because a `while` loop costs nothing. Scope caveat: non-reasoning Qwen uses the wrong formula in code as well (fails both modes) — the mechanism separates the protocols only for models that possess the correct knowledge (gpt-5.5: code 3/3 vs direct 0/3; Qwen-reasoning: code 3/3 vs direct 0/3).

## §4 Answer-selection failures that trace to dataset entries, not reasoning

A distinct set of direct-only failures is not a reasoning difference at all. The grader matches boxed answers to sub-answers by position, keeping the trailing N when a model emits more boxes than the dataset stores. This inverts when a model answers **more of the question than the answer key covers** — and the responsible entries are dataset defects, not model errors:

| id | code | direct | dataset entry |
|---|:--:|:--:|---|
| `dn_10.36` | 6/6 | 0/6 | asks three quantities, stores two — all six models produce the same three correct numbers and are graded on the wrong two |
| `4.6` | 6/6 | 0/6 | asks three Rossby numbers, stores two |
| `jacob_2.1` | 6/6 | 0/6 | asks scale height *and* an Earth comparison, stores one answer |
| `3.2` | 6/6 | 2/6 | second sub-question is symbolic (an expression for the exported fraction); models that box the formula have a stray digit pulled from it, while the two that box only the numeric part pass |

The code protocol never encounters these — but not because the solver produces fewer values: on all three entries it returns **three**, exactly as the question asks. What differs is the alignment rule. `verify_solver` matches each expected sub to the returned entry **with the same key**, falling back to **position counted from the front**, so `dn_10.36` (`1`,`2`) and `jacob_2.1` (`1`) are graded on their correctly-keyed values and `4.6` — whose stored keys are `a`/`b` and so match nothing — on the leading two. A boxed answer carries no key, so the direct grader has only position, and it counts from the end. **These rows measure dataset completeness, not model reasoning.** They are noted here so the raw direct accuracy is read with the right attribution; the affected entries are candidates for a dataset revision (add the missing sub-answers or split the multi-part statements).

## What to claim

1. **The code-vs-direct accuracy gap is small** (mean +1.08; range +3.1 to −1.5), and only half the panel resolves it above run-to-run noise — those three all favour code. It is still not evidence that executable code is a broadly superior *reasoning* vehicle: the resolvable margins are 2–3 points on a 436-problem set.
2. **Code's demonstrable advantages are completion robustness and cost**: the direct protocol cannot complete the computationally deepest problems for the strongest reasoning model (7 of the 9 runs over three such problems), and it costs 1.2–2.1× the tokens for equal-or-lower accuracy. Output length is decoupled from computational depth in code and coupled to it in prose.
3. **Genuine prose-specific failure modes exist** — equation truncation, magnitude-for-sign substitution, shortcut-for-iteration substitution — each verified with logs and a population-level or within-model asymmetry, and each model-specific rather than universal.
4. **A residue of direct-only failures is dataset completeness, not reasoning** (§4), and should be attributed as such.

## Reproducing

Per-problem evidence is in `experiments/core_{code,direct}/{model}.run{N}.json`: `details` holds per-sub expected vs actual, `attempts[].response` holds the verbatim output quoted above. The 7 non-completions carry the transport error and the failure-counting policy inline (`error_as_fail`).
