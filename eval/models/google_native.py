"""Native Google Gemini provider (``provider = "google"``).

Used when we need Gemini's THOUGHT SUMMARIES, which the OpenAI-compatible
endpoint (``generativelanguage.../v1beta/openai/``) does not expose. This hits
the native ``:generateContent`` REST API with
``generationConfig.thinkingConfig.includeThoughts = true``; the response parts
are split into thought parts (``"thought": true``) -> ``Completion.reasoning``
and answer parts -> ``Completion.text``. Endpoints that only speak OpenAI-compat
should omit ``provider`` and use :class:`OpenAIModel` instead.
"""

import httpx

from .base import Model, Completion
from .errors import ModelError
from .retry import with_retry
from .rest import post_json, network_retryable

_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GoogleModel(Model):
    def __init__(self, model: str, *, api_key: str, timeout: float = 120.0,
                 temperature: float | None = None, max_tokens: int = 16384,
                 include_thoughts: bool = True, thinking_budget: int | None = None,
                 thinking_level: str | None = None, base_url: str | None = None,
                 auth_bearer: bool = False, extra_headers: dict | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.include_thoughts = include_thoughts
        self.thinking_budget = thinking_budget   # token budget (Gemini 2.5); mutually exclusive w/ level
        self.thinking_level = thinking_level     # "low"/"medium"/"high" (Gemini 3); pin for reproducibility
        # A gateway may host the native generateContent API at a non-Google base and
        # authenticate via an Authorization header rather than the ?key= query param
        # (e.g. a path-prefixing gateway: /v1/publishers/google/models/{model}). The
        # response shape is unchanged, so only URL + headers differ.
        self.base_url = (base_url or _BASE).rstrip("/")
        self.auth_bearer = auth_bearer
        self.extra_headers = dict(extra_headers or {})
        self.client = httpx.Client(timeout=timeout)

    def generate(self, prompt: str, system: str | None = None) -> Completion:
        gen: dict = {"maxOutputTokens": self.max_tokens}
        if self.temperature is not None:
            gen["temperature"] = self.temperature
        if self.include_thoughts:
            tc: dict = {"includeThoughts": True}
            if self.thinking_level is not None:
                tc["thinkingLevel"] = self.thinking_level
            elif self.thinking_budget is not None:
                tc["thinkingBudget"] = self.thinking_budget
            gen["thinkingConfig"] = tc
        body: dict = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                      "generationConfig": gen}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        if self.auth_bearer:
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {"Authorization": f"Bearer {self.api_key}", **self.extra_headers}
        else:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            headers = self.extra_headers or None
        data = with_retry(lambda: post_json(self.client, url, body, headers=headers),
                          is_retryable=network_retryable)

        cands = data.get("candidates") or []
        if not cands:
            fb = data.get("promptFeedback", {})
            raise ModelError(f"no candidates (blocked: {fb})" if fb else "no candidates returned")
        parts = (cands[0].get("content") or {}).get("parts") or []
        text = "".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
        reasoning = "".join(p["text"] for p in parts if "text" in p and p.get("thought"))
        um = data.get("usageMetadata", {})
        # Gemini reports thought tokens separately from candidate (answer) tokens;
        # fold them into completion_tokens so reasoning_tokens stays a subset of it.
        thoughts = um.get("thoughtsTokenCount")
        return Completion(text=text,
                          prompt_tokens=um.get("promptTokenCount", 0),
                          completion_tokens=um.get("candidatesTokenCount", 0) + (thoughts or 0),
                          reasoning=reasoning or None, reasoning_tokens=thoughts)
