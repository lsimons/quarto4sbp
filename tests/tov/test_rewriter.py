"""Tests for content rewriter."""

import unittest

from quarto4sbp.tov.parser import QmdSection
from quarto4sbp.tov.rewriter import load_prompt, rewrite_section, rewrite_content
from tests.mocks.llm_client import MockLLMClient


class TestLoadPrompt(unittest.TestCase):
    """Test prompt loading functionality."""

    def test_load_system_prompt(self):
        """Test loading system prompt."""
        prompt = load_prompt("system")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("tone of voice", prompt.lower())

    def test_load_rewrite_prompt(self):
        """Test loading rewrite-slide prompt."""
        prompt = load_prompt("rewrite-slide")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("{tone_guidelines}", prompt)
        self.assertIn("{slide_content}", prompt)

    def test_load_nonexistent_prompt_raises_error(self):
        """Test that loading nonexistent prompt raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_prompt("nonexistent-prompt")


class TestRewriteSection(unittest.TestCase):
    """Test section rewriting functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        self.section = QmdSection(
            content="# Original Title\n\nOriginal content here.\n",
            start_line=0,
            end_line=2,
            level=1,
        )

    def test_rewrite_section_basic(self):
        """Test basic section rewriting."""
        # Set up mock response
        self.mock_client.add_response(
            r".*Original content.*", "# Rewritten Title\n\nRewritten content here.\n"
        )

        result = rewrite_section(
            self.section,
            self.mock_client,  # pyright: ignore[reportArgumentType]
            system_prompt="Test system prompt",
        )

        self.assertIn("Rewritten", result)
        self.assertNotIn("Original content here", result)

    def test_rewrite_section_preserves_trailing_newline(self):
        """Test that trailing newline is preserved."""
        section_with_newline = QmdSection(content="Content\n", start_line=0, end_line=0)

        self.mock_client.add_response(r".*", "Rewritten")  # No newline

        result = rewrite_section(
            section_with_newline,
            self.mock_client,  # pyright: ignore[reportArgumentType]
            system_prompt="Test",
        )

        self.assertTrue(result.endswith("\n"))

    def test_rewrite_section_loads_default_system_prompt(self):
        """Test that system prompt is loaded if not provided."""
        self.mock_client.add_response(r".*", "Rewritten content")

        # Don't provide system_prompt, should load default
        result = rewrite_section(self.section, self.mock_client)  # pyright: ignore[reportArgumentType,reportCallIssue]

        self.assertEqual(result, "Rewritten content\n")
        # Verify LLM was called
        self.assertEqual(len(self.mock_client.call_history), 1)

    def test_rewrite_section_call_history(self):
        """Test that rewrite section records call history."""
        self.mock_client.add_response(r".*", "Result")

        rewrite_section(self.section, self.mock_client, system_prompt="Test")  # pyright: ignore[reportArgumentType,reportCallIssue]

        self.assertEqual(len(self.mock_client.call_history), 1)
        call = self.mock_client.call_history[0]
        self.assertIn("prompt", call)
        # System prompt is passed in kwargs
        self.assertIn("kwargs", call)
        self.assertIn("system", call["kwargs"])


class TestRewriteContent(unittest.TestCase):
    """Test content rewriting for multiple sections."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        self.sections = [
            QmdSection(
                content="# Section One\n\nContent 1.\n", start_line=0, end_line=2
            ),
            QmdSection(
                content="# Section Two\n\nContent 2.\n", start_line=3, end_line=5
            ),
            QmdSection(
                content="# Section Three\n\nContent 3.\n", start_line=6, end_line=8
            ),
        ]

    def test_rewrite_multiple_sections(self):
        """Test rewriting multiple sections."""
        self.mock_client.add_response(r".*Content 1.*", "Rewritten 1\n")
        self.mock_client.add_response(r".*Content 2.*", "Rewritten 2\n")
        self.mock_client.add_response(r".*Content 3.*", "Rewritten 3\n")

        results = rewrite_content(
            self.sections,
            client=self.mock_client,  # pyright: ignore[reportArgumentType,reportCallIssue]
            system_prompt="Test",
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], "Rewritten 1\n")
        self.assertEqual(results[1], "Rewritten 2\n")
        self.assertEqual(results[2], "Rewritten 3\n")

    def test_rewrite_empty_sections_list(self):
        """Test rewriting empty sections list."""
        results = rewrite_content([], client=self.mock_client, system_prompt="Test")  # pyright: ignore[reportArgumentType,reportCallIssue]
        self.assertEqual(results, [])

    def test_rewrite_with_progress_callback(self):
        """Test that progress callback is called."""
        self.mock_client.add_response(r".*", "Rewritten")

        progress_calls: list[tuple[int, int]] = []

        def progress_callback(current: int, total: int) -> None:
            progress_calls.append((current, total))

        rewrite_content(
            self.sections,
            client=self.mock_client,  # pyright: ignore[reportArgumentType,reportCallIssue]
            system_prompt="Test",
            progress_callback=progress_callback,
        )

        # Should be called for each section
        self.assertEqual(len(progress_calls), 3)
        self.assertEqual(progress_calls[0], (1, 3))
        self.assertEqual(progress_calls[1], (2, 3))
        self.assertEqual(progress_calls[2], (3, 3))

    def test_rewrite_handles_llm_error_gracefully(self):
        """Test that LLM errors preserve original content."""
        # First section succeeds
        self.mock_client.add_response(r".*Content 1.*", "Rewritten 1\n")
        # Second section has no matching response, will use default
        # Third section succeeds
        self.mock_client.add_response(r".*Content 3.*", "Rewritten 3\n")

        results = rewrite_content(
            self.sections,
            client=self.mock_client,  # pyright: ignore[reportArgumentType,reportCallIssue]
            system_prompt="Test",
        )

        # All should complete (errors are caught and original preserved)
        self.assertEqual(len(results), 3)
        self.assertIn("Rewritten 1", results[0])
        # Second uses default mock response since no match
        self.assertIn("Mock LLM response", results[1])
        self.assertIn("Rewritten 3", results[2])


if __name__ == "__main__":
    unittest.main()
