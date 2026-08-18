"""Abstract :class:`Model` interface — every provider implements ``generate``.

Single-shot and synchronous: the benchmark sends one prompt and reads back the
text + token count. (Contrast axon's async streaming ``Model``, which exists for
multi-turn tool-using agents; a batch eval needs neither streaming nor tools.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Completion:
    """One model response and its token accounting.

    Tokens are split at the source rather than collapsed to a total: ``prompt_tokens``
    (input — re-counted on every stateless repair call) and ``completion_tokens``
    (everything generated, INCLUDING any reasoning). ``reasoning_tokens`` is the
    thinking-only slice of ``completion_tokens`` when the provider reports it, and
    defaults to ``None`` in memory when it does not.

    ``reasoning`` holds the thinking-trace text (reasoning_content) when the
    deployment emits one and the config opts in via ``thinking_echo_field``,
    captured separately from ``text`` (the gradable answer) so a reasoning run can
    persist the chain-of-thought without polluting grading.

    The in-memory field keeps ``None`` because that is what the provider said, but
    :attr:`usage` persists 0: every stored token count is an integer, so nothing
    downstream has to special-case null. Which configurations actually returned a
    thinking trace is answered by the presence of ``reasoning`` text (``rea_cov`` in
    :mod:`eval.analysis.token_count`), not by a null in the token account."""
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning: str | None = None
    reasoning_tokens: int | None = None

    @property
    def usage(self) -> dict:
        """This call's token account as a plain dict — the canonical ``usage`` shape
        persisted in every attempt/record. ``total_tokens`` = prompt + completion;
        ``reasoning_tokens`` is 0 when the provider reported no count, never null, so
        every persisted token field is an int."""
        return {"prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.prompt_tokens + self.completion_tokens,
                "reasoning_tokens": self.reasoning_tokens or 0}


class Model(ABC):
    """An LLM the runner can call. Implementations convert config to the wire
    format and translate SDK exceptions into :mod:`eval.models.errors`."""

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None) -> Completion:
        """Return the completion for one prompt.

        Retries transient errors internally; raises ``PromptTooLongError`` or
        ``ModelError`` (both terminal) on unrecoverable failure.
        """
        ...
