# 010 - LLM Testing Infrastructure

**Purpose:** Enable testing of LLM-powered features without requiring real API calls or incurring costs

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
- **Response fixtures**: JSON/YAML files with canned responses
- **Pytest fixtures**: Reusable test fixtures for common scenarios
- **Deterministic behavior**: Predictable responses for reliable testing
- **Easy debugging**: Clear error messages when fixtures missing or malformed

**Architecture Components:**

### 1. Mock LLM Client (`tests/mocks/llm_client.py`)
```python
class MockLLMClient:
    """Mock LLM client for testing without API calls."""
    
    def __init__(self, responses: dict[str, str] | None = None):
        """Initialize with optional response mapping."""
        self.responses = responses or {}
        self.call_history: list[dict] = []
    
    def prompt(self, prompt: str, **kwargs) -> str:
        """Return canned response for prompt."""
        # Record call for assertions
        # Return matching response or raise error
    
    def add_response(self, pattern: str, response: str):
        """Add a response mapping."""
```

### 2. Response Fixtures (`tests/fixtures/llm/`)
```
tests/fixtures/llm/
  tov/
    rewrite-formal.txt         # Response for formal rewrite
    rewrite-casual.txt         # Response for casual rewrite
  viz/
    analyze-slide.json         # Structured response for slide analysis
    generate-prompt.txt        # Image generation prompt
  common/
    hello.txt                  # Simple test response
```

### 3. Pytest Fixtures (`tests/conftest.py`)
```python
@pytest.fixture
def mock_llm():
    """Provide mock LLM client with common responses."""
    client = MockLLMClient()
    client.add_response("hello", "Hello! I'm a test LLM.")
    return client

@pytest.fixture
def mock_llm_tov():
    """Mock LLM configured for tone-of-voice testing."""
    responses = load_fixture_responses("tov")
    return MockLLMClient(responses)
```

### 4. Test Helpers (`tests/helpers/llm.py`)
```python
def load_fixture_response(category: str, name: str) -> str:
    """Load a response fixture file."""
    
def assert_llm_called_with(mock: MockLLMClient, pattern: str):
    """Assert LLM was called with prompt matching pattern."""
    
def create_mock_with_responses(responses: dict[str, str]) -> MockLLMClient:
    """Create mock client with response mappings."""
```

**Implementation Notes:**
- Mock client stores call history for assertions in tests
- Support regex patterns for flexible response matching
- Load fixtures lazily (only when needed)
- Provide clear error messages when response not found
- Mock client should have same method signatures as real client
- Use `Path(__file__).parent` to locate fixture files
- Consider response lookup order: exact match, regex match, default

**Testing Strategy:**
- Test the mock client itself (meta-testing)
- Test fixture loading and parsing
- Test pytest fixture integration
- Ensure mock behavior matches real client interface
- Example tests for each fixture category

**Integration Tests:**
```python
@pytest.mark.skipif(
    not os.environ.get('RUN_INTEGRATION_TESTS'),
    reason="Integration tests require real LLM API"
)
def test_real_llm_connectivity():
    """Test with real LLM client (optional)."""
```

**Example Usage in Tests:**
```python
def test_rewrite_tone_formal(mock_llm_tov):
    """Test formal tone rewriting."""
    result = rewrite_slide_content(
        "hey check this out",
        tone="formal",
        llm_client=mock_llm_tov
    )
    assert "Please review" in result
    assert_llm_called_with(mock_llm_tov, "formal")
```

**Future Enhancements:**
- Record/replay mode to capture real API responses
- Fuzzy matching for prompts
- Streaming response support
- Token counting simulation
- Error simulation (rate limits, timeouts)

**Status:** Draft