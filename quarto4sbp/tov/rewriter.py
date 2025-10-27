"""Content rewriter using LLM for tone of voice conversion.

This module handles the LLM-based rewriting of markdown content to match
company tone of voice guidelines while preserving technical accuracy and structure.
"""

from pathlib import Path
from typing import Callable, Optional

from quarto4sbp.llm.client import LLMClient
from quarto4sbp.tov.parser import QmdSection


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts/tov/ directory.

    Args:
        prompt_name: Name of the prompt file (without .txt extension)

    Returns:
        Prompt template content

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    # Find the prompts directory relative to this file
    # Structure: quarto4sbp/quarto4sbp/tov/rewriter.py
    # Target: quarto4sbp/prompts/tov/
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    prompt_path = project_root / "prompts" / "tov" / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text()


def rewrite_section(
    section: QmdSection,
    client: LLMClient,
    system_prompt: Optional[str] = None,
) -> str:
    """Rewrite a single section using LLM.

    Args:
        section: QmdSection to rewrite
        client: LLMClient for making LLM calls
        system_prompt: Optional system prompt (loads default if not provided)

    Returns:
        Rewritten section content

    Raises:
        ValueError: If LLM call fails
    """
    # Load system prompt if not provided
    if system_prompt is None:
        system_prompt = load_prompt("system")

    # Load rewrite prompt template
    rewrite_template = load_prompt("rewrite-slide")

    # Format the prompt with section content
    # The template expects {tone_guidelines} and {slide_content}
    # We'll use the system prompt as guidelines
    prompt = rewrite_template.format(
        tone_guidelines=system_prompt,
        slide_content=section.content,
    )

    # Call LLM with system prompt
    response = client.prompt(prompt, system=system_prompt)

    # Return the response, preserving trailing newlines if original had them
    if section.content.endswith("\n") and not response.endswith("\n"):
        response += "\n"

    return response


def rewrite_content(
    sections: list[QmdSection],
    client: Optional[LLMClient] = None,
    system_prompt: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> list[str]:
    """Rewrite all sections using LLM.

    Args:
        sections: List of QmdSection to rewrite
        client: Optional LLMClient (creates new one if not provided)
        system_prompt: Optional system prompt override
        progress_callback: Optional callback function(current, total) for progress

    Returns:
        List of rewritten section contents in same order

    Raises:
        ValueError: If LLM client creation or calls fail
    """
    # Create client if not provided
    if client is None:
        client = LLMClient()

    # Load system prompt once if not provided
    if system_prompt is None:
        system_prompt = load_prompt("system")

    rewritten: list[str] = []

    for i, section in enumerate(sections):
        # Progress callback
        if progress_callback:
            progress_callback(i + 1, len(sections))

        # Rewrite this section
        try:
            rewritten_content = rewrite_section(section, client, system_prompt)
            rewritten.append(rewritten_content)
        except Exception as e:
            # On error, preserve original content
            print(f"Warning: Failed to rewrite section {i + 1}: {e}")
            print("Preserving original content for this section.")
            rewritten.append(section.content)

    return rewritten
