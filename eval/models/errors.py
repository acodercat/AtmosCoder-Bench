"""Provider-agnostic model-layer error taxonomy (mirrors axon.models.errors).

Providers translate their SDK exceptions into these so the runner can decide
what to do without knowing which SDK raised: ``PromptTooLongError`` and a plain
``ModelError`` are terminal (recorded as the model's failure on that problem),
``TransientNetworkError`` is what retry treats as worth another attempt.
"""


class ModelError(Exception):
    """Base class for all provider-agnostic model-layer errors. Not retryable."""


class PromptTooLongError(ModelError):
    """The request exceeded the model's context window. Not retryable."""


class TransientNetworkError(ModelError):
    """A transient transport / rate-limit failure. Retryable."""
