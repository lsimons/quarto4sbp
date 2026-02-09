"""LLM client wrapper for AI-powered features.

This module provides a thin wrapper around lsimons-llm for LLM interactions,
adding TOML configuration file support on top of the base environment variable config.
"""

import time
from typing import Any

from lsimons_llm import LLMClient as BaseLLMClient  # pyright: ignore[reportMissingTypeStubs]
from lsimons_llm.config import LLMConfig as BaseLLMConfig  # pyright: ignore[reportMissingTypeStubs]

from quarto4sbp.llm.config import LLMConfig, load_config


class LLMClient:
    """Wrapper around lsimons-llm client for LLM interactions.

    This client provides a simple interface for LLM prompting with support for
    retries, error handling, and TOML configuration file support.

    Example:
        client = LLMClient()
        response = client.prompt("What is 2+2?")
        print(response)
    """

    def __init__(self, config: LLMConfig | None = None) -> None:
        """Initialize LLM client.

        Args:
            config: Optional LLMConfig instance. If not provided, loads from
                   configuration files and environment.
        """
        self.config = config or load_config()

        # Create base config for lsimons-llm client
        base_config = BaseLLMConfig(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            timeout=self.config.timeout,
            max_retries=self.config.max_attempts,
        )
        self._client = BaseLLMClient(base_config)

    def prompt(
        self,
        prompt_text: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a prompt to the LLM and get response.

        Args:
            prompt_text: The prompt text to send
            system: Optional system prompt
            model: Optional model override (uses config default if not provided)
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            The LLM response text

        Raises:
            ValueError: If API call fails after retries
        """
        # Build messages list
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt_text})

        try:
            return self._client.chat(
                messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            raise ValueError(f"LLM API call failed: {e}") from e

    def test_connectivity(self) -> dict[str, Any]:
        """Test LLM connectivity with a simple prompt.

        Returns:
            Dictionary with test results including:
                - success: bool indicating if test passed
                - response: the LLM response text (if successful)
                - error: error message (if failed)
                - elapsed_time: time taken in seconds
                - model: model name used
        """
        test_prompt = "Respond with exactly: 'Hello from LLM'"
        start_time = time.time()

        try:
            response = self.prompt(test_prompt)
            elapsed = time.time() - start_time

            return {
                "success": True,
                "response": response,
                "error": None,
                "elapsed_time": elapsed,
                "model": self.config.model,
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "response": None,
                "error": str(e),
                "elapsed_time": elapsed,
                "model": self.config.model,
            }

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "LLMClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def create_client(config: LLMConfig | None = None) -> LLMClient:
    """Create an LLM client instance.

    Convenience function for creating a client.

    Args:
        config: Optional LLMConfig instance

    Returns:
        Configured LLMClient instance
    """
    return LLMClient(config)
