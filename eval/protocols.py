"""Answer protocols — *how* a model is asked to answer a problem, and how its
response is turned into a gradable results dict.

Every protocol feeds the same grader (`eval.engine.verify_solver`): per sub-part,
relative error <= tolerance against the known answer. Only the answer *modality*
differs, which is exactly the variable the code-vs-direct comparison isolates.

- `code`   — the model writes a `solve()` function; we execute it. Arithmetic is
             offloaded to a deterministic interpreter, so the score reflects
             whether the model knows the *method*; grading is reproducible.
- `direct` — the model reasons in prose and reports its final answer(s) as
             `\\boxed{<number>}` (the open-ended-QA paradigm). Same problems,
             same numeric grading.
- `agent`  — an iterative code-interpreter: the model runs code in a persistent
             session, sees each cell's output, refines over several turns, and
             calls `submit()` with the final answer. Trades more interaction for
             the chance to check intermediate results; graded identically.

Each protocol runs one problem via `run_episode(model, problem)`, returning an
:class:`Episode`. The default is the single-shot generate->grade->repair loop;
`agent` overrides it with the multi-turn loop. The single-shot path turns one
response into a gradable form via `attempt(text, problem)` -> :class:`Attempt`:
  results  — dict[sub -> {"value", "unit"}] handed to the grader ({} if ungradable)
  error    — None, or a short reason the response was ungradable
  note     — optional diagnostics (e.g. how many boxes were parsed)

The runner persists ``attempts`` — a per-CALL log (one ``{"prompt","response",
"outcome"}`` per stateless ``model.generate`` call) plus ``num_attempts`` — so the
Attempt only needs to carry the parsed/gradable form, not the text to log (the
``system`` prompt, constant across calls, lives once in the experiment metrics).
Note: ``attempts`` is NOT a chat transcript; the repair loop re-prompts single-turn
(it re-injects the problem+code+error), it does not send history to the API.
"""

import re
from dataclasses import dataclass, field

from eval.engine import run_solver, extract_code
from eval.models import ModelError, PromptTooLongError
from eval.sandbox import CodeSession

# --- code protocol -----------------------------------------------------------
CODE_SYSTEM = "You are an expert in atmospheric science."
CODE_PROMPT = """You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {{"value": <number>, "unit": "<unit>"}} — exactly that many entries, no intermediate or unit-converted extras. Each "value" must be a single number, never a list; if one part asks for several values, give each its own entry.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
{problem}

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block."""

# Feedback prompt for the code self-repair loop: the failed code + its execution
# error are handed back so the model can fix the bug and try again.
CODE_REPAIR = """Your solve() function failed to run. Fix the bug and return the corrected function.

## Problem
{problem}

## Your code
{code}

## Error when it was executed
{error}

Return the COMPLETE corrected solve(): a dict keyed "1".."N" in the order asked, each
{{"value": <number>, "unit": "<unit>"}}, standard library only. Put all arithmetic in the function; give the corrected solve() in a single ```python code block."""

# --- direct protocol ---------------------------------------------------------
DIRECT_SYSTEM = "You are an expert in atmospheric science."
DIRECT_PROMPT = """You are given an atmospheric science problem. Work out the solution and compute the numerical answer(s) yourself.

## Rules
1. Use the given values, supplying any standard physical constants you need.
2. Give one value per quantity asked, in the order asked — exactly that many.
3. Do the unit conversions explicitly.

## Problem
{problem}

The graded answer is the number you report, so do the arithmetic yourself. Show your working, then give each final answer on its own line as \\boxed{{<number> <unit>}} — the number followed by its unit, e.g. \\boxed{{4.7 inches}} or \\boxed{{1.5e-3 m s^-1}} (write "dimensionless" if it has no unit). Any correct unit is accepted; the answer is converted before grading. If the problem asks for N quantities, give exactly N boxes in that order."""

# Feedback prompt when the model answered but produced no \boxed{} value to grade.
DIRECT_REPAIR = """Your previous answer did not contain a \\boxed{{}} value, which is required to grade it.

## Problem
{problem}

## Your previous answer
{answer}

State EACH requested quantity's final numerical value, in the order asked, each on its own
line as \\boxed{{<number> <unit>}} — the number followed by its unit (write "dimensionless"
if it has none)."""

