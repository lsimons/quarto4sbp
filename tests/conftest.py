"""Pytest configuration and fixtures for quarto4sbp tests."""

import pytest

from tests.helpers.llm import load_all_fixtures, load_fixture_response
from tests.mocks.llm_client import MockLLMClient


@pytest.fixture
def mock_llm() -> MockLLMClient:
    """Provide mock LLM client with common responses.

    Returns:
        MockLLMClient configured with basic test responses
    """
    client = MockLLMClient()
    client.add_response("hello", "Hello! I'm a test LLM.")
    client.add_response(r"what.*name", "I'm a mock LLM client for testing.")
    client.add_response(r"test", "This is a test response.")
    return client


@pytest.fixture
def mock_llm_common() -> MockLLMClient:
    """Mock LLM client with common fixtures loaded.

    Returns:
        MockLLMClient with all common category fixtures
    """
    fixtures = load_all_fixtures("common")
    return MockLLMClient(fixtures)


@pytest.fixture
def mock_llm_tov() -> MockLLMClient:
    """Mock LLM configured for tone-of-voice testing.

    Returns:
        MockLLMClient with tone-of-voice fixtures loaded
    """
    client = MockLLMClient()

    # Load tone-of-voice fixtures
    try:
        formal = load_fixture_response("tov", "rewrite-formal")
        casual = load_fixture_response("tov", "rewrite-casual")

        client.add_response(r"formal|professional|executive", formal)
        client.add_response(r"casual|informal|friendly", casual)
    except FileNotFoundError:
        # Fixtures not available, use basic responses
        client.set_default_response("Rewritten content")

    return client


@pytest.fixture
def mock_llm_viz() -> MockLLMClient:
    """Mock LLM configured for visualization/image testing.

    Returns:
        MockLLMClient with visualization fixtures loaded
    """
    client = MockLLMClient()

    # Load visualization fixtures
    try:
        analyze = load_fixture_response("viz", "analyze-slide")
        prompt = load_fixture_response("viz", "generate-prompt")

        client.add_response(r"analyze|analysis|slide", analyze)
        client.add_response(r"image|visual|generate.*prompt", prompt)
    except FileNotFoundError:
        # Fixtures not available, use basic responses
        client.set_default_response("Visual analysis result")

    return client


@pytest.fixture
def mock_llm_empty() -> MockLLMClient:
    """Empty mock LLM client for custom configuration in tests.

    Returns:
        MockLLMClient with no pre-configured responses
    """
    return MockLLMClient()


@pytest.fixture
def mock_llm_with_history() -> MockLLMClient:
    """Mock LLM client with some call history for testing.

    Returns:
        MockLLMClient with pre-populated call history
    """
    client = MockLLMClient()
    client.prompt("First test prompt")
    client.prompt("Second test prompt")
    client.prompt("Third test prompt")
    return client
