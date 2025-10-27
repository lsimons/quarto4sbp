# 010 - LLM Testing Infrastructure

**Purpose:** Enable testing of LLM-powered features without requiring real API calls or incurring costs

**Documentation:** See [llm-testing-guide.md](../llm-testing-guide.md) for comprehensive usage guide.

**Requirements:**
- Mock LLM client that mimics real client interface
- Fixture system for pre-defined LLM responses
- Support for both simple string responses and structured JSON responses
- Test helpers for common LLM testing patterns
- Integration with pytest fixtures
- No external API calls during normal test runs
- Optional integration tests with real API (gated by environment variable)

**Design Approach:**
- **Mock client class**: Implements same interface as real LLM client
- **Response fixtures**: Text/JSON files with canned responses
- **Pytest fixtures**: Reusable test fixtures for common scenarios (6 pre-configured fixtures)
- **Deterministic behavior**: Predictable responses for reliable testing
- **Easy debugging**: Clear error messages when fixtures missing or malformed

**Architecture Components:**

### 1. Mock LLM Client (`tests/mocks/llm_client.py`)
- Implements `MockLLMClient` class with `prompt()` method
- Records call history for test assertions
- Supports exact and regex pattern matching for responses
- Provides default response fallback
- Methods: `add_response()`, `set_default_response()`, `clear_history()`, `was_called_with()`, etc.

### 2. Response Fixtures (`tests/fixtures/llm/`)
Organized by category:
- `common/` - General-purpose test responses
- `tov/` - Tone-of-voice rewriting responses
- `viz/` - Visualization/image generation responses

### 3. Pytest Fixtures (`tests/conftest.py`)
Six pre-configured fixtures:
- `mock_llm` - Basic mock with common responses
- `mock_llm_common` - Pre-loaded with common category fixtures
- `mock_llm_tov` - Configured for tone-of-voice testing
- `mock_llm_viz` - Configured for visualization testing
- `mock_llm_empty` - Empty mock for custom configuration
- `mock_llm_with_history` - Mock with pre-populated call history

### 4. Test Helpers (`tests/helpers/llm.py`)
- `load_fixture_response(category, name)` - Load fixture as string
- `load_fixture_json(category, name)` - Load and parse JSON fixture
- `load_all_fixtures(category)` - Load all fixtures from category
- `assert_llm_called_with(mock, pattern)` - Assert prompt pattern was used
- `assert_llm_not_called_with(mock, pattern)` - Assert pattern was not used
- `assert_llm_call_count(mock, expected)` - Assert exact call count
- `get_llm_call_prompts(mock)` - Get list of all prompts from history

**Implementation Notes:**
- Response lookup order: exact match → regex match → default response
- Regex matching is case-insensitive
- Call history includes prompt text, kwargs, and call type
- Fixture files use `.txt` or `.json` extensions
- Example tests demonstrate all patterns (19 examples in `tests/test_llm_examples.py`)

**Testing Strategy:**
- Test the mock client itself (23 tests in `test_mock_llm_client.py`)
- Test fixture loading and parsing (12 tests in `test_llm_fixtures.py`)
- Test pytest fixture integration (18 tests in `test_llm_pytest_fixtures.py`)
- Example tests for all patterns (19 examples, skipped by default)

**Integration Tests:**
Controlled by `RUN_INTEGRATION_TESTS` environment variable (for real API testing, not LLM mocking).

**Example Usage:**
```python
def test_rewrite_tone_formal(mock_llm_tov):
    """Test formal tone rewriting."""
    result = rewrite_slide_content(
        "hey check this out",
        tone="formal",
        llm_client=mock_llm_tov
    )
    assert "Please review" in result
    assert_llm_called_with(mock_llm_tov, r"formal")
```

**Status:** Implemented