"""Tests for generic configuration system."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quarto4sbp.utils.config import (
    clear_config_cache,
    expand_env_vars,
    find_config_files,
    load_config,
    load_toml_file,
)


class TestExpandEnvVars(unittest.TestCase):
    """Tests for environment variable expansion."""

    def test_expand_single_var(self) -> None:
        """Test expanding a single environment variable."""
        os.environ["TEST_VAR"] = "test_value"
        try:
            result = expand_env_vars("${TEST_VAR}")
            self.assertEqual(result, "test_value")
        finally:
            del os.environ["TEST_VAR"]

    def test_expand_multiple_vars(self) -> None:
        """Test expanding multiple environment variables."""
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "value2"
        try:
            result = expand_env_vars("${VAR1} and ${VAR2}")
            self.assertEqual(result, "value1 and value2")
        finally:
            del os.environ["VAR1"]
            del os.environ["VAR2"]

    def test_expand_undefined_var(self) -> None:
        """Test that undefined variables are left unchanged."""
        result = expand_env_vars("${UNDEFINED_VAR}")
        self.assertEqual(result, "${UNDEFINED_VAR}")

    def test_no_vars_to_expand(self) -> None:
        """Test string with no variables to expand."""
        result = expand_env_vars("plain text")
        self.assertEqual(result, "plain text")

    def test_expand_var_in_middle(self) -> None:
        """Test expanding variable in middle of string."""
        os.environ["MIDDLE"] = "center"
        try:
            result = expand_env_vars("start ${MIDDLE} end")
            self.assertEqual(result, "start center end")
        finally:
            del os.environ["MIDDLE"]


class TestLoadTomlFile(unittest.TestCase):
    """Tests for TOML file loading."""

    def test_load_valid_toml(self) -> None:
        """Test loading a valid TOML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[section]\nkey = "value"\n')
            temp_path = Path(f.name)

        try:
            config = load_toml_file(temp_path)
            self.assertIn("section", config)
            self.assertEqual(config["section"], {"key": "value"})  # type: ignore[comparison-overlap]
        finally:
            temp_path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading a file that doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            load_toml_file(Path("/nonexistent/path.toml"))

    def test_load_invalid_toml(self) -> None:
        """Test loading invalid TOML syntax."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid toml syntax [[[")
            temp_path = Path(f.name)

        try:
            with self.assertRaises(ValueError) as ctx:
                load_toml_file(temp_path)
            self.assertIn("Invalid TOML", str(ctx.exception))
        finally:
            temp_path.unlink()


class TestFindConfigFiles(unittest.TestCase):
    """Tests for configuration file discovery."""

    def test_find_both_configs(self) -> None:
        """Test finding both user and local configs."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create user config
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text("[user]\n")

                # Create local config
                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)
                        local_config_path = Path("q4s.toml")
                        local_config_path.write_text("[local]\n")

                        user_config, local_config = find_config_files()

                        self.assertIsNotNone(user_config)
                        self.assertIsNotNone(local_config)
                        self.assertEqual(user_config, user_config_path)
                        self.assertEqual(local_config, local_config_path)
                finally:
                    os.chdir(original_cwd)

    def test_find_only_user_config(self) -> None:
        """Test finding only user config."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create user config
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text("[user]\n")

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)
                        # No local config

                        user_config, local_config = find_config_files()

                        self.assertIsNotNone(user_config)
                        self.assertIsNone(local_config)
                        self.assertEqual(user_config, user_config_path)
                finally:
                    os.chdir(original_cwd)

    def test_find_only_local_config(self) -> None:
        """Test finding only local config."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)
                # No user config

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)
                        local_config_path = Path("q4s.toml")
                        local_config_path.write_text("[local]\n")

                        user_config, local_config = find_config_files()

                        self.assertIsNone(user_config)
                        self.assertIsNotNone(local_config)
                        self.assertEqual(local_config, local_config_path)
                finally:
                    os.chdir(original_cwd)

    def test_find_no_configs(self) -> None:
        """Test when no config files exist."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        user_config, local_config = find_config_files()

                        self.assertIsNone(user_config)
                        self.assertIsNone(local_config)
                finally:
                    os.chdir(original_cwd)


class TestLoadConfig(unittest.TestCase):
    """Tests for full configuration loading and merging."""

    def test_load_empty_config(self) -> None:
        """Test loading when no config files exist."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        config = load_config(cache=False)

                        self.assertEqual(config, {})
                finally:
                    os.chdir(original_cwd)

    def test_load_only_user_config(self) -> None:
        """Test loading only user config."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create user config
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text("""
[section]
key1 = "user_value1"
key2 = "user_value2"
""")

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        config = load_config(cache=False)

                        self.assertIn("section", config)
                        self.assertEqual(config["section"]["key1"], "user_value1")
                        self.assertEqual(config["section"]["key2"], "user_value2")
                finally:
                    os.chdir(original_cwd)

    def test_load_only_local_config(self) -> None:
        """Test loading only local config."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Create local config
                        local_config_path = Path("q4s.toml")
                        local_config_path.write_text("""
[section]
key1 = "local_value1"
key2 = "local_value2"
""")

                        config = load_config(cache=False)

                        self.assertIn("section", config)
                        self.assertEqual(config["section"]["key1"], "local_value1")
                        self.assertEqual(config["section"]["key2"], "local_value2")
                finally:
                    os.chdir(original_cwd)

    def test_merge_user_and_local_configs(self) -> None:
        """Test that local config overrides user config."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create user config
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text("""
[section]
key1 = "user_value1"
key2 = "user_value2"
only_in_user = "user_only"
""")

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Create local config that overrides some values
                        local_config_path = Path("q4s.toml")
                        local_config_path.write_text("""
