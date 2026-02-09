"""Prompt management utilities for LLM integration.

Provides utilities for loading, caching, and formatting prompts from the prompts/ directory.
Supports template variables using Python's string formatting.
"""

import os
from functools import lru_cache
from pathlib import Path


class PromptNotFoundError(Exception):
    """Raised when a prompt file cannot be found."""

    pass


class PromptLoader:
    """Manages loading and caching of prompt files.

    Prompts are stored in the prompts/ directory relative to the package root.
    They are organized by feature (tov, viz, common) and loaded on demand.

    Example:
        loader = PromptLoader()
        prompt = loader.load("tov/system")
        formatted = loader.load_and_format("viz/analyze-slide", slide_content="...")
    """

    def __init__(self, prompts_dir: Path | None = None) -> None:
        """Initialize the prompt loader.

        Args:
            prompts_dir: Optional custom prompts directory path.
                        Defaults to prompts/ in the package root.
        """
        if prompts_dir is None:
            # Find package root (where prompts/ directory lives)
            package_root = Path(__file__).parent.parent.parent
            self.prompts_dir = package_root / "prompts"
        else:
            self.prompts_dir = prompts_dir

    @lru_cache(maxsize=32)  # noqa: B019
    def load(self, prompt_name: str) -> str:
        """Load a prompt file by name.

        Prompt names are relative to the prompts/ directory and should not
        include the file extension. For example, "tov/system" loads
        "prompts/tov/system.txt".

        Args:
            prompt_name: Name of the prompt without extension (e.g., "tov/system")

        Returns:
            The prompt text as a string

        Raises:
            PromptNotFoundError: If the prompt file doesn't exist
        """
        # Try .txt extension first, then .md as fallback
        for ext in [".txt", ".md"]:
            prompt_path = self.prompts_dir / f"{prompt_name}{ext}"
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8").strip()

        # If neither exists, raise error with helpful message
        raise PromptNotFoundError(
            f"Prompt '{prompt_name}' not found in {self.prompts_dir}. "
            f"Tried: {prompt_name}.txt, {prompt_name}.md"
        )

    def load_and_format(self, prompt_name: str, **kwargs: str) -> str:
        """Load a prompt and format it with template variables.

        Uses Python's string.format() to substitute template variables.

        Example:
            prompt = loader.load_and_format(
                "viz/analyze-slide",
                slide_content="# My Slide\\n- Point 1\\n- Point 2"
            )

        Args:
            prompt_name: Name of the prompt without extension
            **kwargs: Template variables to substitute in the prompt

        Returns:
            The formatted prompt text

        Raises:
            PromptNotFoundError: If the prompt file doesn't exist
            KeyError: If a required template variable is missing
        """
        template = self.load(prompt_name)
        return template.format(**kwargs)

    def list_prompts(self, category: str | None = None) -> list[str]:
        """List available prompts, optionally filtered by category.

        Args:
            category: Optional category to filter by (e.g., "tov", "viz", "common")

        Returns:
            List of prompt names (without extensions)
        """
        prompts: list[str] = []

        if category:
            search_dir = self.prompts_dir / category
            if not search_dir.exists():
                return []
            prefix = f"{category}/"
        else:
            search_dir = self.prompts_dir
            prefix = ""

        for root, _dirs, files in os.walk(search_dir):
            root_path = Path(root)
            for file in files:
                if file.endswith((".txt", ".md")):
                    # Get relative path from prompts_dir
                    file_path = root_path / file
                    rel_path = file_path.relative_to(self.prompts_dir)
                    # Remove extension
                    prompt_name = str(rel_path.with_suffix(""))
                    # Only add if in the right category (or no category filter)
                    if not category or prompt_name.startswith(prefix):
                        prompts.append(prompt_name)

        return sorted(prompts)

    def clear_cache(self) -> None:
        """Clear the prompt cache.

        Useful for testing or if prompts are modified at runtime.
        """
        self.load.cache_clear()


# Global default loader instance
_default_loader: PromptLoader | None = None


def get_loader() -> PromptLoader:
    """Get the default global prompt loader instance.

    Returns:
        The default PromptLoader instance
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = PromptLoader()
    return _default_loader


def load_prompt(prompt_name: str) -> str:
    """Load a prompt using the default loader.

    Convenience function for loading prompts without creating a loader instance.

    Args:
        prompt_name: Name of the prompt without extension

    Returns:
        The prompt text

    Raises:
        PromptNotFoundError: If the prompt file doesn't exist
    """
    return get_loader().load(prompt_name)


def load_and_format_prompt(prompt_name: str, **kwargs: str) -> str:
    """Load and format a prompt using the default loader.

    Convenience function for loading and formatting prompts without creating
    a loader instance.

    Args:
        prompt_name: Name of the prompt without extension
        **kwargs: Template variables to substitute

    Returns:
        The formatted prompt text

    Raises:
        PromptNotFoundError: If the prompt file doesn't exist
        KeyError: If a required template variable is missing
    """
    return get_loader().load_and_format(prompt_name, **kwargs)
