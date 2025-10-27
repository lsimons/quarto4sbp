"""Mock LLM client for testing without API calls."""

import re
from typing import Any


class MockLLMClient:
    """Mock LLM client that returns canned responses for testing.

    This mock client mimics the interface of the real LLM client but returns
    pre-configured responses instead of making actual API calls. It records
    all calls for test assertions.
    """

    def __init__(self, responses: dict[str, str] | None = None):
        """Initialize mock client with optional response mappings.

        Args:
            responses: Dictionary mapping prompt patterns to responses.
                       Keys can be exact strings or regex patterns.
        """
        self.responses: dict[str, str] = responses or {}
        self.call_history: list[dict[str, Any]] = []
        self._default_response = "Mock LLM response"

    def prompt(self, prompt_text: str, **kwargs: Any) -> str:
        """Return canned response for prompt.

        Args:
            prompt_text: The prompt text
            **kwargs: Additional parameters (ignored in mock)

        Returns:
            Matching response string

        Raises:
            ValueError: If no matching response found and no default set
        """
        # Record the call
        self.call_history.append(
            {"prompt": prompt_text, "kwargs": kwargs, "type": "prompt"}
        )

        # Try exact match first
        if prompt_text in self.responses:
            return self.responses[prompt_text]

        # Try regex matches
        for pattern, response in self.responses.items():
            if re.search(pattern, prompt_text, re.IGNORECASE):
                return response

        # Return default if available
        if self._default_response:
            return self._default_response

        # No match found
        raise ValueError(
            f"No response configured for prompt: {prompt_text[:100]}...\n"
            f"Available patterns: {list(self.responses.keys())}"
        )

    def add_response(self, pattern: str, response: str) -> None:
        """Add a response mapping.

        Args:
            pattern: Prompt pattern (exact string or regex)
            response: Response to return for matching prompts
        """
        self.responses[pattern] = response

    def set_default_response(self, response: str) -> None:
        """Set default response for unmatched prompts.

        Args:
            response: Default response text
        """
        self._default_response = response

    def clear_history(self) -> None:
        """Clear call history."""
        self.call_history = []

    def get_call_count(self) -> int:
        """Get number of calls made.

        Returns:
            Number of calls in history
        """
        return len(self.call_history)

    def get_last_call(self) -> dict[str, Any] | None:
        """Get the last call made.

        Returns:
            Last call dict or None if no calls made
        """
        return self.call_history[-1] if self.call_history else None

    def was_called_with(self, pattern: str) -> bool:
        """Check if client was called with prompt matching pattern.

        Args:
            pattern: Prompt pattern to search for (regex)

        Returns:
            True if any call matches pattern
        """
        for call in self.call_history:
            if re.search(pattern, call["prompt"], re.IGNORECASE):
                return True
        return False

    def get_calls_matching(self, pattern: str) -> list[dict[str, Any]]:
        """Get all calls matching a pattern.

        Args:
            pattern: Prompt pattern to search for (regex)

        Returns:
            List of matching call records
        """
        matches: list[dict[str, Any]] = []
        for call in self.call_history:
            if re.search(pattern, call["prompt"], re.IGNORECASE):
                matches.append(call)  # pyright: ignore[reportUnknownMemberType]
        return matches  # pyright: ignore[reportUnknownVariableType]
