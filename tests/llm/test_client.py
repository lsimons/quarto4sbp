"""Tests for LLM client."""

import unittest
from unittest.mock import MagicMock, patch

from quarto4sbp.llm.client import LLMClient, create_client
from quarto4sbp.llm.config import LLMConfig


class TestLLMClientInitialization(unittest.TestCase):
    """Test cases for LLM client initialization."""

    @patch("quarto4sbp.llm.client.load_config")
    def test_init_without_config(self, mock_load_config: MagicMock) -> None:
        """Test initialization without explicit config loads from system."""
        mock_config = LLMConfig(
            model="test-model",
            api_key="test-key",
        )
        mock_load_config.return_value = mock_config

        client = LLMClient()

        self.assertEqual(client.config, mock_config)
        mock_load_config.assert_called_once()

    def test_init_with_config(self) -> None:
        """Test initialization with explicit config."""
        config = LLMConfig(
            model="test-model",
            api_key="test-key",
        )

        client = LLMClient(config)

        self.assertEqual(client.config, config)


class TestLLMClientPrompt(unittest.TestCase):
    """Test cases for LLM client prompt method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.config = LLMConfig(
            model="test-model",
            api_key="test-key",
            temperature=0.7,
            max_tokens=1000,
            timeout=30,
            max_attempts=3,
            backoff_factor=2,
        )

    @patch("quarto4sbp.llm.client.llm")
    def test_prompt_basic(self, mock_llm_module: MagicMock) -> None:
        """Test basic prompt call."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text.return_value = "Test response"
        mock_model = MagicMock()
        mock_model.prompt.return_value = mock_response
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)
        response = client.prompt("Test prompt")

        self.assertEqual(response, "Test response")
        mock_llm_module.get_model.assert_called_once_with("test-model")
        mock_model.prompt.assert_called_once()

    @patch("quarto4sbp.llm.client.llm")
    def test_prompt_with_system_message(self, mock_llm_module: MagicMock) -> None:
        """Test prompt with system message."""
        mock_response = MagicMock()
        mock_response.text.return_value = "Test response"
        mock_model = MagicMock()
        mock_model.prompt.return_value = mock_response
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)
        response = client.prompt("Test prompt", system="System message")

        self.assertEqual(response, "Test response")
        # Verify the prompt includes system message
        call_args = mock_model.prompt.call_args
        prompt_arg = call_args[0][0]
        self.assertIn("System message", prompt_arg)
        self.assertIn("Test prompt", prompt_arg)

    @patch("quarto4sbp.llm.client.llm")
    def test_prompt_with_overrides(self, mock_llm_module: MagicMock) -> None:
        """Test prompt with parameter overrides."""
        mock_response = MagicMock()
        mock_response.text.return_value = "Test response"
        mock_model = MagicMock()
        mock_model.prompt.return_value = mock_response
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)
        response = client.prompt(
            "Test prompt",
            model="different-model",
            temperature=0.5,
            max_tokens=500,
        )

        self.assertEqual(response, "Test response")
        # Verify different model was used
        mock_llm_module.get_model.assert_called_once_with("different-model")
        # Verify parameters were passed
        call_args = mock_model.prompt.call_args
        self.assertEqual(call_args[1]["temperature"], 0.5)
        self.assertEqual(call_args[1]["max_tokens"], 500)

    @patch("quarto4sbp.llm.client.time.sleep")
    @patch("quarto4sbp.llm.client.llm")
    def test_prompt_retry_on_failure(
        self, mock_llm_module: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """Test that prompt retries on failure."""
        mock_model = MagicMock()
        # First two calls fail, third succeeds
        mock_response = MagicMock()
        mock_response.text.return_value = "Success"
        mock_model.prompt.side_effect = [
            Exception("API error"),
            Exception("API error"),
            mock_response,
        ]
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)
        response = client.prompt("Test prompt")

        self.assertEqual(response, "Success")
        self.assertEqual(mock_model.prompt.call_count, 3)
        # Verify backoff sleep was called
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("quarto4sbp.llm.client.time.sleep")
    @patch("quarto4sbp.llm.client.llm")
    def test_prompt_fails_after_max_retries(
        self, mock_llm_module: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """Test that prompt raises error after max retries."""
        mock_model = MagicMock()
        mock_model.prompt.side_effect = Exception("API error")
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)

        with self.assertRaises(ValueError) as context:
            client.prompt("Test prompt")

        self.assertIn("failed after", str(context.exception))
        self.assertIn("3 attempts", str(context.exception))

        self.assertEqual(mock_model.prompt.call_count, 3)


class TestLLMClientTestConnectivity(unittest.TestCase):
    """Test cases for LLM client connectivity testing."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.config = LLMConfig(
            model="test-model",
            api_key="test-key",
        )

    @patch("quarto4sbp.llm.client.llm")
    def test_connectivity_success(self, mock_llm_module: MagicMock) -> None:
        """Test successful connectivity test."""
        mock_response = MagicMock()
        mock_response.text.return_value = "Hello from LLM"
        mock_model = MagicMock()
        mock_model.prompt.return_value = mock_response
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)
        result = client.test_connectivity()

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["response"])
        self.assertIsNone(result["error"])
        self.assertGreater(result["elapsed_time"], 0)
        self.assertEqual(result["model"], "test-model")

    @patch("quarto4sbp.llm.client.llm")
    def test_connectivity_failure(self, mock_llm_module: MagicMock) -> None:
        """Test failed connectivity test."""
        mock_model = MagicMock()
        mock_model.prompt.side_effect = Exception("Connection failed")
        mock_llm_module.get_model.return_value = mock_model

        client = LLMClient(self.config)
        result = client.test_connectivity()

        self.assertFalse(result["success"])
        self.assertIsNone(result["response"])
        self.assertIsNotNone(result["error"])
        self.assertIn("Connection failed", str(result["error"]))
        self.assertGreater(result["elapsed_time"], 0)
        self.assertEqual(result["model"], "test-model")


class TestCreateClient(unittest.TestCase):
    """Test cases for create_client convenience function."""

    @patch("quarto4sbp.llm.client.load_config")
    def test_create_client_without_config(self, mock_load_config: MagicMock) -> None:
        """Test creating client without config."""
        mock_config = LLMConfig(
            model="test-model",
            api_key="test-key",
        )
        mock_load_config.return_value = mock_config

        client = create_client()

        self.assertIsInstance(client, LLMClient)
        self.assertEqual(client.config, mock_config)

    def test_create_client_with_config(self) -> None:
        """Test creating client with config."""
        config = LLMConfig(
            model="test-model",
            api_key="test-key",
        )

        client = create_client(config)

        self.assertIsInstance(client, LLMClient)
        self.assertEqual(client.config, config)


if __name__ == "__main__":
    unittest.main()
