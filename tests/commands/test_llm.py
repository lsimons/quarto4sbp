"""Tests for llm command."""

import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from quarto4sbp.commands.llm import cmd_llm
from quarto4sbp.llm.config import LLMConfig


class TestCmdLlm(unittest.TestCase):
    """Test cases for llm command."""

    def test_no_subcommand(self) -> None:
        """Test that missing subcommand shows usage."""
        stderr = StringIO()
        with patch("sys.stderr", stderr):
            result = cmd_llm([])

        self.assertEqual(result, 1)
        output = stderr.getvalue()
        self.assertIn("Usage: q4s llm test", output)

    def test_invalid_subcommand(self) -> None:
        """Test that invalid subcommand shows usage."""
        stderr = StringIO()
        with patch("sys.stderr", stderr):
            result = cmd_llm(["invalid"])

        self.assertEqual(result, 1)
        output = stderr.getvalue()
        self.assertIn("Usage: q4s llm test", output)

    @patch("quarto4sbp.commands.llm.load_config")
    def test_configuration_load_error(self, mock_load_config: MagicMock) -> None:
        """Test handling of configuration loading errors."""
        mock_load_config.side_effect = ValueError("Missing API key")

        stderr = StringIO()
        with patch("sys.stderr", stderr):
            result = cmd_llm(["test"])

        self.assertEqual(result, 1)
        output = stderr.getvalue()
        self.assertIn("Configuration error", output)
        self.assertIn("Missing API key", output)

    @patch("quarto4sbp.commands.llm.LLMClient")
    @patch("quarto4sbp.commands.llm.load_config")
    def test_successful_connectivity_test(
        self, mock_load_config: MagicMock, mock_client_class: MagicMock
    ) -> None:
        """Test successful LLM connectivity test."""
        mock_config = LLMConfig(
            model="test-model",
            api_key="test-key",
            base_url="https://api.example.com",
            max_tokens=1000,
            temperature=0.7,
            timeout=30,
        )
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.test_connectivity.return_value = {
            "success": True,
            "response": "Hello from LLM",
            "error": None,
            "elapsed_time": 1.23,
            "model": "test-model",
        }
        mock_client_class.return_value = mock_client

        stdout = StringIO()
        with patch("sys.stdout", stdout):
            result = cmd_llm(["test"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("Configuration loaded successfully", output)
        self.assertIn("test-model", output)
        self.assertIn("https://api.example.com", output)
        self.assertIn("API call successful", output)
        self.assertIn("Hello from LLM", output)
        self.assertIn("1.23s", output)
        self.assertIn("working correctly", output)

    @patch("quarto4sbp.commands.llm.LLMClient")
    @patch("quarto4sbp.commands.llm.load_config")
    def test_failed_connectivity_test(
        self, mock_load_config: MagicMock, mock_client_class: MagicMock
    ) -> None:
        """Test failed LLM connectivity test."""
        mock_config = LLMConfig(model="test-model", api_key="test-key")
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.test_connectivity.return_value = {
            "success": False,
            "response": None,
            "error": "Connection timeout",
            "elapsed_time": 30.0,
            "model": "test-model",
        }
        mock_client_class.return_value = mock_client

        stdout = StringIO()
        stderr = StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            result = cmd_llm(["test"])

        self.assertEqual(result, 1)
        output = stderr.getvalue()
        self.assertIn("API call failed", output)
        self.assertIn("Connection timeout", output)
        self.assertIn("30.00s", output)
        self.assertIn("Troubleshooting", output)
        self.assertIn("OPENAI_API_KEY", output)

    @patch("quarto4sbp.commands.llm.LLMClient")
    @patch("quarto4sbp.commands.llm.load_config")
    def test_config_without_base_url(
        self, mock_load_config: MagicMock, mock_client_class: MagicMock
    ) -> None:
        """Test configuration display without base_url."""
        mock_config = LLMConfig(
            model="test-model",
            api_key="test-key",
            base_url=None,
            max_tokens=1000,
            temperature=0.7,
            timeout=30,
        )
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.test_connectivity.return_value = {
            "success": True,
            "response": "OK",
            "error": None,
            "elapsed_time": 0.5,
            "model": "test-model",
        }
        mock_client_class.return_value = mock_client

        stdout = StringIO()
        with patch("sys.stdout", stdout):
            result = cmd_llm(["test"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("test-model", output)
        self.assertNotIn("Base URL:", output)  # Should not show if None

    @patch("quarto4sbp.commands.llm.LLMClient")
    @patch("quarto4sbp.commands.llm.load_config")
    def test_client_initialization_error(
        self, mock_load_config: MagicMock, mock_client_class: MagicMock
    ) -> None:
        """Test handling of client initialization errors."""
        mock_config = LLMConfig(model="test-model", api_key="test-key")
        mock_load_config.return_value = mock_config
        mock_client_class.side_effect = Exception("Unexpected error")

        stderr = StringIO()
        with patch("sys.stderr", stderr):
            result = cmd_llm(["test"])

        self.assertEqual(result, 1)
        output = stderr.getvalue()
        self.assertIn("Failed to initialize client", output)
        self.assertIn("Unexpected error", output)


if __name__ == "__main__":
    unittest.main()
