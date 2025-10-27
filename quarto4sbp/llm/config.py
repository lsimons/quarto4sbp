"""Configuration system for LLM integration.

Supports loading configuration from:
1. TOML files (~/.config/q4s.toml and/or q4s.toml in project root)
2. Environment variables (override TOML settings)

Environment variables:
- OPENAI_API_KEY: API key for LLM provider
- OPENAI_API_URL: Custom API endpoint URL
- OPENAI_API_MODEL: Model name override
"""

import os
from dataclasses import dataclass
from typing import Any, Optional

from quarto4sbp.utils.config import load_config as load_toml_config


@dataclass
class LLMConfig:
    """Configuration for LLM client.

    Attributes:
        model: Model name (e.g., "azure/gpt-5-mini")
        api_key: API key for authentication
        base_url: Optional custom API endpoint URL
        max_tokens: Maximum tokens per request
        temperature: Sampling temperature (0.0-1.0)
        timeout: Request timeout in seconds
        max_attempts: Maximum retry attempts
        backoff_factor: Exponential backoff multiplier
    """

    model: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 10000
    temperature: float = 0.7
    timeout: int = 30
    max_attempts: int = 3
    backoff_factor: int = 2


def load_config() -> LLMConfig:
    """Load LLM configuration from files and environment.

    Configuration hierarchy (later overrides earlier):
    1. Default values
    2. ~/.config/q4s.toml settings
    3. ./q4s.toml settings (overrides user config)
    4. Environment variables (overrides all files)

    Returns:
        LLMConfig instance with loaded configuration

    Raises:
        ValueError: If API key is not configured
    """
    # Start with defaults
    config_dict: dict[str, Any] = {
        "model": "azure/gpt-5-mini",
        "api_key": "",
        "base_url": None,
        "max_tokens": 10000,
        "temperature": 0.7,
        "timeout": 30,
        "max_attempts": 3,
        "backoff_factor": 2,
    }

    # Load and merge TOML files (user config + local config)
    toml_data = load_toml_config(expand_vars=True)
    llm_section = toml_data.get("llm", {})

    # Update main config values from TOML
    if isinstance(llm_section, dict):
        for key in [
            "model",
            "api_key",
            "base_url",
            "max_tokens",
            "temperature",
            "timeout",
        ]:
            if key in llm_section:
                config_dict[key] = llm_section[key]

        # Update retry settings from TOML
        retry_section = llm_section.get("retry", {})  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        if isinstance(retry_section, dict):
            if "max_attempts" in retry_section:
                config_dict["max_attempts"] = retry_section["max_attempts"]
            if "backoff_factor" in retry_section:
                config_dict["backoff_factor"] = retry_section["backoff_factor"]

    # Environment variables override everything
    if api_key := os.environ.get("OPENAI_API_KEY"):
        config_dict["api_key"] = api_key

    if api_url := os.environ.get("OPENAI_API_URL"):
        config_dict["base_url"] = api_url

    if model := os.environ.get("OPENAI_API_MODEL"):
        config_dict["model"] = model

    # Validate API key is set
    if not config_dict["api_key"]:
        raise ValueError(
            "API key not configured. Set OPENAI_API_KEY environment variable "
            "or configure api_key in ~/.config/q4s.toml"
        )

    # Create config object with type conversion
    return LLMConfig(
        model=str(config_dict["model"]),
        api_key=str(config_dict["api_key"]),
        base_url=str(config_dict["base_url"]) if config_dict["base_url"] else None,
        max_tokens=int(config_dict["max_tokens"])
        if isinstance(config_dict["max_tokens"], int)
        else 10000,
        temperature=float(config_dict["temperature"])
        if isinstance(config_dict["temperature"], (int, float))
        else 0.7,
        timeout=int(config_dict["timeout"])
        if isinstance(config_dict["timeout"], int)
        else 30,
        max_attempts=int(config_dict["max_attempts"])
        if isinstance(config_dict["max_attempts"], int)
        else 3,
        backoff_factor=int(config_dict["backoff_factor"])
        if isinstance(config_dict["backoff_factor"], int)
        else 2,
    )
