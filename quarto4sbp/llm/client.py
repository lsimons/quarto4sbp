"""LLM client wrapper for AI-powered features.

This module provides a thin wrapper around the llm library for LLM interactions.
"""

import time

import llm
from typing import Any, Optional

from quarto4sbp.llm.config import LLMConfig, load_config


class LLMClient:
    """Wrapper around llm library for LLM interactions.

    This client provides a simple interface for LLM prompting with support for
    retries, error handling, and token tracking.

    Example:
        client = LLMClient()
        response = client.prompt("What is 2+2?")
        print(response)
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize LLM client.

        Args:
            config: Optional LLMConfig instance. If not provided, loads from
                   configuration files and environment.
        """
        self.config = config or load_config()

    def prompt(
        self,
        prompt_text: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
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
        # Use config defaults if not overridden
        model = model or self.config.model
        temperature = (
            temperature if temperature is not None else self.config.temperature
        )
        max_tokens = max_tokens or self.config.max_tokens

        # Set up model with API key
        llm_model = llm.get_model(model)
        if self.config.api_key:
            llm_model.key = self.config.api_key

        # Build the full prompt with system message if provided
        full_prompt = prompt_text
        if system:
            full_prompt = f"{system}\n\n{prompt_text}"

        # Retry logic with exponential backoff
        last_error: Optional[Exception] = None
        for attempt in range(self.config.max_attempts):
            try:
                # Make the API call
                response = llm_model.prompt(  # pyright: ignore[reportUnknownMemberType]
                    full_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.config.timeout,
                )

                # Extract text from response
                return str(response.text())

            except Exception as e:
                last_error = e
                # If this isn't the last attempt, wait before retrying
                if attempt < self.config.max_attempts - 1:
                    wait_time = self.config.backoff_factor**attempt
                    time.sleep(wait_time)
                continue

        # All retries failed
        error_msg = f"LLM API call failed after {self.config.max_attempts} attempts"
        if last_error:
            error_msg += f": {last_error}"
        raise ValueError(error_msg)

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


def create_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Create an LLM client instance.

    Convenience function for creating a client.

    Args:
        config: Optional LLMConfig instance

    Returns:
        Configured LLMClient instance
    """
    return LLMClient(config)
