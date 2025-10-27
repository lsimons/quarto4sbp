# 009 - LLM Integration Architecture

**Purpose:** Establish foundational LLM integration for AI-powered features like tone-of-voice rewriting and image generation

**Requirements:**
- Use a remote LiteLLM with URL + API key
- Support multiple models
- Configuration via environment variables and config file
- Prompt management system for organizing and versioning prompts
- Basic connectivity testing capability
- Rate limiting and error handling with retries
- Type-safe API with full typing support

**Design Approach:**
- **Single LLM provider**: Depend on external LiteLLM service for provider independence
- **Configuration hierarchy**: Environment variables override config file settings
- **Prompts as code**: Store prompts in `prompts/` directory as `.md` files
- **Fail-fast validation**: Check configuration and connectivity early
- **Dependency-optional**: LLM features optional, core functionality remains dependency-free

**Architecture Components:**

### 1. LLM Client
Use the `llm` library (`https://llm.datasette.io/`, `pip install llm`) directly, via a very simple/thin wrapper class (`quarto4sbp/llm/client.py`).

API docs: https://llm.datasette.io/en/stable/python-api.html

### 2. Configuration System (`quarto4sbp/llm/config.py`)
- Read from `~/.config/q4s.toml` or `q4s.toml` in project root
- Environment variables: `OPENAI_API_KEY`, `OPENAI_API_URL`, `OPENAI_API_MODEL`
- API provider: LiteLLM
- Default model: `azure/gpt-5-mini`

### 3. Prompt Management (`prompts/` directory)
```
prompts/
  tov/
    system.txt              # System prompt for tone of voice
    rewrite-slide.txt       # Prompt for slide rewriting
  viz/
    analyze-slide.txt       # Prompt for slide analysis
    generate-image.txt      # Prompt for image generation
  common/
    format-json.txt         # Common prompt snippets
```

### 4. Provider Implementations
- Single implementation for LiteLLM

### 5. Testing Command (`q4s llm test`)
- Verify configuration loaded correctly
- Test API connectivity with simple prompt
- Display token usage and response time
- Validate API key and permissions

**Configuration File Format:**
```toml
[llm]
model = "azure/gpt-5-mini"    # model name
api_key = "${OPENAI_API_KEY}" # supports env var expansion
base_url = ""                 # LiteLLM endpoint
max_tokens = 10000            # default max tokens
temperature = 0.7             # default temperature
timeout = 30                  # request timeout in seconds

[llm.retry]
max_attempts = 3              # retry attempts
backoff_factor = 2            # exponential backoff multiplier
```

**Environment Variables:**
- `OPENAI_API_KEY` - API key (required for cloud providers)
- `OPENAI_API_URL` - Custom API endpoint
- `OPENAI_API_MODEL` - Override model selection

**Implementation Notes:**
- Don't make HTTP requests directly, use the llm library
- Use `tomli` for TOML parsing (from stdlib in Python 3.11+)
- Store prompts as plain text files, load with `Path.read_text()`
- Support template variables in prompts using Python f-strings or simple `.format()`
- Error messages must be actionable (e.g., "Set OPENAI_API_KEY environment variable")
- Implement exponential backoff for rate limits (429 errors)
- Cache prompt file contents to avoid repeated disk reads

**Security Considerations:**
- Never log API keys
- Validate and sanitize user input before sending to LLM
- Set reasonable token limits to prevent cost overruns

**Testing Strategy:**
- Unit tests with mocked responses (no real API calls)
- Mock client for testing LLM-dependent features (see spec-010)
- Integration tests gated by `RUN_INTEGRATION_TESTS=1` (optional, uses real APIs)
- Test configuration loading from files and environment
- Test error handling (network errors, invalid API keys, rate limits)
- Test token counting accuracy (±10% acceptable for estimates)

**Status:** Draft
