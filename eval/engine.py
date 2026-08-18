"""Solver execution + grading engine — the heart of the benchmark contract.

A `solve()` function takes every given value as a defaulted parameter, uses only
the standard library, and returns ``dict[str, {"value": number, "unit": str}]``
keyed by sub-part id. This module executes such code and grades its output
against known answers within a relative tolerance.

Pure standard library, zero project dependencies: imported by both the
evaluation harness (`eval/`) and the dataset pipeline (`pipeline/`).

  run_solver(code)                  -> (ok, results_dict, info)
  compare_values(expected, actual)  -> bool   (rel-err <= tol; handles inf, ×/x)
  verify_solver(results, expected)  -> (all_passed, per_sub_details)

Grading rule: per sub-answer, relative error <= tolerance (default 5%). A sub may
list multiple acceptable values (passes if any match). Missing sub keys fall back
to positional matching against the returned dict's key order.
"""

import re
import sys
import json
import math
import subprocess
from collections import defaultdict

# Solver code is untrusted model output: it may loop forever. We run it in an
# isolated subprocess (the only reliable way to enforce a CPU-bound timeout under
# the runner's thread pool — signals only fire on the main thread, and a hung
# thread cannot be killed) that emits its verdict as a single JSON line.
SOLVER_TIMEOUT = 10.0

_SOLVER_RUNNER = r"""
import sys, json, traceback
ns = {"print": lambda *a, **k: None}
try:
    exec(sys.stdin.read(), ns)
    fn = ns.get("solve")
    if not callable(fn):
        out = {"ok": False, "err": "No solve() function defined"}
    else:
        r = fn()
        if not isinstance(r, dict):
            out = {"ok": False, "err": "solve() returned %s, expected dict" % type(r).__name__}
        else:
            out = {"ok": True, "result": r}
except Exception:
    out = {"ok": False, "err": "Runtime error in solve():\n" + traceback.format_exc()}
try:
    sys.stdout.write("\n" + json.dumps(out))
except (TypeError, ValueError):
    sys.stdout.write("\n" + json.dumps(out, default=str))
"""


def extract_code(text: str) -> str:
    """Extract Python code from an LLM response (```python fenced or raw).

    A model sometimes opens a fence and never closes it — the body is complete, only the
    trailing ``` is missing. Returning the raw text then hands the ```python line itself to
    the interpreter and the attempt dies with a SyntaxError on line 1, which looks like a
    model failure but is an extraction artefact. So an unterminated opening fence is
    stripped and everything after it is used."""
    if not text:
        return ""
    text = text.strip()
    match = re.search(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    unterminated = re.match(r'```[a-zA-Z]*\s*\n(.*)', text, re.DOTALL)
    if unterminated:
        return unterminated.group(1).strip()
    return text


def run_solver(code: str, timeout: float = SOLVER_TIMEOUT) -> tuple[bool, dict, str]:
    """Execute solver code and call solve(). Returns (success, results_dict, error_or_info).

    Runs in an isolated subprocess with a hard ``timeout`` so runaway model code
    (e.g. an infinite loop) is killed and reported as a failure instead of hanging
    the eval. The injected no-op ``print`` silences solver debug output; the real
    verdict is the last JSON line on stdout."""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _SOLVER_RUNNER],
            input=code, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, {}, f"Execution timeout (> {timeout:g}s) — likely an infinite loop"

    out = proc.stdout.strip()
    if not out:
        return False, {}, f"Compile/exec error (no output):\n{proc.stderr.strip()[:1000]}"
    try:
        payload = json.loads(out.splitlines()[-1])
    except json.JSONDecodeError:
        return False, {}, f"Unparseable solver output:\n{out[:1000]}"

    if not payload.get("ok"):
        return False, {}, payload.get("err", "unknown solver error")
    return True, payload["result"], "ok"


