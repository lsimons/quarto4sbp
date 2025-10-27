"""Tests for MockLLMClient."""

import unittest

from tests.mocks.llm_client import MockLLMClient


class TestMockLLMClient(unittest.TestCase):
    """Test MockLLMClient functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MockLLMClient()

    def test_init_empty(self):
        """Test initialization with no responses."""
        client = MockLLMClient()
        self.assertEqual(len(client.responses), 0)
        self.assertEqual(len(client.call_history), 0)

    def test_init_with_responses(self):
        """Test initialization with response mappings."""
        responses = {"hello": "Hi there!", "goodbye": "See you!"}
        client = MockLLMClient(responses)
        self.assertEqual(len(client.responses), 2)
        self.assertEqual(client.responses["hello"], "Hi there!")

    def test_prompt_exact_match(self):
        """Test prompt with exact match."""
        self.client.add_response("What is 2+2?", "The answer is 4")
        result = self.client.prompt("What is 2+2?")
        self.assertEqual(result, "The answer is 4")

    def test_prompt_regex_match(self):
        """Test prompt with regex pattern match."""
        self.client.add_response(r"what.*time", "It's testing time!")
        result = self.client.prompt("What is the time?")
        self.assertEqual(result, "It's testing time!")

    def test_prompt_case_insensitive(self):
        """Test that regex matching is case-insensitive."""
        self.client.add_response(r"hello", "Hi!")
        result = self.client.prompt("HELLO world")
        self.assertEqual(result, "Hi!")

    def test_prompt_default_response(self):
        """Test default response for unmatched prompts."""
        result = self.client.prompt("Random question")
        self.assertEqual(result, "Mock LLM response")

    def test_prompt_no_match_no_default(self):
        """Test error when no match and default disabled."""
        self.client.set_default_response("")
        with self.assertRaises(ValueError) as cm:
            self.client.prompt("Unknown prompt")
        self.assertIn("No response configured", str(cm.exception))
        self.assertIn("Unknown prompt", str(cm.exception))

    def test_add_response(self):
        """Test adding responses after initialization."""
        self.client.add_response("test", "response")
        self.assertEqual(self.client.responses["test"], "response")
        result = self.client.prompt("test")
        self.assertEqual(result, "response")

    def test_set_default_response(self):
        """Test setting custom default response."""
        self.client.set_default_response("Custom default")
        result = self.client.prompt("Anything")
        self.assertEqual(result, "Custom default")

    def test_call_history_recorded(self):
        """Test that calls are recorded in history."""
        self.client.prompt("First call")
        self.client.prompt("Second call")
        self.assertEqual(len(self.client.call_history), 2)
        self.assertEqual(self.client.call_history[0]["prompt"], "First call")
        self.assertEqual(self.client.call_history[1]["prompt"], "Second call")

    def test_call_history_includes_kwargs(self):
        """Test that kwargs are recorded in history."""
        self.client.prompt("Test", temperature=0.7, max_tokens=100)
        call = self.client.call_history[0]
        self.assertEqual(call["kwargs"]["temperature"], 0.7)
        self.assertEqual(call["kwargs"]["max_tokens"], 100)

    def test_clear_history(self):
        """Test clearing call history."""
        self.client.prompt("First")
        self.client.prompt("Second")
        self.assertEqual(len(self.client.call_history), 2)
        self.client.clear_history()
        self.assertEqual(len(self.client.call_history), 0)

    def test_get_call_count(self):
        """Test getting call count."""
        self.assertEqual(self.client.get_call_count(), 0)
        self.client.prompt("Test 1")
        self.assertEqual(self.client.get_call_count(), 1)
        self.client.prompt("Test 2")
        self.assertEqual(self.client.get_call_count(), 2)

    def test_get_last_call(self):
        """Test getting last call."""
        self.assertIsNone(self.client.get_last_call())
        self.client.prompt("First")
        self.client.prompt("Second")
        last = self.client.get_last_call()
        self.assertIsNotNone(last)
        assert last is not None  # Type narrowing for pyright
        self.assertEqual(last["prompt"], "Second")

    def test_was_called_with_exact(self):
        """Test checking if called with specific prompt."""
        self.client.prompt("Hello world")
        self.assertTrue(self.client.was_called_with("Hello"))
        self.assertTrue(self.client.was_called_with("world"))
        self.assertFalse(self.client.was_called_with("goodbye"))

    def test_was_called_with_regex(self):
        """Test checking calls with regex pattern."""
        self.client.prompt("The quick brown fox")
        self.assertTrue(self.client.was_called_with(r"quick.*fox"))
        self.assertTrue(self.client.was_called_with(r"^The"))
        self.assertFalse(self.client.was_called_with(r"^quick"))

    def test_get_calls_matching(self):
        """Test getting all calls matching pattern."""
        self.client.prompt("Hello there")
        self.client.prompt("Goodbye")
        self.client.prompt("Hello again")

        matches = self.client.get_calls_matching("Hello")
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["prompt"], "Hello there")
        self.assertEqual(matches[1]["prompt"], "Hello again")

    def test_get_calls_matching_empty(self):
        """Test getting matches when none exist."""
        self.client.prompt("Test")
        matches = self.client.get_calls_matching("nomatch")
        self.assertEqual(len(matches), 0)

    def test_multiple_responses(self):
        """Test client with multiple response patterns."""
        self.client.add_response(r"weather", "It's sunny!")
        self.client.add_response(r"time", "It's 3 PM")
        self.client.add_response(r"hello", "Hi there!")

        self.assertEqual(self.client.prompt("What's the weather?"), "It's sunny!")
        self.assertEqual(self.client.prompt("What time is it?"), "It's 3 PM")
        self.assertEqual(self.client.prompt("hello world"), "Hi there!")

    def test_exact_match_priority(self):
        """Test that exact matches take priority over regex."""
        self.client.add_response("test", "exact match")
        self.client.add_response(r"test.*", "regex match")

        # Exact match should be returned
        result = self.client.prompt("test")
        self.assertEqual(result, "exact match")

    def test_complex_response(self):
        """Test with complex multi-line response."""
        complex_response = """# Title

This is a complex response with:
- Multiple lines
- Formatting
- Special characters: !@#$%

And more content."""

        self.client.add_response("complex", complex_response)
        result = self.client.prompt("complex")
        self.assertEqual(result, complex_response)


class TestMockLLMClientWithFixtures(unittest.TestCase):
    """Test MockLLMClient integration with fixtures."""

    def test_load_fixtures_into_mock(self):
        """Test loading fixture responses into mock client."""
        from tests.helpers.llm import load_fixture_response

        hello_response = load_fixture_response("common", "hello")
        client = MockLLMClient({"hello": hello_response})

        result = client.prompt("hello")
        self.assertIn("test LLM", result)

    def test_mock_with_multiple_fixtures(self):
        """Test mock client with multiple fixture responses."""
        from tests.helpers.llm import load_all_fixtures

        fixtures = load_all_fixtures("common")
        client = MockLLMClient(fixtures)

        result = client.prompt("hello")
        self.assertIn("test LLM", result)


if __name__ == "__main__":
    unittest.main()
