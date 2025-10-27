"""LLM integration package for quarto4sbp.

This package provides LLM functionality for AI-powered features like
tone-of-voice rewriting and image generation.
"""

from quarto4sbp.llm.config import LLMConfig, load_config

__all__ = ["LLMConfig", "load_config"]