def compare_values(expected: str, actual: float, tolerance: float = 0.05) -> bool:
    """Compare expected string value to actual float within relative tolerance."""
    exp_str = str(expected).strip()
    # Special values
    if exp_str in ("\\infty", "inf", "infinity"):
        return math.isinf(actual) and actual > 0
    if exp_str in ("-\\infty", "-inf"):
        return math.isinf(actual) and actual < 0
    try:
        exp_val = float(exp_str)
    except ValueError:
        # loosely-formatted scientific notation only: "1.5×10^3", "1.5 x 10^3",
        # "1.5×3" (× as the power-of-ten separator). A bare stray 'x' won't match.
        sci = re.fullmatch(r"\s*([-+]?\d*\.?\d+)\s*[×xX]\s*(?:10\s*\^?\s*)?([-+]?\d+)\s*", exp_str)
        if not sci:
            return False
        exp_val = float(sci.group(1)) * 10 ** int(sci.group(2))

    if exp_val == 0 and actual == 0:
        return True
    if exp_val == 0:
        return abs(actual) < tolerance
    return abs(actual - exp_val) / max(abs(exp_val), 1e-15) <= tolerance


# --- unit-aware grading ------------------------------------------------------
# A scalar unit -> (dimension, factor-to-base-unit). Only simple, unambiguous
# units are listed. Compound units ("m s^-1", "g m^-3") are deliberately absent
# and fall back to plain value comparison, as is temperature (K/°C differ by an
# offset, not a factor — handled by listing both forms as acceptable values).
_UNIT_FACTORS = {
    # length -> m
    "m": ("L", 1.0), "meter": ("L", 1.0), "metre": ("L", 1.0), "cm": ("L", 1e-2),
    "mm": ("L", 1e-3), "km": ("L", 1e3), "um": ("L", 1e-6), "µm": ("L", 1e-6),
    "micron": ("L", 1e-6), "nm": ("L", 1e-9),
    "inch": ("L", 0.0254), "inches": ("L", 0.0254), "ft": ("L", 0.3048),
    "foot": ("L", 0.3048), "feet": ("L", 0.3048), "mile": ("L", 1609.344), "miles": ("L", 1609.344),
    # time -> s. Sub-second prefixes were absent until 2026-08-01, so an answer
    # declared in "s" could never reconcile against a GT stored in "ns" (found on
    # fp_11.1, where every frontier configuration reports the lifetime in seconds).
    # "ms" is unambiguous after lowercasing ("Ms" is not a unit any answer uses),
    # mirroring the "um"/"nm" precedent in the length row.
    "s": ("T", 1.0), "sec": ("T", 1.0), "second": ("T", 1.0), "seconds": ("T", 1.0),
    "ms": ("T", 1e-3), "millisecond": ("T", 1e-3), "milliseconds": ("T", 1e-3),
    "us": ("T", 1e-6), "µs": ("T", 1e-6), "μs": ("T", 1e-6),
    "microsecond": ("T", 1e-6), "microseconds": ("T", 1e-6),
    "ns": ("T", 1e-9), "nanosecond": ("T", 1e-9), "nanoseconds": ("T", 1e-9),
    "min": ("T", 60.0), "minute": ("T", 60.0), "minutes": ("T", 60.0),
    "h": ("T", 3600.0), "hr": ("T", 3600.0), "hour": ("T", 3600.0), "hours": ("T", 3600.0),
    "day": ("T", 86400.0), "days": ("T", 86400.0),
    "yr": ("T", 31557600.0), "year": ("T", 31557600.0), "years": ("T", 31557600.0),
    # pressure -> Pa
    "pa": ("P", 1.0), "hpa": ("P", 100.0), "kpa": ("P", 1000.0),
    "mb": ("P", 100.0), "mbar": ("P", 100.0), "bar": ("P", 1e5), "atm": ("P", 101325.0),
    # mass -> kg
    "kg": ("M", 1.0), "g": ("M", 1e-3), "gram": ("M", 1e-3), "grams": ("M", 1e-3), "mg": ("M", 1e-6),
    "ug": ("M", 1e-9), "μg": ("M", 1e-9), "microgram": ("M", 1e-9), "micrograms": ("M", 1e-9),
    "ng": ("M", 1e-12), "tonne": ("M", 1e3), "tonnes": ("M", 1e3), "metricton": ("M", 1e3),
    # dimensionless ratio (reconciles a percentage with a bare fraction).
    # "1" is the SI convention for a dimensionless unit and appears frequently
    # in model outputs (143 graded answers were failed for declaring it before
    # it was added on 2026-07-25).
    "": ("R", 1.0), "dimensionless": ("R", 1.0), "fraction": ("R", 1.0),
    "ratio": ("R", 1.0), "unitless": ("R", 1.0), "%": ("R", 1e-2), "percent": ("R", 1e-2),
    "1": ("R", 1.0),
    # energy -> J (kilo prefix only; "mJ"/"MJ" is ambiguous after lowercasing
    # and is deliberately NOT mapped)
    "j": ("E", 1.0), "joule": ("E", 1.0), "joules": ("E", 1.0), "kj": ("E", 1e3),
    # plane angle -> rad. Bare "°" maps here; "°C" is handled by the
    # temperature branch of _canonical BEFORE this table is consulted, and a
    # unit like "degrees (direction from)" does not normalise to a bare token,
    # so wind-direction conventions are never silently reconciled.
    "rad": ("A", 1.0), "radian": ("A", 1.0), "radians": ("A", 1.0),
    "deg": ("A", 0.017453292519943295), "degree": ("A", 0.017453292519943295),
    "degrees": ("A", 0.017453292519943295), "°": ("A", 0.017453292519943295),
    # temperature DIFFERENCE (linear, offset-free) — reached only through
    # _canonical_compound, i.e. inside compound units such as "K/km" vs "K/m" or
    # "°C/h" (lapse rates, tendencies). A degree Celsius and a kelvin are the same
    # SIZE of interval, so both map to 1.0 here; the 273.15 offset applies to
    # absolute temperatures only. An ABSOLUTE temperature never reaches this
    # table: _canonical intercepts bare K/°C/C first and gives them the
    # offset-aware TEMPABS dimension, which can never reconcile against this
    # "ΘD" difference dimension (so "20 °C" is never credited against "20 °").
    "k": ("ΘD", 1.0), "c": ("ΘD", 1.0), "°c": ("ΘD", 1.0), "℃": ("ΘD", 1.0),
}

