# Evaluation prompts

*Every prompt the harness sends, reproduced verbatim from `eval/protocols.py`. This is the methods-section reference: what the model is told, and nothing else is sent.*

A model sees **only the problem text**. No formula, no expected answer, no hint about the number of significant figures, and no worked example is ever included. The system prompt is constant within a run and stored once in that run's `metrics.system`; the user prompt is stored per call in `attempts[].prompt`, so any measurement can be checked against what follows.

`{problem}` is replaced by the problem statement. In the source these templates are Python format strings, so a literal brace is written `{{`; below they are shown as the model receives them, with single braces. Rendered examples of both protocols on a real problem are in [`../evidence/air_167_signed_flux.md`](../evidence/air_167_signed_flux.md).

## Protocol summary

| `--mode` | what the model produces | what is graded | retry budget |
|---|---|---|---|
| `code` | a Python `solve()` function | the value the function **returns when executed** | 5 content attempts |
| `direct` | prose working, answers in `\boxed{}` | the **number the model reports** | 5 content attempts |
| `agent` | cells in a stateful Python REPL, ending in `submit()` | the submitted values | 10 interpreter turns |

"Content attempts" count only the model's own output being ungradable — code that will not run, or prose with no `\boxed{}`. Each such failure is fed back once (the repair prompts below) and re-asked as a fresh single-turn call; no chat history is sent. A wrong-but-runnable answer is a finished measurement and is never retried. API and infrastructure failures are retried separately and are not counted here.

---

## `code`

### System prompt — `code`

~~~~
You are an expert in atmospheric science.
~~~~

### User prompt — `code`

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras. Each "value" must be a single number, never a list; if one part asks for several values, give each its own entry.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
{problem}

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

*One sentence in Rule 2 — "Each "value" must be a single number, never a list; if one part asks for several values, give each its own entry." — was added after the stored runs; the measurements in `experiments/` were produced without it.*

### Repair prompt — `code`

Sent when the returned code fails to execute. `{code}` is the code that was run and `{error}` the interpreter's message.

~~~~
Your solve() function failed to run. Fix the bug and return the corrected function.

## Problem
{problem}

## Your code
{code}

## Error when it was executed
{error}

Return the COMPLETE corrected solve(): a dict keyed "1".."N" in the order asked, each
{"value": <number>, "unit": "<unit>"}, standard library only. Put all arithmetic in the function; give the corrected solve() in a single ```python code block.
~~~~

---

## `direct`

### System prompt — `direct`

~~~~
You are an expert in atmospheric science.
~~~~

### User prompt — `direct`

~~~~
You are given an atmospheric science problem. Work out the solution and compute the numerical answer(s) yourself.

## Rules
1. Use the given values, supplying any standard physical constants you need.
2. Give one value per quantity asked, in the order asked — exactly that many.
3. Do the unit conversions explicitly.

## Problem
{problem}

The graded answer is the number you report, so do the arithmetic yourself. Show your working, then give each final answer on its own line as \boxed{<number> <unit>} — the number followed by its unit, e.g. \boxed{4.7 inches} or \boxed{1.5e-3 m s^-1} (write "dimensionless" if it has no unit). Any correct unit is accepted; the answer is converted before grading. If the problem asks for N quantities, give exactly N boxes in that order.
~~~~

### Repair prompt — `direct`

Sent when no `\boxed{}` value could be parsed. `{answer}` is the previous response.

~~~~
Your previous answer did not contain a \boxed{} value, which is required to grade it.

## Problem
{problem}

## Your previous answer
{answer}

State EACH requested quantity's final numerical value, in the order asked, each on its own
line as \boxed{<number> <unit>} — the number followed by its unit (write "dimensionless"
if it has none).
~~~~

---

## `agent`

### System prompt — `agent`

~~~~
You are an expert in atmospheric science working with a stateful Python interpreter. Solve the problem step by step: run code to compute and verify intermediate results, then submit the final answer.
~~~~

### User prompt — `agent`

~~~~
You are given an atmospheric science problem. Solve it using a stateful Python interpreter that keeps your variables between turns.

## How to work
1. Each turn, reason briefly, then write ONE ```python code block. It is executed and you see its output before the next turn.
2. Use print() to inspect intermediate values and check your work — variables persist across turns, so you can build up and correct the solution.
3. Standard library only (math, etc.). Do every unit conversion explicitly in code.
4. When you are confident, call submit(answer) inside a code block, where answer is a dict with one entry per quantity asked, keyed "1".."N" in the order asked, each {"value": <number>, "unit": "<unit>"}.
   Example: submit({"1": {"value": rho, "unit": "kg/m3"}})
   submit() ends the task; the submitted values are graded.

## Problem
{problem}
~~~~

There is no repair prompt: the interpreter's output is the feedback, and the loop ends when the model calls `submit()` or the turn budget runs out.

---

## Controlled ablations

Two knobs vary the wording without touching the protocol, for the sensitivity experiment in [`../results/PROMPT_SENSITIVITY.md`](../results/PROMPT_SENSITIVITY.md). Both are applied to a shallow copy of the shared protocol object and recorded in the run's `metrics`.

### `--system` · `SYSTEM_PRESETS`

| preset | text |
|---|---|
| `expert` | You are an expert in atmospheric science. |
| `coder` | You are a Python code generator. |
| `coder-strict` | You are a Python code generator. Return ONLY executable Python code. |

`expert` is the default and is what every experiment in `docs/results/` uses, except the code-only arm of the prompt ablation, which uses `coder-strict`.

### `--prompt` · `PROMPT_PRESETS`

`original` is the default and is byte-identical to the `code` user prompt above. `restrictive` removes the permission to reason and asks for code only:

**`original`**

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras. Each "value" must be a single number, never a list; if one part asks for several values, give each its own entry.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
{problem}

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

**`restrictive`**

~~~~
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
~~~~

Either flag also accepts a literal string instead of a preset name. The preset swaps assert on their anchor phrases, so a mis-edit fails loudly rather than silently producing a non-variant.

---

## Reproduction

```bash
uv run python -m eval.runner --model kimi-k2.6 --set core --exp-id core_code
uv run python -m eval.runner --model gemini --mode direct --exp-id core_direct
uv run python -m eval.runner --model gpt55 --mode agent --exp-id core_agent
uv run python -m eval.runner --model kimi-k2.6 --set core --prompt restrictive --system coder-strict \
    --exp-id core_code_restrictive
```

The prompts above are the single source of truth: `eval/protocols.py` holds them and the runner sends nothing else.

