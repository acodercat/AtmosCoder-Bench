"""Shared helpers for the raw-httpx JSON providers (Gemini native, OpenAI Responses).

Both speak plain REST rather than the OpenAI SDK, so they share connection error
handling and HTTP-status -> exception mapping. (SDK-based providers use their own
client's exceptions instead.)
"""

import httpx

from .errors import ModelError, PromptTooLongError, TransientNetworkError


def network_retryable(error: Exception) -> bool:
    """Retry on connection/timeout blips and surfaced 429/5xx."""
    return isinstance(error, (TransientNetworkError, httpx.TimeoutException, httpx.TransportError))


def post_json(client: httpx.Client, url: str, body: dict, *, headers: dict | None = None) -> dict:
    """POST ``body`` as JSON and return the parsed response. Maps failures to
    TransientNetworkError (429/5xx, retryable), PromptTooLongError, or ModelError."""
    try:
        response = client.post(url, json=body, headers=headers)
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        raise TransientNetworkError(str(exc)) from exc
    if response.status_code == 429 or response.status_code >= 500:
        raise TransientNetworkError(f"{response.status_code}: {response.text[:200]}")
    if response.status_code >= 400:
        message = response.text.lower()
        too_long = "too long" in message or "context" in message or ("token" in message and "exceed" in message)
        raise (PromptTooLongError if too_long else ModelError)(f"{response.status_code}: {response.text[:300]}")
    return response.json()
