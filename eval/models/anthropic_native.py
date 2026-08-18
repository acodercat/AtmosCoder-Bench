"""Native Anthropic Messages API provider (``provider = "anthropic"``).

Used when the config points at the real Anthropic API (or an Anthropic-native
proxy). Endpoints that only speak OpenAI-compat — including LiteLLM proxies that
translate Claude — should omit ``provider`` and use :class:`OpenAIModel` instead.
"""

import anthropic

from .base import Model, Completion
from .errors import ModelError, PromptTooLongError, TransientNetworkError
from .retry import with_retry, RETRYABLE_HTTP_STATUS

_TRANSIENT = (anthropic.APIConnectionError, anthropic.APITimeoutError, ConnectionError, TimeoutError)


def _is_retryable(error: Exception) -> bool:
    status = getattr(error, "status_code", None) or getattr(error, "status", None)
    if status in RETRYABLE_HTTP_STATUS:
        return True
    return isinstance(error, _TRANSIENT)


class AnthropicModel(Model):
    def __init__(self, model: str, *, api_key: str, base_url: str | None = None,
                 timeout: float = 120.0, max_tokens: int = 16384,
                 thinking: dict | None = None) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.thinking = thinking  # native shape, e.g. {"type": "enabled", "budget_tokens": N}
        self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url, timeout=timeout)

    def generate(self, prompt: str, system: str | None = None) -> Completion:
        kwargs: dict = {"model": self.model, "max_tokens": self.max_tokens,
                        "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        if self.thinking:
            kwargs["thinking"] = self.thinking
        try:
            resp = with_retry(lambda: self.client.messages.create(**kwargs),
                              is_retryable=_is_retryable)
        except anthropic.BadRequestError as exc:
            message = str(exc).lower()
            raise (PromptTooLongError if "too long" in message or "context" in message
                   else ModelError)(str(exc)) from exc
        except _TRANSIENT as exc:
            raise TransientNetworkError(str(exc)) from exc
        except Exception as exc:
            raise ModelError(str(exc)) from exc

        text = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")
        usage = resp.usage
        # Claude folds thinking tokens into output_tokens with no separate count, so
        # reasoning_tokens is left unset and persists as 0 even on extended-thinking runs;
        # the thinking is still inside completion_tokens, just not broken out.
        return Completion(text=text,
                          prompt_tokens=usage.input_tokens if usage else 0,
                          completion_tokens=usage.output_tokens if usage else 0)
