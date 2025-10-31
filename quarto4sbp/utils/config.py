"""Generic configuration system for loading and merging TOML files.

This module provides utilities for loading TOML configuration files from
standard locations with proper merging behavior:

1. ~/.config/q4s.toml (user/base config)
2. ./q4s.toml (project/local config - overrides base)

Environment variable expansion is supported using ${VAR_NAME} syntax.

The config is cached on first load for performance. Tests can use
cache=False or clear_config_cache() to reload.
"""

import os
import re
from pathlib import Path
from typing import Any, Optional

# Module-level cache for configuration
_config_cache: Optional[dict[str, Any]] = None

import tomllib  # Python 3.11+


def expand_env_vars(value: str) -> str:
    """Expand environment variables in string values.

    Supports ${VAR_NAME} syntax.

    Args:
        value: String that may contain ${VAR_NAME} patterns

    Returns:
        String with environment variables expanded

    Examples:
        >>> os.environ["MY_VAR"] = "test"
        >>> expand_env_vars("${MY_VAR}")
        'test'
        >>> expand_env_vars("prefix-${MY_VAR}-suffix")
        'prefix-test-suffix'
    """

    def replace_var(match: re.Match[str]) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    return re.sub(r"\$\{([A-Z_][A-Z0-9_]*)\}", replace_var, value)


def _expand_env_vars_recursive(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively expand environment variables in nested dict values.

    Args:
        data: Dictionary that may contain strings with ${VAR_NAME} patterns

    Returns:
        Dictionary with all string values having env vars expanded
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = expand_env_vars(value)
        elif isinstance(value, dict):
            result[key] = _expand_env_vars_recursive(value)  # pyright: ignore[reportUnknownArgumentType]
        else:
            result[key] = value
    return result


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, with override taking precedence.

    Args:
        base: Base dictionary
        override: Override dictionary (values take precedence)

    Returns:
        Merged dictionary

    Examples:
        >>> base = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> override = {"b": {"d": 4, "e": 5}, "f": 6}
        >>> _merge_dicts(base, override)
        {'a': 1, 'b': {'c': 2, 'd': 4, 'e': 5}, 'f': 6}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = _merge_dicts(result[key], value)  # pyright: ignore[reportUnknownArgumentType]
        else:
            # Override takes precedence
            result[key] = value

    return result


def load_toml_file(path: Path) -> dict[str, Any]:
    """Load a single TOML file.

    Args:
        path: Path to TOML file

    Returns:
        Parsed TOML data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If TOML is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        with open(path, "rb") as f:
            data: dict[str, Any] = tomllib.load(f)  # type: ignore[no-redef]
    except Exception as e:
        raise ValueError(f"Invalid TOML in {path}: {e}") from e

    return data  # pyright: ignore[reportUnknownVariableType]


def find_config_files() -> tuple[Optional[Path], Optional[Path]]:
    """Find configuration files in standard locations.

    Returns:
        Tuple of (user_config_path, local_config_path)
        Either or both may be None if not found

    Examples:
        >>> user_config, local_config = find_config_files()
        >>> # user_config might be ~/.config/q4s.toml
        >>> # local_config might be ./q4s.toml
    """
    # User config in home directory
    user_config = Path.home() / ".config" / "q4s.toml"
    user_config_exists = user_config.exists()

    # Local config in current directory
    local_config = Path("q4s.toml")
    local_config_exists = local_config.exists()

    return (
        user_config if user_config_exists else None,
        local_config if local_config_exists else None,
    )


def clear_config_cache() -> None:
    """Clear the cached configuration.

    Useful for tests that need to reload configuration.
    """
    global _config_cache
    _config_cache = None


def load_config(expand_vars: bool = True, cache: bool = True) -> dict[str, Any]:
    """Load and merge configuration from standard TOML files.

    Loads configuration in order:
    1. ~/.config/q4s.toml (base config)
    2. ./q4s.toml (local config - overrides base)

    By default, configuration is cached on first load. Subsequent calls
    return the cached config unless cache=False is specified.

    Args:
        expand_vars: Whether to expand ${VAR_NAME} environment variables
        cache: Whether to cache the config (default True for performance)

    Returns:
        Merged configuration dictionary

    Examples:
        >>> config = load_config()  # Loads and caches
        >>> config = load_config()  # Returns cached version
        >>> config = load_config(cache=False)  # Forces reload
        >>> llm_config = config.get("llm", {})
    """
    global _config_cache

    # Return cached config if available and caching is enabled
    if cache and _config_cache is not None:
        return _config_cache
    user_config_path, local_config_path = find_config_files()

    # Start with empty config
    merged_config: dict[str, Any] = {}

    # Load and merge user config first (base)
    if user_config_path:
        try:
            user_data = load_toml_file(user_config_path)
            merged_config = user_data
        except (FileNotFoundError, ValueError):
            # User config errors are non-fatal
            pass

    # Load and merge local config (overrides)
    if local_config_path:
        try:
            local_data = load_toml_file(local_config_path)
            merged_config = _merge_dicts(merged_config, local_data)
        except (FileNotFoundError, ValueError):
            # Local config errors are non-fatal
            pass

    # Expand environment variables if requested
    if expand_vars:
        merged_config = _expand_env_vars_recursive(merged_config)

    # Cache the config if caching is enabled
    if cache:
        _config_cache = merged_config

    return merged_config
