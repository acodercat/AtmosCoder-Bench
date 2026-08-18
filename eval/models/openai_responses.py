"""OpenAI **Responses API** provider (``provider = "openai_responses"``).

Chat-Completions hides a GPT-5/o-series model's reasoning (only reasoning_tokens
in usage). The Responses API (``POST /v1/responses`` with
``reasoning={"summary": "auto"|"detailed", "effort": ...}``) returns a reasoning
SUMMARY as an output item, which we surface as ``Completion.reasoning``. The final
answer is the ``message`` output item's text. Use this when an OpenAI-style
endpoint exposes ``/responses`` and we want the reasoning trace; otherwise use
:class:`OpenAIModel` (chat completions).
"""

import httpx

from .base import Model, Completion
from .errors import TransientNetworkError
from .retry import with_retry
from .rest import post_json, network_retryable


class OpenAIResponsesModel(Model):
    def __init__(self, model: str, *, api_key: str, base_url: str, timeout: float = 120.0,
                 max_tokens: int = 16384, reasoning_effort: str | None = None,
                 reasoning_summary: str = "auto", temperature: float | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self.url = base_url.rstrip("/") + "/responses"
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        self.reasoning_summary = reasoning_summary
        self.temperature = temperature
        self.client = httpx.Client(timeout=timeout)

    def generate(self, prompt: str, system: str | None = None) -> Completion:
        body: dict = {"model": self.model, "input": prompt, "max_output_tokens": self.max_tokens}
        reasoning: dict = {"summary": self.reasoning_summary}
        if self.reasoning_effort:
            reasoning["effort"] = self.reasoning_effort
        body["reasoning"] = reasoning
        if system:
            body["instructions"] = system
        if self.temperature is not None:
            body["temperature"] = self.temperature

        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = with_retry(lambda: post_json(self.client, self.url, body, headers=headers),
                          is_retryable=network_retryable)

        answer, summary = [], []
        for item in data.get("output", []):
            t = item.get("type")
            if t == "message":
                for c in item.get("content", []):
                    if c.get("text"):
                        answer.append(c["text"])
            elif t == "reasoning":
                for s in item.get("summary", []):
                    if s.get("text"):
                        summary.append(s["text"])
        text = "".join(answer)
        if not text and data.get("status") == "incomplete":
            raise TransientNetworkError(f"incomplete: {data.get('incomplete_details')}")
        u = data.get("usage", {})
        # A reported reasoning_tokens of 0 is real (this call didn't think); only an
        # absent field is unknown (-> None).
        reasoning_tokens = (u.get("output_tokens_details") or {}).get("reasoning_tokens")
        return Completion(text=text,
                          prompt_tokens=u.get("input_tokens", 0),
                          completion_tokens=u.get("output_tokens", 0),
                          reasoning="".join(summary) or None, reasoning_tokens=reasoning_tokens)