# --- agent protocol ----------------------------------------------------------
AGENT_SYSTEM = ("You are an expert in atmospheric science working with a stateful Python "
                "interpreter. Solve the problem step by step: run code to compute and verify "
                "intermediate results, then submit the final answer.")
AGENT_PROMPT = """You are given an atmospheric science problem. Solve it using a stateful Python interpreter that keeps your variables between turns.

## How to work
1. Each turn, reason briefly, then write ONE ```python code block. It is executed and you see its output before the next turn.
2. Use print() to inspect intermediate values and check your work — variables persist across turns, so you can build up and correct the solution.
3. Standard library only (math, etc.). Do every unit conversion explicitly in code.
4. When you are confident, call submit(answer) inside a code block, where answer is a dict with one entry per quantity asked, keyed "1".."N" in the order asked, each {{"value": <number>, "unit": "<unit>"}}.
   Example: submit({{"1": {{"value": rho, "unit": "kg/m3"}}}})
   submit() ends the task; the submitted values are graded.

## Problem
{problem}"""

_BOXED = re.compile(r"\\boxed\s*\{")
_NUM = re.compile(
    r"[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|"  # 7,387 / 12,345.6
    r"[-+]?\d*\.?\d+\s*(?:[eE]|×\s*10\^?|x\s*10\^?|\\times\s*10\^?|\\cdot\s*10\^?)\s*\{?[-+]?\d+\}?|"  # sci / latex
    r"[-+]?\d*\.?\d+"  # plain
)


def _balanced_boxed(text: str) -> list[str]:
    """Brace-balanced contents of every ``\\boxed{...}``, in document order."""
    contents = []
    for match in _BOXED.finditer(text):
        position, depth, chars = match.end(), 1, []
        while position < len(text) and depth:
            char = text[position]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    break
            chars.append(char)
            position += 1
        contents.append("".join(chars))
    return contents


def _parse_number(boxed: str):
    """Pull a single float out of boxed content like ``1.5\\times10^{-3} N``."""
    match = _NUM.search(boxed)
    if not match:
        return None
    token = re.sub(r"\s*(?:×\s*10\^?|x\s*10\^?|\\times\s*10\^?|\\cdot\s*10\^?)\s*", "e", match.group(0))
    token = token.replace("{", "").replace("}", "").replace(",", "").replace(" ", "")
    try:
        return float(token)
    except ValueError:
        return None


def _parse_unit(boxed: str) -> str:
    """Pull the unit out of boxed content like ``4.7 inches`` or ``1.5\\times10^{-3} m s^-1``.

    The direct prompt asks for ``\\boxed{<number> <unit>}``; grading needs the unit so the
    engine can reconcile an answer given in a different but commensurate unit (the code
    protocol gets this for free from its ``{"value", "unit"}`` contract). Everything the
    number match consumed is dropped and the remainder is de-LaTeX'd; an empty or
    "dimensionless" remainder yields "".
    """
    match = _NUM.search(boxed)
    if not match:
        return ""
    unit = (boxed[:match.start()] + " " + boxed[match.end():]).strip()
    unit = re.sub(r"\\(?:mathrm|text|rm|mbox|textrm|operatorname)\s*\{([^}]*)\}", r"\1", unit)
    unit = re.sub(r"\\(?:,|;|:|!|quad|qquad|,)", " ", unit)
    unit = unit.replace("$", "").replace("~", " ").replace("\\", "")
    unit = unit.replace("{", "").replace("}", "").replace("−", "-").replace("·", " ")
    unit = re.sub(r"\s+", " ", unit).strip(" .,:;()[]")
    if unit.lower() in {"", "dimensionless", "unitless", "none", "n/a", "-", "ratio"}:
        return ""
    return unit