# Absolute temperatures need an affine map (K = scale*x + offset), which the
# multiplicative _UNIT_FACTORS table cannot express. Handled as a special case
# in _canonical, ahead of the table lookup. Fahrenheit is intentionally
# omitted ("f" is too collision-prone a token; no graded answer has needed it).
_TEMP_ABSOLUTE = {
    "k": (1.0, 0.0), "kelvin": (1.0, 0.0),
    "c": (1.0, 273.15), "°c": (1.0, 273.15), "degc": (1.0, 273.15),
    "celsius": (1.0, 273.15), "℃": (1.0, 273.15),
}


def _canonical(value: float, unit: str):
    """(dimension, value-in-base-unit) for a recognised scalar unit, else None."""
    normalized = str(unit).strip().lower()
    for junk in ("$", "\\mathrm", "\\text", "{", "}", " "):
        normalized = normalized.replace(junk, "")
    temp = _TEMP_ABSOLUTE.get(normalized)
    if temp is not None:
        scale, offset = temp
        return "TEMPABS", value * scale + offset
    factor = _UNIT_FACTORS.get(normalized)
    if factor is None:
        return None
    dimension, to_base = factor
    return dimension, value * to_base


_SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
        "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}


def _canonical_compound(value: float, unit: str):
    """Generalise `_canonical` to COMPOUND units (rates, areas, etc.):
    parse a unit like "cm^3 min^-1", "m s^-1", "tonnes/yr", "g/m^3" into a
    (dimension-signature, value-in-SI) pair. Returns None if any token is not a
    recognised scalar unit (then the caller falls back to plain comparison).

    The signature is the sorted tuple of (dimension, net-exponent), so two units
    reconcile only when their FULL dimensional signature matches — never across
    dimensions. Returns (signature, value*factor)."""
    s = str(unit).strip().lower()
    for junk in ("$", "\\mathrm", "\\text", "{", "}"):
        s = s.replace(junk, "")
    for u, a in _SUP.items():
        s = s.replace(u, a)
    s = s.replace("·", " ").replace("×", " ").replace("*", " ").replace("per", "/")
    if s.count("/") > 1:
        return None
    num, _, den = s.partition("/")
    dims, factor = {}, 1.0

    def absorb(piece, sign):
        nonlocal factor
        for tok in piece.split():
            # "°" and "℃" are part of a unit token ("°c/km", "℃/h"), not separators
            m = re.fullmatch(r"([a-zµμ%°℃]+)\^?(-?\d+)?", tok)
            if not m:
                return False
            name, power = m.group(1), int(m.group(2)) if m.group(2) else 1
            if name not in _UNIT_FACTORS:
                return False
            dim, f = _UNIT_FACTORS[name]
            dims[dim] = dims.get(dim, 0) + sign * power
            factor *= f ** (sign * power)
        return True

    if not num.strip() or not absorb(num, 1) or (den and not absorb(den, -1)):
        return None
    signature = tuple(sorted((d, e) for d, e in dims.items() if e != 0))
    return signature, value * factor