[section]
key1 = "local_override"
only_in_local = "local_only"
""")

                        config = load_config(cache=False)

                        self.assertIn("section", config)
                        # Local overrides user
                        self.assertEqual(config["section"]["key1"], "local_override")
                        # User value preserved when not overridden
                        self.assertEqual(config["section"]["key2"], "user_value2")
                        # Values from both configs present
                        self.assertEqual(config["section"]["only_in_user"], "user_only")
                        self.assertEqual(
                            config["section"]["only_in_local"], "local_only"
                        )
                finally:
                    os.chdir(original_cwd)

    def test_merge_nested_sections(self) -> None:
        """Test deep merging of nested sections."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create user config with nested structure
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text("""
[llm]
model = "user-model"
api_key = "user-key"

[llm.retry]
max_attempts = 3
backoff_factor = 2

[other_section]
value = "user"
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

                        config = load_config(cache=False)

                        # Check that nested merging works correctly
                        self.assertEqual(
                            config["llm"]["model"], "local-model"
                        )  # overridden
                        self.assertEqual(
                            config["llm"]["api_key"], "user-key"
                        )  # preserved
                        self.assertEqual(
                            config["llm"]["retry"]["max_attempts"], 5
                        )  # overridden
                        self.assertEqual(
                            config["llm"]["retry"]["backoff_factor"], 2
                        )  # preserved
                        self.assertEqual(
                            config["other_section"]["value"], "user"
                        )  # preserved
                finally:
                    os.chdir(original_cwd)

    def test_env_var_expansion(self) -> None:
        """Test that environment variables are expanded."""
        os.environ["TEST_API_KEY"] = "expanded-key-123"
        try:
            with patch("pathlib.Path.home") as mock_home:
                with tempfile.TemporaryDirectory() as tmpdir:
                    mock_home.return_value = Path(tmpdir)

                    original_cwd = os.getcwd()
                    try:
                        with tempfile.TemporaryDirectory() as local_dir:
                            os.chdir(local_dir)

                            # Create config with env var
                            local_config_path = Path("q4s.toml")
                            local_config_path.write_text("""
[llm]
api_key = "${TEST_API_KEY}"
model = "gpt-4"
""")

                            config = load_config(expand_vars=True, cache=False)

                            self.assertEqual(
                                config["llm"]["api_key"], "expanded-key-123"
                            )
                            self.assertEqual(config["llm"]["model"], "gpt-4")
                    finally:
                        os.chdir(original_cwd)
        finally:
            del os.environ["TEST_API_KEY"]

    def test_env_var_expansion_disabled(self) -> None:
        """Test that env var expansion can be disabled."""
        os.environ["TEST_VAR"] = "should-not-expand"
        try:
            with patch("pathlib.Path.home") as mock_home:
                with tempfile.TemporaryDirectory() as tmpdir:
                    mock_home.return_value = Path(tmpdir)

                    original_cwd = os.getcwd()
                    try:
                        with tempfile.TemporaryDirectory() as local_dir:
                            os.chdir(local_dir)

                            local_config_path = Path("q4s.toml")
                            local_config_path.write_text("""
[section]
value = "${TEST_VAR}"
""")

                            config = load_config(expand_vars=False, cache=False)

                            self.assertEqual(config["section"]["value"], "${TEST_VAR}")
                    finally:
                        os.chdir(original_cwd)
        finally:
            del os.environ["TEST_VAR"]

    def test_invalid_user_config_ignored(self) -> None:
        """Test that invalid user config is gracefully ignored."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create invalid user config
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text("invalid [[[toml")

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Valid local config
                        local_config_path = Path("q4s.toml")
                        local_config_path.write_text('[section]\nkey = "value"\n')

                        # Should not raise, should use local config
                        config = load_config(cache=False)

                        self.assertEqual(config["section"]["key"], "value")
                finally:
                    os.chdir(original_cwd)

    def test_invalid_local_config_ignored(self) -> None:
        """Test that invalid local config is gracefully ignored."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                # Create valid user config
                config_dir = Path(tmpdir) / ".config"
                config_dir.mkdir()
                user_config_path = config_dir / "q4s.toml"
                user_config_path.write_text('[section]\nkey = "user_value"\n')

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Invalid local config
                        local_config_path = Path("q4s.toml")
                        local_config_path.write_text("invalid [[[toml")

                        # Should not raise, should use user config
                        config = load_config(cache=False)

                        self.assertEqual(config["section"]["key"], "user_value")
                finally:
                    os.chdir(original_cwd)


class TestConfigCaching(unittest.TestCase):
    """Tests for configuration caching behavior."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        clear_config_cache()

    def tearDown(self) -> None:
        """Clear cache after each test."""
        clear_config_cache()

    def test_config_is_cached_by_default(self) -> None:
        """Test that config is cached on first load."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Create config
                        config_path = Path("q4s.toml")
                        config_path.write_text('[section]\nkey = "value1"\n')

                        # First load
                        config1 = load_config(cache=True)
                        self.assertEqual(config1["section"]["key"], "value1")

                        # Modify file
                        config_path.write_text('[section]\nkey = "value2"\n')

                        # Second load should return cached value
                        config2 = load_config(cache=True)
                        self.assertEqual(
                            config2["section"]["key"], "value1"
                        )  # Still cached

                        # Should be same object
                        self.assertIs(config1, config2)
                finally:
                    os.chdir(original_cwd)

    def test_cache_false_reloads_config(self) -> None:
        """Test that cache=False forces reload."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Create config
                        config_path = Path("q4s.toml")
                        config_path.write_text('[section]\nkey = "value1"\n')

                        # First load
                        config1 = load_config(cache=True)
                        self.assertEqual(config1["section"]["key"], "value1")

                        # Modify file
                        config_path.write_text('[section]\nkey = "value2"\n')

                        # Load with cache=False should get new value
                        config2 = load_config(cache=False)
                        self.assertEqual(config2["section"]["key"], "value2")

                        # Should be different objects
                        self.assertIsNot(config1, config2)
                finally:
                    os.chdir(original_cwd)

    def test_clear_cache_reloads_next_time(self) -> None:
        """Test that clear_config_cache() forces next load to reload."""
        with patch("pathlib.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)

                original_cwd = os.getcwd()
                try:
                    with tempfile.TemporaryDirectory() as local_dir:
                        os.chdir(local_dir)

                        # Create config
                        config_path = Path("q4s.toml")
                        config_path.write_text('[section]\nkey = "value1"\n')

                        # First load
                        config1 = load_config(cache=True)
                        self.assertEqual(config1["section"]["key"], "value1")

                        # Modify file and clear cache
                        config_path.write_text('[section]\nkey = "value2"\n')
                        clear_config_cache()

                        # Next load should get new value
                        config2 = load_config(cache=True)
                        self.assertEqual(config2["section"]["key"], "value2")

                        # Should be different objects
                        self.assertIsNot(config1, config2)
                finally:
                    os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
