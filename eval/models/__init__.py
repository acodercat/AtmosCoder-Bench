"""Model abstraction layer — swap LLM providers via models.toml, no code change.

    from eval.models import load_config, build_model
    model = build_model(load_config("kimi-k2.6"), thinking_mode="off")
    completion = model.generate(prompt, system=...)   # -> Completion(text, tokens)
"""

from .base import Model, Completion
from .errors import ModelError, PromptTooLongError, TransientNetworkError
from .registry import load_config, build_model
from .openai_compat import OpenAIModel
from .anthropic_native import AnthropicModel

__all__ = [
    "Model", "Completion",
    "ModelError", "PromptTooLongError", "TransientNetworkError",
    "load_config", "build_model",
    "OpenAIModel", "AnthropicModel",
]
