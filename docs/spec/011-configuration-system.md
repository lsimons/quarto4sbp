# 011 - Generic Configuration System

**Purpose:** Provide reusable TOML-based configuration loading with merging, caching, and environment variable expansion for all q4s features

**Requirements:**
- Load configuration from standard TOML file locations
- Merge user-level and project-level configs with proper override precedence
- Expand environment variables in configuration values
- Cache configuration on startup for performance
- Support test isolation with cache clearing
- Type-safe API with full typing support
- Gracefully handle missing or invalid config files

**Design Approach:**
- **Dual-location loading**: Support both user (~/.config/q4s.toml) and local (./q4s.toml) configs
- **Deep merging**: Recursively merge nested sections, local overrides user
- **One-time load**: Cache config on first access, reuse cached version
- **Variable expansion**: Support ${VAR_NAME} syntax in TOML values
- **Fail-safe**: Invalid configs are ignored, don't break the application
- **Test-friendly**: Provide cache control for test isolation

**Architecture:**

### File Locations (in load order)
1. `~/.config/q4s.toml` - User/global configuration (base)
2. `./q4s.toml` - Project/local configuration (overrides)

### Core Functions (`quarto4sbp/utils/config.py`)

**`load_config(expand_vars=True, cache=True) -> dict[str, Any]`**
- Main entry point for loading configuration
- Merges user and local configs with deep merge
- Caches result by default for performance
- Returns empty dict if no config files found

**`find_config_files() -> tuple[Optional[Path], Optional[Path]]`**
- Discovers config files in standard locations
- Returns (user_config_path, local_config_path)
- Returns None for paths that don't exist

**`load_toml_file(path: Path) -> dict[str, Any]`**
- Loads a single TOML file
- Validates syntax
- Raises FileNotFoundError or ValueError on errors

**`expand_env_vars(value: str) -> str`**
- Expands ${VAR_NAME} patterns in strings
- Leaves undefined variables unchanged
- Used for API keys and other secrets

**`clear_config_cache() -> None`**
- Clears cached configuration
- Used by tests for isolation

### Merging Behavior

Deep merge with override precedence:
```toml
# ~/.config/q4s.toml (base)
[llm]
model = "gpt-4"
api_key = "${OPENAI_API_KEY}"
max_tokens = 10000

[llm.retry]
max_attempts = 3
backoff_factor = 2
```

```toml
# ./q4s.toml (overrides)
[llm]
model = "gpt-3.5-turbo"  # overrides user setting

[llm.retry]
max_attempts = 5  # overrides user setting
# backoff_factor inherited from user config
```

Result:
```python
{
  "llm": {
    "model": "gpt-3.5-turbo",        # from local
    "api_key": "<expanded>",          # from user
    "max_tokens": 10000,              # from user
    "retry": {
      "max_attempts": 5,              # from local
      "backoff_factor": 2             # from user
    }
  }
}
```

### Caching Behavior

**Production usage (cached):**
```python
from quarto4sbp.utils.config import load_config

# First call - loads and caches
config = load_config()

# Subsequent calls - returns cached version (fast!)
config = load_config()
```

**Test usage (uncached):**
```python
from quarto4sbp.utils.config import load_config, clear_config_cache

def setUp():
    clear_config_cache()  # Ensure clean slate

def test_something():
    config = load_config(cache=False)  # Force reload
```

### Environment Variable Expansion

Supports `${VAR_NAME}` syntax:
```toml
[llm]
api_key = "${OPENAI_API_KEY}"
base_url = "${CUSTOM_API_URL}"
```

Variables are expanded after merging, before caching. Undefined variables remain as literals.

### Error Handling

Configuration errors are **non-fatal**:
- Missing config files: Return empty dict
- Invalid TOML syntax: Ignore that file, try next location
- File read errors: Ignore that file, try next location

This ensures the application works even without configuration files (env vars can still be used).

### Feature-Specific Usage

Each feature loads its section from the merged config:

```python
# llm/config.py
from quarto4sbp.utils.config import load_config as load_toml_config

def load_config() -> LLMConfig:
    toml_data = load_toml_config()
    llm_section = toml_data.get("llm", {})
    # Extract LLM-specific settings...
```

This allows multiple features to share the same config files while maintaining separation of concerns.

### Testing Strategy

- Unit tests use `cache=False` for independence
- Integration tests use `clear_config_cache()` in setUp/tearDown
- Mock `Path.home()` for user config path control
- Use `os.chdir()` with temp directories for local config testing
- Test merging, expansion, caching, and error handling separately

**Status:** Implemented