def _units_reconcile(expected: str, expected_unit: str, actual: float,
                     actual_unit: str, tolerance: float) -> bool:
    """True if expected and actual agree once each is converted via its DECLARED
    unit (e.g. 1.5 cm vs 0.0146 m, 35 % vs 0.35, or 4.5e-8 cm^3/min vs 7.5e-10
    cm^3/s). Fires only when both units parse to the SAME dimensional signature,
    so it never loosens a same-unit compare; it only credits an answer that is
    right in a different but commensurate unit. Tries the simple scalar map first,
    then the compound parser."""
    try:
        expected_value = float(str(expected).strip())
    except ValueError:
        return False
    ce, ca = _canonical(expected_value, expected_unit), _canonical(actual, actual_unit)
    if ce is not None and ca is not None and ce[0] == ca[0]:
        base_expected, base_actual = ce[1], ca[1]
    else:  # fall back to compound parsing (rates, areas, ...)
        ce, ca = _canonical_compound(expected_value, expected_unit), _canonical_compound(actual, actual_unit)
        if ce is None or ca is None or ce[0] != ca[0]:
            return False
        base_expected, base_actual = ce[1], ca[1]
    if base_expected == 0:
        return abs(base_actual) < tolerance
    return abs(base_actual - base_expected) / max(abs(base_expected), 1e-15) <= tolerance


def verify_solver(solver_results: dict, expected_answers: list[dict],
                  tolerance: float = 0.05) -> tuple[bool, list]:
    """Verify solver results against expected answers (per-sub, positional fallback).

    Each expected sub-answer is matched to the returned entry with the same key,
    falling back to position by key order. The code/direct prompts instruct the
    model to return its answers keyed "1".."N" in the order asked, so this mapping
    is unambiguous; a sub may list several acceptable values (passes if any match).
    """
    if not solver_results:
        return False, [{"error": "empty results"}]

    expected_by_sub = defaultdict(list)
    for expected in expected_answers:
        expected_by_sub[str(expected["sub"])].append((expected["value"], expected.get("unit", "")))

    solver_keys = list(solver_results.keys())
    details = []
    all_passed = True

    for sub, accepted in expected_by_sub.items():
        accepted_values = [value for value, _ in accepted]
        accepted_units = [unit for _, unit in accepted]
        entry = solver_results.get(sub)
        if entry is None:  # positional fallback
            position = list(expected_by_sub.keys()).index(sub)
            if position < len(solver_keys):
                entry = solver_results[solver_keys[position]]

        if entry is None:
            details.append({"sub": sub, "expected": accepted_values, "expected_units": accepted_units,
                            "actual": None, "actual_unit": "", "passed": False})
            all_passed = False
            continue

        actual_value = entry.get("value") if isinstance(entry, dict) else entry
        actual_unit = entry.get("unit", "") if isinstance(entry, dict) else ""
        try:
            actual_float = float(actual_value)
        except (ValueError, TypeError):
            details.append({"sub": sub, "expected": accepted_values, "expected_units": accepted_units,
                            "actual": str(actual_value), "actual_unit": actual_unit, "passed": False})
            all_passed = False
            continue

        # Pass if the value matches outright, OR if it matches once both sides are
        # converted via their declared units (a right answer in a commensurate unit).
        passed = any(compare_values(value, actual_float, tolerance)
                     or _units_reconcile(value, unit, actual_float, actual_unit, tolerance)
                     for value, unit in accepted)
        # Units are stored so offline re-grading can replay the same unit-aware rule
        # (without them a bare numeric re-compare under-grades commensurate-unit answers).
        details.append({"sub": sub, "expected": accepted_values, "expected_units": accepted_units,
                        "actual": actual_float, "actual_unit": actual_unit, "passed": passed})
        if not passed:
            all_passed = False

    return all_passed, details
