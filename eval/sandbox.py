"""Stateful Python REPL for the agentic ``agent`` protocol.

Unlike :func:`eval.engine.run_solver` (which executes one self-contained solve()),
the agent protocol needs a session that PERSISTS state across turns: the model runs
a snippet, sees its output, then writes the next snippet using variables it already
defined. The model ends the task by calling the injected ``submit()``.

Kept separate from ``eval.engine`` on purpose — engine is the shared, single-shot
execution core used by both eval/ and pipeline/, and stays free of REPL state.
"""

import io
import threading
import traceback
from dataclasses import dataclass

_UNSET = object()   # distinguishes "submit() never called" from "submit(None)"


@dataclass
class CellResult:
    """Outcome of executing one code cell in a session."""
    stdout: str
    error: str | None          # formatted traceback / timeout message, or None on success
    submitted: bool            # did this cell call submit()?
    answer: object             # the value passed to submit() (only when submitted)

    def observation(self) -> str:
        """What to show the model back as this cell's result."""
        if self.error:
            return self.error
        return self.stdout.strip() or "(no output)"


def _exec_with_timeout(code, namespace, timeout):
    """Exec ``code`` into ``namespace`` in a daemon thread. Returns a formatted
    traceback on failure, a timeout message if it overran, or None on success. A
    runaway cell leaks its thread instead of hanging the worker."""
    box = {}

    def target():
        try:
            exec(code, namespace)
        except Exception:
            box["error"] = traceback.format_exc()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return f"TimeoutError: code did not finish within {timeout}s"
    return box.get("error")


class CodeSession:
    """A persistent namespace the model drives across turns.

    ``print`` is shadowed to capture output per-cell into a local buffer (NOT via
    ``redirect_stdout``, which swaps a global stream and would clobber concurrent
    sessions in the runner's thread pool). ``submit`` records the final answer and
    signals the loop to stop.
    """

    def __init__(self):
        self._buffer = io.StringIO()
        self._answer = _UNSET
        self.namespace = {"__name__": "__main__", "print": self._print, "submit": self._submit}

    def _print(self, *args, sep=" ", end="\n", **_):
        self._buffer.write(sep.join(str(arg) for arg in args) + end)

    def _submit(self, answer):
        self._answer = answer

    def run(self, code: str, timeout: int = 10) -> CellResult:
        self._buffer = io.StringIO()
        self._answer = _UNSET
        error = _exec_with_timeout(code, self.namespace, timeout)
        submitted = self._answer is not _UNSET
        return CellResult(
            stdout=self._buffer.getvalue()[-2000:],
            error=error[-2000:] if error else None,
            submitted=submitted,
            answer=self._answer if submitted else None,
        )
