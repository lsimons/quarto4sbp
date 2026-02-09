"""Tests for LLM configuration system."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quarto4sbp.llm.config import LLMConfig, load_config
from quarto4sbp.utils.config import clear_config_cache


class TestLoadConfig(unittest.TestCase):
    """Tests for LLM configuration loading."""

    def setUp(self) -> None:
        """Set up test environment."""
        # Save original environment
        self.original_env = os.environ.copy()
        # Clear LLM env vars to prevent leakage from real environment
        for key in list(os.environ.keys()):
            if key.startswith("LLM_"):
                del os.environ[key]
        # Clear config cache for test isolation
        clear_config_cache()

    def tearDown(self) -> None:
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
        # Clear config cache after test
        clear_config_cache()

    def test_load_config_from_env_only(self) -> None:
        """Test loading configuration from environment variables only."""
        os.environ["LLM_API_KEY"] = "test-key-123"

        config = load_config()

        self.assertEqual(config.api_key, "test-key-123")
        self.assertEqual(config.model, "azure/gpt-5-mini")  # default
        self.assertEqual(config.base_url, "https://litellm.sbp.ai/v1/")
        self.assertEqual(config.max_tokens, 10000)
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.timeout, 30)

    def test_load_config_with_all_env_vars(self) -> None:
        """Test loading with all environment variables set."""
        os.environ["LLM_API_KEY"] = "env-key"
        os.environ["LLM_BASE_URL"] = "https://api.example.com"
        os.environ["LLM_MODEL"] = "gpt-4"

        config = load_config()

        self.assertEqual(config.api_key, "env-key")
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.base_url, "https://api.example.com")

    def test_load_config_missing_api_key(self) -> None:
        """Test that missing API key raises ValueError."""
        # Clear any API key from environment
        os.environ.pop("LLM_API_KEY", None)

        with self.assertRaises(ValueError) as ctx:
            load_config()

        self.assertIn("API key not configured", str(ctx.exception))
        self.assertIn("LLM_API_KEY", str(ctx.exception))

    def test_load_config_from_toml_file(self) -> None:
        """Test loading configuration from TOML file."""
        with (
            patch("pathlib.Path.home") as mock_home,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_home.return_value = Path(tmpdir)

            original_cwd = os.getcwd()
            try:
                with tempfile.TemporaryDirectory() as local_dir:
                    os.chdir(local_dir)
                    config_path = Path("q4s.toml")
                    config_path.write_text("""
[llm]
model = "custom-model"
api_key = "file-key-456"
base_url = "https://custom.api.com"
max_tokens = 5000
temperature = 0.5
timeout = 60

[llm.retry]
max_attempts = 5
backoff_factor = 3
""")

                    config = load_config()

                    self.assertEqual(config.api_key, "file-key-456")
                    self.assertEqual(config.model, "custom-model")
                    self.assertEqual(config.base_url, "https://custom.api.com")
                    self.assertEqual(config.max_tokens, 5000)
                    self.assertEqual(config.temperature, 0.5)
                    self.assertEqual(config.timeout, 60)
                    self.assertEqual(config.max_attempts, 5)
                    self.assertEqual(config.backoff_factor, 3)
            finally:
                os.chdir(original_cwd)

    def test_env_vars_override_toml(self) -> None:
        """Test that environment variables override TOML settings."""
        with (
            patch("pathlib.Path.home") as mock_home,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_home.return_value = Path(tmpdir)

            original_cwd = os.getcwd()
            try:
                with tempfile.TemporaryDirectory() as local_dir:
                    os.chdir(local_dir)
                    config_path = Path("q4s.toml")
                    config_path.write_text("""
[llm]
model = "toml-model"
api_key = "toml-key"
base_url = "https://toml.api.com"
""")

                    os.environ["LLM_API_KEY"] = "env-key-override"
                    os.environ["LLM_MODEL"] = "env-model-override"
                    os.environ["LLM_BASE_URL"] = "https://env.api.com"

                    config = load_config()

                    # Environment should override TOML
                    self.assertEqual(config.api_key, "env-key-override")
                    self.assertEqual(config.model, "env-model-override")
                    self.assertEqual(config.base_url, "https://env.api.com")
            finally:
                os.chdir(original_cwd)

    def test_env_var_expansion_in_toml(self) -> None:
        """Test that environment variables are expanded in TOML values."""
        with (
            patch("pathlib.Path.home") as mock_home,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_home.return_value = Path(tmpdir)

            original_cwd = os.getcwd()
            try:
                with tempfile.TemporaryDirectory() as local_dir:
                    os.chdir(local_dir)
                    config_path = Path("q4s.toml")
                    config_path.write_text("""
