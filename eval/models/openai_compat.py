"""OpenAI-compatible provider — one class for every openai-compat endpoint.

Covers OpenAI, Azure OpenAI, DeepSeek, Qwen/DashScope, Gemini (openai-compat
base_url), Moonshot/Kimi (first-party or self-hosted vLLM/SGLang), and LiteLLM
proxies. The class knows nothing about a specific deployment: reasoning, thinking
toggles, and ``reasoning_content`` echo all flow through config
(``reasoning_effort`` / ``extra_body`` / ``thinking_echo_field``).

Responses are streamed: a long generation keeps the connection busy chunk-by-chunk,
so it cannot trip a proxy's gateway/idle timeout the way a single blocking response
can (a self-hosted SGLang behind nginx returns 504 on slow non-streamed answers).
The accumulated text is identical to a non-streamed completion.
"""

import openai

from .base import Model, Completion
from .errors import ModelError, PromptTooLongError, TransientNetworkError
from .retry import with_retry, exponential_backoff, MAX_DELAY, RETRYABLE_HTTP_STATUS

_TRANSIENT = (openai.APIConnectionError, openai.APITimeoutError, ConnectionError, TimeoutError)


def _is_retryable(error: Exception) -> bool:
    status = getattr(error, "status_code", None) or getattr(error, "status", None)
    if status in RETRYABLE_HTTP_STATUS:
        return True
    return isinstance(error, _TRANSIENT)


def _retry_delay(attempt: int, error: Exception) -> float:
    """Honour a server ``Retry-After`` header when present, else exp-backoff."""
    retry_after = (getattr(error, "headers", None) or {}).get("retry-after")
    if retry_after is not None:
        try:
            return min(float(retry_after), MAX_DELAY)
        except (ValueError, TypeError):
            pass
    return exponential_backoff(attempt)


def _is_context_length(error: Exception) -> bool:
    """Detect 'prompt too long' across dialects: OpenAI uses a structured code,
    Moonshot et al. only say so in the message body."""
    if getattr(error, "code", None) == "context_length_exceeded":
        return True
    msg = str(error).lower()
    return "maximum context length" in msg or "context window" in msg


def _delta_field(delta, name: str):
    """Read a field off a streaming delta, including non-standard ones like
    ``reasoning_content`` that the SDK keeps under ``model_extra``."""
    value = getattr(delta, name, None)
    if value is None and getattr(delta, "model_extra", None):
        value = delta.model_extra.get(name)
    return value


def _reasoning_tokens(usage):
    """Extract the reasoning-token count from a usage object across dialects:
    OpenAI/OpenRouter/DeepSeek nest it under ``completion_tokens_details``; some
    SGLang servers (Kimi) expose a flat ``reasoning_tokens``. Returns the reported
    value (a real 0 is kept, not coerced) or None when the field is absent."""
    det = getattr(usage, "completion_tokens_details", None)
    rt = getattr(det, "reasoning_tokens", None) if det else None
    if rt is None:
        rt = getattr(usage, "reasoning_tokens", None)
        if rt is None and getattr(usage, "model_extra", None):
            rt = usage.model_extra.get("reasoning_tokens")
    return rt


class OpenAIModel(Model):
    def __init__(self, model: str, *, api_key: str, base_url: str | None = None,
                 timeout: float = 120.0, temperature: float | None = None,
                 reasoning: bool = False, reasoning_effort: str | None = None,
                 max_tokens: int = 16384, extra_body: dict | None = None,
                 thinking_echo_field: str | None = None) -> None:
        self.model = model
        self.temperature = temperature
        self.reasoning = reasoning
        self.reasoning_effort = reasoning_effort
        self.max_tokens = max_tokens
        self.extra_body = extra_body or None
        self.thinking_echo_field = thinking_echo_field
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def _kwargs(self, prompt: str, system: str | None) -> dict:
        messages = ([{"role": "system", "content": system}] if system else []) + \
                   [{"role": "user", "content": prompt}]
        kwargs: dict = {"model": self.model, "messages": messages}
        if self.reasoning:  # o1/o3/Azure-style: budget is max_completion_tokens, no temperature
            kwargs["max_completion_tokens"] = self.max_tokens
            if self.reasoning_effort:
                kwargs["reasoning_effort"] = self.reasoning_effort
        else:
            kwargs["max_tokens"] = self.max_tokens
            if self.temperature is not None:
                kwargs["temperature"] = self.temperature
        if self.extra_body:
            kwargs["extra_body"] = self.extra_body
        return kwargs

    def _stream_completion(self, kwargs: dict) -> Completion:
        """Open a streaming response and accumulate its chunks into one Completion.

        The ``with`` block releases the underlying httpx connection back to the pool
        even if iteration is cut short (an error mid-stream, a retry), which matters
        under the runner's long-lived thread pool."""
        content, reasoning = [], []
        prompt_tokens, completion_tokens, reasoning_tokens = 0, 0, None
        with self.client.chat.completions.create(
                **kwargs, stream=True, stream_options={"include_usage": True}) as stream:
            for chunk in stream:
                if chunk.usage:  # final usage-only chunk (include_usage)
                    prompt_tokens = chunk.usage.prompt_tokens or 0
                    completion_tokens = chunk.usage.completion_tokens or 0
                    reasoning_tokens = _reasoning_tokens(chunk.usage)
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    content.append(delta.content)
                # Thinking servers may stream the answer in a separate field (e.g.
                # reasoning_content on Moonshot/Qwen/DeepSeek-R1) with content empty.
                if self.thinking_echo_field:
                    piece = _delta_field(delta, self.thinking_echo_field)
                    if piece:
                        reasoning.append(piece)
        reasoning_text = "".join(reasoning)
        return Completion(text="".join(content) or reasoning_text,
                          prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                          reasoning=reasoning_text or None, reasoning_tokens=reasoning_tokens)

    def generate(self, prompt: str, system: str | None = None) -> Completion:
        kwargs = self._kwargs(prompt, system)
        try:
            return with_retry(lambda: self._stream_completion(kwargs),
                              is_retryable=_is_retryable, get_delay=_retry_delay)
        except openai.BadRequestError as exc:
            raise (PromptTooLongError if _is_context_length(exc) else ModelError)(str(exc)) from exc
        except _TRANSIENT as exc:
            raise TransientNetworkError(str(exc)) from exc
        except Exception as exc:
            raise ModelError(str(exc)) from exc
