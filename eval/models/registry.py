"""models.toml → :class:`Model`. Declarative config, validated at load,
dispatched to a provider class (mirrors agent-worker's model_registry).

Adding a model is a TOML edit, no code change. ``provider`` selects the class:
``"anthropic"`` → native Anthropic SDK; everything else → OpenAI-compat (which
already covers openai/azure/deepseek/qwen/gemini/moonshot/sglang/litellm).
"""

import tomllib
from pathlib import Path

from .base import Model
from .openai_compat import OpenAIModel
from .anthropic_native import AnthropicModel
from .google_native import GoogleModel
from .openai_responses import OpenAIResponsesModel

MODELS_TOML = Path("models.toml")
DEFAULT_MAX_TOKENS = 16384
KNOWN_PROVIDERS = {"openai", "anthropic", "moonshot", "qwen", "azure", "google", "openai_responses"}


def load_config(name: str, path: Path = MODELS_TOML) -> dict:
    """Read and validate one model section from models.toml. Fails fast on a
    missing section, missing credentials, or an unknown provider."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    with open(path, "rb") as f:
        registry = tomllib.load(f)
    if name not in registry:
        raise ValueError(f"Model '{name}' not in {path}. Available: {sorted(registry)}")
    cfg = registry[name]
    if not (cfg.get("model_id") or cfg.get("api_model")):
        raise ValueError(f"Model '{name}': missing 'model_id' (or 'api_model')")
    if not cfg.get("api_key"):
        raise ValueError(f"Model '{name}': missing 'api_key'")
    provider = cfg.get("provider", "openai")
    if provider not in KNOWN_PROVIDERS:
        raise ValueError(f"Model '{name}': unknown provider '{provider}' "
                         f"(known: {sorted(KNOWN_PROVIDERS)})")
    return cfg


def build_model(cfg: dict, thinking_mode: str = "on") -> Model:
    """Construct a :class:`Model` from a validated config dict.

    ``thinking_mode`` ("on"/"off") selects which ``thinking`` variant to bake in
    for configs that define one (SGLang/Moonshot dialect for OpenAI-compat, native
    shape for Anthropic). Configs without a ``thinking`` table ignore it.
    """
    model = cfg.get("model_id") or cfg.get("api_model")
    max_tokens = cfg.get("max_tokens", DEFAULT_MAX_TOKENS)
    thinking_variant = (cfg.get("thinking") or {}).get(thinking_mode)

    if cfg.get("provider") == "openai_responses":
        return OpenAIResponsesModel(
            model, api_key=cfg["api_key"], base_url=cfg["base_url"],
            timeout=cfg.get("timeout", 120.0), max_tokens=max_tokens,
            reasoning_effort=cfg.get("reasoning_effort"),
            reasoning_summary=cfg.get("reasoning_summary", "auto"),
            temperature=cfg.get("temperature"),
        )

    if cfg.get("provider") == "google":
        return GoogleModel(
            model, api_key=cfg["api_key"], timeout=cfg.get("timeout", 120.0),
            temperature=cfg.get("temperature"), max_tokens=max_tokens,
            include_thoughts=cfg.get("include_thoughts", True),
            thinking_budget=cfg.get("thinking_budget"),
            thinking_level=cfg.get("thinking_level"),
            base_url=cfg.get("base_url"),
            auth_bearer=cfg.get("auth_bearer", False),
            extra_headers=cfg.get("extra_headers"),
        )

    if cfg.get("provider") == "anthropic":
        return AnthropicModel(
            model, api_key=cfg["api_key"], base_url=cfg.get("base_url"),
            timeout=cfg.get("timeout", 120.0), max_tokens=max_tokens,
            thinking=thinking_variant or None,
        )

    # OpenAI-compatible: merge the selected thinking variant onto extra_body.
    extra_body = dict(cfg.get("extra_body", {}))
    if thinking_variant:
        extra_body.update(thinking_variant)
    return OpenAIModel(
        model, api_key=cfg["api_key"], base_url=cfg.get("base_url"),
        timeout=cfg.get("timeout", 120.0),
        temperature=cfg.get("temperature"), reasoning=cfg.get("reasoning", False),
        reasoning_effort=cfg.get("reasoning_effort"), max_tokens=max_tokens,
        extra_body=extra_body or None, thinking_echo_field=cfg.get("thinking_echo_field"),
    )