def _call_log(prompt: str, completion, outcome: str) -> dict:
    """One per-call log entry: the prompt sent, the model's response and outcome,
    plus that call's token account under ``usage``. ``reasoning`` (the thinking-trace
    text) is included only when the model emitted one; ``usage`` is always present and
    every one of its fields is an int, with ``usage.reasoning_tokens`` 0 when the
    provider reported no count. Episode
    totals are summed from these entries (see :class:`Episode`)."""
    entry = {"prompt": prompt}
    if completion.reasoning:
        entry["reasoning"] = completion.reasoning
    entry["response"] = completion.text
    entry["outcome"] = outcome
    entry["usage"] = completion.usage
    return entry


@dataclass
class Attempt:
    """A response turned into a gradable form (or a reason it could not be)."""
    results: dict = field(default_factory=dict)  # sub -> {"value", "unit"}
    error: str | None = None                     # set iff ungradable
    note: str | None = None                      # optional diagnostics
    code: str | None = None                      # the code that was run (for repair feedback)


@dataclass
class Episode:
    """The result of running one protocol episode on one problem.

    ``attempts`` is a per-CALL log, NOT a chat transcript. Each model call is an
    independent, STATELESS single-turn request — the repair loop does not send
    conversation history to the API; it re-injects the problem + failed code +
    error into a fresh standalone prompt (see ``repair_prompt``). So each entry is
    exactly what one ``model.generate`` call sent and got back.
    """
    attempt: Attempt           # final gradable outcome (results) or a content failure (error)
    attempts: list[dict]       # one entry per model call (see _call_log) — the token source of truth
    note: str | None = None

    @property
    def usage(self) -> dict:
        """Episode token account, summed across calls from each attempt's ``usage``
        (the attempts are the source of truth). ``prompt_tokens`` is re-counted per
        stateless call; ``completion_tokens`` includes any reasoning; ``reasoning_tokens``
        is 0 when no call reported one (non-reasoning model or a provider that omits the
        count), never null. This aggregate is provisional: ``ExperimentStore.add`` replaces
        the record's ``usage`` with the uniform o200k recount of the stored text."""
        prompt = sum(call["usage"]["prompt_tokens"] for call in self.attempts)
        completion = sum(call["usage"]["completion_tokens"] for call in self.attempts)
        reasoning = sum((call["usage"].get("reasoning_tokens") or 0) for call in self.attempts)
        return {"prompt_tokens": prompt, "completion_tokens": completion,
                "total_tokens": prompt + completion,
                "reasoning_tokens": reasoning}


class Protocol:
    """How a model is asked to answer, and how its response becomes a gradable Attempt.

    ``run_episode`` owns the whole interaction for one problem. The default below is
    the SINGLE-SHOT loop: build a prompt, generate once, grade; on an ungradable
    *content* output, feed it back via ``repair_prompt`` and retry, up to
    ``max_attempts``. The agent protocol overrides it with a multi-turn loop.
    Transient API errors are absorbed per call in ``_generate`` (blind retry,
    uncounted); a content try only counts once the model has produced output.
    """
    name: str
    system: str
    max_attempts: int = 1     # single-shot content tries before giving up
    api_retries: int = 2      # blind retries for transient API errors, per call

    def build_prompt(self, problem: dict) -> str:
        raise NotImplementedError

    def attempt(self, text: str, problem: dict) -> Attempt:
        raise NotImplementedError

    def repair_prompt(self, problem: dict, outcome: Attempt, response: str) -> str | None:
        """Follow-up prompt that feeds a *content* failure (the model's own output was
        ungradable) back so it can fix it. None if this protocol has no repair for it."""
        return None

    def _generate(self, model, prompt: str):
        """One model call, blind-retrying transient API errors. PromptTooLongError is
        deterministic and propagates immediately; a persistent API error propagates
        after ``api_retries`` so the runner can record it as an excluded error."""
        fails = 0
        while True:
            try:
                return model.generate(prompt, self.system)
            except PromptTooLongError:
                raise
            except ModelError:
                fails += 1
                if fails > self.api_retries:
                    raise

    def run_episode(self, model, problem: dict, budget: int | None = None) -> Episode:
        """Single-shot loop: generate, grade; feed an ungradable output back to be
        fixed (``repair_prompt``) until gradable or the budget is spent.

        Each iteration is an INDEPENDENT, stateless ``model.generate`` call — no
        conversation history is sent; the repair prompt is a fresh standalone prompt
        that re-states the problem + failed code + error. ``attempts`` logs each such
        call (see ``_call_log``)."""
        limit = budget or self.max_attempts
        prompt = self.build_prompt(problem)
        attempts, note = [], None
        outcome = Attempt(error="no response")
        while len(attempts) < limit:
            completion = self._generate(model, prompt)
            outcome = self.attempt(completion.text, problem)
            note = outcome.note
            log_outcome = "graded" if not outcome.error else f"ungradable: {outcome.error}"
            attempts.append(_call_log(prompt, completion, log_outcome))
            if not outcome.error:
                break
            repair = self.repair_prompt(problem, outcome, completion.text)
            if not repair:
                break
            prompt = repair
        return Episode(outcome, attempts, note)


