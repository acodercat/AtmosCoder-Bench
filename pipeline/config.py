import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # LLM
    api_key: str = field(default_factory=lambda: os.environ.get("ATMOSCODER_LLM_API_KEY", ""))
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    model_id: str = "gemini-3.1-pro-preview"
    temperature: float = 0.2
    max_tokens: int = 16384

    # MinerU
    mineru_token: str = field(default_factory=lambda: os.environ.get("MINERU_TOKEN", ""))
    mineru_api_url: str = "https://mineru.net/api/v4"

    # Paths
    materials_dir: str = "data/raw"
    output_dir: str = "data/processed"
    max_retries: int = 3
