"""Test helpers for LLM testing."""

import json
from pathlib import Path
from typing import Any


def get_fixtures_dir() -> Path:
    """Get the path to the LLM fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "llm"


def load_fixture_response(category: str, name: str) -> str:
    """Load a response fixture file.

    Args:
        category: Fixture category (e.g., 'common', 'tov', 'viz')
        name: Fixture name without extension (e.g., 'hello', 'rewrite-formal')

    Returns:
        Content of the fixture file

    Raises:
        FileNotFoundError: If fixture file doesn't exist
    """
    fixtures_dir = get_fixtures_dir()

    # Try .txt first, then .json
    for ext in [".txt", ".json"]:
        fixture_path = fixtures_dir / category / f"{name}{ext}"
        if fixture_path.exists():
            return fixture_path.read_text(encoding="utf-8")

    # If not found, raise helpful error
    raise FileNotFoundError(
        f"Fixture not found: {category}/{name}\nLooked in: {fixtures_dir / category}"
    )


def load_fixture_json(category: str, name: str) -> dict[str, Any]:
    """Load a JSON response fixture file.

    Args:
        category: Fixture category (e.g., 'viz')
        name: Fixture name without extension (e.g., 'analyze-slide')

    Returns:
        Parsed JSON content

    Raises:
        FileNotFoundError: If fixture file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    content = load_fixture_response(category, name)
    return json.loads(content)


def load_all_fixtures(category: str) -> dict[str, str]:
    """Load all fixture responses from a category.

    Args:
        category: Fixture category (e.g., 'common', 'tov', 'viz')

    Returns:
        Dictionary mapping fixture name to content
    """
    fixtures_dir = get_fixtures_dir() / category

    if not fixtures_dir.exists():
        return {}

    fixtures = {}
    for fixture_file in fixtures_dir.glob("*"):
        if fixture_file.is_file() and fixture_file.suffix in [".txt", ".json"]:
            name = fixture_file.stem
            fixtures[name] = fixture_file.read_text(encoding="utf-8")

    return fixtures  # pyright: ignore[reportUnknownVariableType]


def create_mock_with_responses(responses: dict[str, str]) -> Any:
    """Create mock client with response mappings.

    Args:
        responses: Dictionary mapping prompt patterns to responses

    Returns:
        MockLLMClient configured with responses
    """
    from tests.mocks.llm_client import MockLLMClient  # pyright: ignore[reportMissingImports,reportUnknownVariableType]

    return MockLLMClient(responses)  # pyright: ignore[reportUnknownVariableType]