[llm]
api_key = "${MY_SECRET_KEY}"
model = "gpt-4"
""")

                    os.environ["MY_SECRET_KEY"] = "expanded-key-789"

                    config = load_config()

                    self.assertEqual(config.api_key, "expanded-key-789")
                    self.assertEqual(config.model, "gpt-4")
            finally:
                os.chdir(original_cwd)

    def test_partial_toml_config(self) -> None:
        """Test TOML with only some fields configured."""
        with (
            patch("pathlib.Path.home") as mock_home,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_home.return_value = Path(tmpdir)

            original_cwd = os.getcwd()
            try:
                with tempfile.TemporaryDirectory() as local_dir:
                    os.chdir(local_dir)
                    config_path = Path("q4s.toml")
                    config_path.write_text("""
[llm]
api_key = "partial-key"
model = "partial-model"
# Other fields use defaults
""")

                    config = load_config()

                    self.assertEqual(config.api_key, "partial-key")
                    self.assertEqual(config.model, "partial-model")
                    # Defaults
                    self.assertEqual(config.base_url, "https://litellm.sbp.ai/v1/")
                    self.assertEqual(config.max_tokens, 10000)
                    self.assertEqual(config.temperature, 0.7)
            finally:
                os.chdir(original_cwd)

    def test_invalid_toml_ignored(self) -> None:
        """Test that invalid TOML file is gracefully ignored."""
        with (
            patch("pathlib.Path.home") as mock_home,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_home.return_value = Path(tmpdir)

            original_cwd = os.getcwd()
            try:
                with tempfile.TemporaryDirectory() as local_dir:
                    os.chdir(local_dir)
                    config_path = Path("q4s.toml")
                    config_path.write_text("invalid [[[toml")

                    os.environ["LLM_API_KEY"] = "fallback-key"

                    # Should not raise, should fall back to env vars
                    config = load_config()

                    self.assertEqual(config.api_key, "fallback-key")
            finally:
                os.chdir(original_cwd)

    def test_merge_user_and_local_configs(self) -> None:
        """Test that local config overrides user config for LLM settings."""
        with (
            patch("pathlib.Path.home") as mock_home,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_home.return_value = Path(tmpdir)

            # Create user config
            config_dir = Path(tmpdir) / ".config"
            config_dir.mkdir()
            user_config_path = config_dir / "q4s.toml"
            user_config_path.write_text("""
[llm]
model = "user-model"
api_key = "user-key"
max_tokens = 8000

[llm.retry]
max_attempts = 3
backoff_factor = 2
""")

            original_cwd = os.getcwd()
            try:
                with tempfile.TemporaryDirectory() as local_dir:
                    os.chdir(local_dir)

                    # Create local config that partially overrides
                    local_config_path = Path("q4s.toml")
                    local_config_path.write_text("""
[llm]
model = "local-model"

[llm.retry]
max_attempts = 5
""")

                    config = load_config()

                    # Check that merging works correctly
                    self.assertEqual(config.model, "local-model")  # overridden
                    self.assertEqual(config.api_key, "user-key")  # preserved
                    self.assertEqual(config.max_tokens, 8000)  # preserved
                    self.assertEqual(config.max_attempts, 5)  # overridden
                    self.assertEqual(config.backoff_factor, 2)  # preserved
            finally:
                os.chdir(original_cwd)


class TestLLMConfig(unittest.TestCase):
    """Tests for LLMConfig dataclass."""

    def test_create_config_with_defaults(self) -> None:
        """Test creating config with minimal required fields."""
        config = LLMConfig(model="test-model", api_key="test-key")

        self.assertEqual(config.model, "test-model")
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.base_url, "https://litellm.sbp.ai/v1/")
        self.assertEqual(config.max_tokens, 10000)
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_attempts, 3)
        self.assertEqual(config.backoff_factor, 2)

    def test_create_config_with_all_fields(self) -> None:
        """Test creating config with all fields specified."""
        config = LLMConfig(
            model="custom-model",
            api_key="custom-key",
            base_url="https://custom.url",
            max_tokens=5000,
            temperature=0.9,
            timeout=60,
            max_attempts=5,
            backoff_factor=3,
        )

        self.assertEqual(config.model, "custom-model")
        self.assertEqual(config.api_key, "custom-key")
        self.assertEqual(config.base_url, "https://custom.url")
        self.assertEqual(config.max_tokens, 5000)
        self.assertEqual(config.temperature, 0.9)
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.max_attempts, 5)
        self.assertEqual(config.backoff_factor, 3)


if __name__ == "__main__":
    unittest.main()