class CodeProtocol(Protocol):
    name, system = "code", CODE_SYSTEM
    prompt_template = CODE_PROMPT   # overridable per-run via `eval.runner --prompt <name>`
    max_attempts = 5   # self-repair: feed execution errors back up to 5 times, then fail

    def build_prompt(self, problem):
        return self.prompt_template.format(problem=problem["problem"])

    def attempt(self, text, problem):
        code = extract_code(text)
        if not code:
            return Attempt(error="no code in response", code="")
        ran, results, error_info = run_solver(code)
        if not ran:
            return Attempt(error=error_info[:200], code=code)
        return Attempt(results=results, code=code)

    def repair_prompt(self, problem, outcome, response):
        return CODE_REPAIR.format(problem=problem["problem"],
                                  code=outcome.code or "(no code was produced)", error=outcome.error)


class DirectProtocol(Protocol):
    name, system = "direct", DIRECT_SYSTEM
    max_attempts = 5   # symmetric with code: re-ask (with feedback) if no \boxed{} value

    def build_prompt(self, problem):
        return DIRECT_PROMPT.format(problem=problem["problem"])

    def attempt(self, text, problem):
        if not text:
            return Attempt(error="empty response")
        n_subs = len({str(sub["sub"]) for sub in problem["sub_answers"]})
        boxes = _balanced_boxed(text)
        # (value, unit) per box: the prompt asks for "\boxed{<number> <unit>}", and the unit
        # is what lets the engine reconcile a correct answer given in a commensurate unit.
        parsed = [(_parse_number(box), _parse_unit(box)) for box in boxes]
        answers = [(value, unit) for value, unit in parsed if value is not None]
        note = f"boxes={len(boxes)} nums={len(answers)} need={n_subs} units={sum(1 for _, u in answers if u)}"
        if len(answers) > n_subs:  # extra boxes are intermediate; the finals are the last N
            answers = answers[-n_subs:]
        if not answers:
            return Attempt(error="no boxed answer", note=note)
        results = {str(index + 1): {"value": value, "unit": unit}
                   for index, (value, unit) in enumerate(answers)}
        return Attempt(results=results, note=note)

    def repair_prompt(self, problem, outcome, response):
        return DIRECT_REPAIR.format(problem=problem["problem"],
                                    answer=(response or "").strip()[-2000:] or "(empty)")


class AgentProtocol(Protocol):
    """Iterative code-interpreter: the model runs code in a persistent session, sees
    each cell's output, refines over up to ``max_turns`` turns, then calls submit()."""
    name, system = "agent", AGENT_SYSTEM
    max_turns = 10   # turns before giving up if the model never calls submit()

    def build_prompt(self, problem):
        return AGENT_PROMPT.format(problem=problem["problem"])

    # Overrides the single-shot loop entirely, so attempt()/repair_prompt() are unused.
    def run_episode(self, model, problem: dict, budget: int | None = None) -> Episode:
        limit = budget or self.max_turns
        session = CodeSession()
        prompt = self.build_prompt(problem)
        transcript = prompt   # what the model actually sees: problem + appended results
        attempts = []   # one entry per turn (see _call_log); "outcome" is the cell observation
        for turn in range(1, limit + 1):
            completion = self._generate(model, transcript)
            response = completion.text
            code = extract_code(response)
            if not code:
                observation = ("No ```python code block found. Write one to compute, "
                               "and call submit(answer) once you have the final answer.")
            else:
                cell = session.run(code)
                if cell.submitted:
                    outcome = self._grade(cell.answer)
                    if not outcome.error:   # gradable (pass or wrong-but-runnable) -> done
                        attempts.append(_call_log(transcript, completion, "graded"))
                        return Episode(outcome, attempts, f"turns={turn}")
                    observation = outcome.error   # malformed submit -> ask again
                else:
                    observation = cell.observation()
            attempts.append(_call_log(transcript, completion, observation))
            transcript += f"\n\n{response.strip()}\n\n## Result\n{observation}"
        return Episode(Attempt(error=f"no submit() within {limit} turns"), attempts, f"turns={limit}")

    @staticmethod
    def _grade(answer) -> Attempt:
        """Turn a submit() payload into a gradable results dict, leniently accepting
        either {"1": {"value", "unit"}} or a bare {"1": <number>}."""
        if not isinstance(answer, dict) or not answer:
            return Attempt(error='submit() expects a non-empty dict keyed "1".."N", '
                                 'each {"value": <number>, "unit": "<unit>"}')
        results = {}
        for key, entry in answer.items():
            if isinstance(entry, dict) and "value" in entry:
                results[str(key)] = {"value": entry["value"], "unit": str(entry.get("unit", ""))}
            else:
                results[str(key)] = {"value": entry, "unit": ""}
        return Attempt(results=results)


PROTOCOLS = {protocol.name: protocol
             for protocol in (CodeProtocol(), DirectProtocol(), AgentProtocol())}

# Named system-prompt presets for controlled prompt ablations. Select one with
# `eval.runner --system <name>` (or pass a literal string) to override a run's
# system prompt without editing this file; the resolved value is recorded in the
# run metrics for provenance. The per-mode default is what each protocol already
# carries (currently "expert" for both code and direct).
SYSTEM_PRESETS = {
    "expert": "You are an expert in atmospheric science.",   # current default
    "coder": "You are a Python code generator.",             # role-only variant (isolates persona; no output constraint)
    "coder-strict": "You are a Python code generator. Return ONLY executable Python code.",  # legacy full system
}

# Named code-prompt (user) presets, selected with `eval.runner --prompt <name>`.
# "original" is the live default (reasoning-permissive). "restrictive" is the legacy code-only
# prompt (the pre-redesign form that constrains output to code), built by swapping the opening,
# rules, and closing of the default to their restrictive forms. Assertions guard that every swap
# matched an anchor (a silent no-op would be a false variant).
_PERMISSIVE_OPEN = "Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s)."
_RESTRICT_OPEN = "Write a Python `solve()` function that computes the numerical answer(s)."
_PERMISSIVE_CLOSE = "The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block."
_RESTRICT_CLOSE = "Write ONLY the Python code containing the solve() function."
_PERMISSIVE_RULES = """1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {{"value": <number>, "unit": "<unit>"}} — exactly that many entries, no intermediate or unit-converted extras. Each "value" must be a single number, never a list; if one part asks for several values, give each its own entry.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number."""
_RESTRICT_RULES = """1. All given values from the problem must be function parameters with defaults.
2. Return a dict with one entry per quantity the problem asks for, keyed "1", "2",
   ..., "N" in the order asked, each mapping to {{"value": <number>, "unit": "<unit>"}}.
   Return exactly that many entries; do NOT add intermediate or unit-converted values.
3. Only use standard library (math, etc.). No external packages.
4. Do unit conversions explicitly in code."""

def _swap(base, old, new):
    assert old in base, f"prompt-preset anchor not found: {old[:40]!r}"
    return base.replace(old, new)

PROMPT_PRESETS = {
    "original": CODE_PROMPT,
    "restrictive": _swap(_swap(_swap(CODE_PROMPT, _PERMISSIVE_OPEN, _RESTRICT_OPEN), _PERMISSIVE_RULES, _RESTRICT_RULES), _PERMISSIVE_CLOSE, _RESTRICT_CLOSE),
}
