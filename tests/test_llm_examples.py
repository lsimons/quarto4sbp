"""Example tests demonstrating mock LLM usage patterns.

This module contains example tests showing how to use the LLM testing
infrastructure for different use cases. These examples can be used as
templates for writing your own LLM-based tests.

These tests are skipped by default. Set RUN_EXAMPLE_TESTS=1 to run them.
"""

# pyright: reportUnknownParameterType=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false
# pyright: reportMissingParameterType=false

import json
import os

import pytest

from tests.helpers.llm import (
    assert_llm_call_count,
    assert_llm_called_with,
    assert_llm_not_called_with,
    get_llm_call_prompts,
    load_fixture_response,
)


@pytest.mark.skipif(
    not os.environ.get("RUN_EXAMPLE_TESTS"),
    reason="Example tests skipped (set RUN_EXAMPLE_TESTS=1 to run)",
)
class TestBasicLLMUsage:
    """Examples of basic mock LLM usage."""

    def test_simple_prompt_response(self, mock_llm):
        """Example: Test a simple prompt-response interaction."""
        # When
        response = mock_llm.prompt("hello")

        # Then
        assert "test LLM" in response
        assert_llm_call_count(mock_llm, 1)
        assert_llm_called_with(mock_llm, "hello")

    def test_custom_response_mapping(self, mock_llm_empty):
        """Example: Configure custom responses for specific prompts."""
        # Given: Configure mock with custom responses
        mock_llm_empty.add_response("analyze this code", "The code looks good!")
        mock_llm_empty.add_response(r"generate.*test", "Here are some test cases...")

        # When
        result1 = mock_llm_empty.prompt("analyze this code")
        result2 = mock_llm_empty.prompt("generate unit tests")

        # Then
        assert result1 == "The code looks good!"
        assert "test cases" in result2
        assert_llm_call_count(mock_llm_empty, 2)

    def test_regex_pattern_matching(self, mock_llm_empty):
        """Example: Use regex patterns for flexible matching."""
        # Given: Configure with regex pattern
        mock_llm_empty.add_response(
            r"(write|create|make).*function", "def example(): pass"
        )

        # When: Different phrasings that match the pattern
        result1 = mock_llm_empty.prompt("write a function to sort")
        result2 = mock_llm_empty.prompt("create a function for parsing")
        result3 = mock_llm_empty.prompt("make a function that validates")

        # Then: All should get the same response
        assert "def example()" in result1
        assert "def example()" in result2
        assert "def example()" in result3


@pytest.mark.skipif(
    not os.environ.get("RUN_EXAMPLE_TESTS"),
    reason="Example tests skipped (set RUN_EXAMPLE_TESTS=1 to run)",
)
class TestToneOfVoiceRewriting:
    """Examples of testing tone-of-voice features."""

    def test_formal_tone_conversion(self, mock_llm_tov):
        """Example: Test converting text to formal tone."""
        # Given: Input text in casual tone
        casual_text = "Hey, check out this cool feature we built!"

        # When: Request formal rewrite
        result = mock_llm_tov.prompt(
            f"Rewrite in formal professional tone: {casual_text}"
        )

        # Then: Should receive formal version from fixture
        assert len(result) > 0
        assert_llm_called_with(mock_llm_tov, r"formal")
        assert_llm_call_count(mock_llm_tov, 1)

    def test_casual_tone_conversion(self, mock_llm_tov):
        """Example: Test converting text to casual tone."""
        # Given: Input text in formal tone
        formal_text = "We are pleased to announce the implementation of this feature."

        # When: Request casual rewrite
        result = mock_llm_tov.prompt(f"Rewrite in casual friendly tone: {formal_text}")

        # Then: Should receive casual version from fixture
        assert len(result) > 0
        assert_llm_called_with(mock_llm_tov, r"casual")

    def test_multiple_tone_conversions(self, mock_llm_tov):
        """Example: Test multiple tone conversions in sequence."""
        # When: Convert multiple pieces of text
        mock_llm_tov.prompt("Make this formal: thanks!")
        mock_llm_tov.prompt("Make this casual: We appreciate your feedback.")
        mock_llm_tov.prompt("Make this professional: cool stuff")

        # Then: Verify all calls were made
        assert_llm_call_count(mock_llm_tov, 3)
        prompts = get_llm_call_prompts(mock_llm_tov)
        assert len(prompts) == 3
        assert "formal" in prompts[0].lower()
        assert "casual" in prompts[1].lower()


@pytest.mark.skipif(
    not os.environ.get("RUN_EXAMPLE_TESTS"),
    reason="Example tests skipped (set RUN_EXAMPLE_TESTS=1 to run)",
)
class TestVisualizationAndImageGeneration:
    """Examples of testing visualization/image features."""

    def test_slide_analysis(self, mock_llm_viz):
        """Example: Test analyzing slide content."""
        # Given: Slide content to analyze
        slide_content = """
        # Key Benefits
        - Improved efficiency
        - Reduced costs
        - Better satisfaction
        """

        # When: Request analysis
        result = mock_llm_viz.prompt(f"Analyze this slide:\n{slide_content}")

        # Then: Should receive analysis from fixture
        assert len(result) > 0
        assert_llm_called_with(mock_llm_viz, r"analyze")

    def test_image_prompt_generation(self, mock_llm_viz):
        """Example: Test generating image prompts."""
        # Given: Context for image
        context = "dashboard showing efficiency metrics"

        # When: Request image generation prompt
        result = mock_llm_viz.prompt(f"Generate image prompt for: {context}")

        # Then: Should receive prompt from fixture
        assert len(result) > 0
        assert_llm_called_with(mock_llm_viz, r"generate.*prompt")

    def test_multiple_visualizations(self, mock_llm_viz):
        """Example: Test generating multiple visualizations."""
        # When: Request multiple analyses and prompts
        mock_llm_viz.prompt("Analyze slide 1")
        mock_llm_viz.prompt("Generate image for slide 1")
        mock_llm_viz.prompt("Analyze slide 2")
        mock_llm_viz.prompt("Generate image for slide 2")

        # Then: Verify all operations
        assert_llm_call_count(mock_llm_viz, 4)
        assert len(get_llm_call_prompts(mock_llm_viz)) == 4


@pytest.mark.skipif(
    not os.environ.get("RUN_EXAMPLE_TESTS"),
    reason="Example tests skipped (set RUN_EXAMPLE_TESTS=1 to run)",
)
class TestCallHistoryAndAssertions:
    """Examples of using call history and assertion helpers."""

    def test_verify_specific_prompts(self, mock_llm):
        """Example: Verify specific prompts were used."""
        # When: Make various calls
        mock_llm.prompt("analyze this code")
        mock_llm.prompt("fix the bug")
        mock_llm.prompt("optimize performance")

        # Then: Verify specific patterns
        assert_llm_called_with(mock_llm, r"analyze")
        assert_llm_called_with(mock_llm, r"bug")
        assert_llm_called_with(mock_llm, r"optimize")
        assert_llm_not_called_with(mock_llm, r"delete")

    def test_verify_call_order(self, mock_llm):
        """Example: Verify calls were made in expected order."""
        # When: Make calls in specific order
        mock_llm.prompt("step 1: analyze")
        mock_llm.prompt("step 2: implement")
        mock_llm.prompt("step 3: test")

        # Then: Verify order
        prompts = get_llm_call_prompts(mock_llm)
        assert "step 1" in prompts[0]
        assert "step 2" in prompts[1]
        assert "step 3" in prompts[2]

    def test_verify_call_count(self, mock_llm):
        """Example: Verify exact number of calls."""
        # When: Make specific number of calls
        for i in range(5):
            mock_llm.prompt(f"iteration {i}")

        # Then: Verify count
        assert_llm_call_count(mock_llm, 5)

    def test_verify_no_unwanted_calls(self, mock_llm):
        """Example: Verify certain patterns were NOT called."""
        # When: Make safe operations
        mock_llm.prompt("read data")
        mock_llm.prompt("analyze data")

        # Then: Verify no dangerous operations
        assert_llm_not_called_with(mock_llm, r"delete")
        assert_llm_not_called_with(mock_llm, r"drop.*table")
        assert_llm_not_called_with(mock_llm, r"rm -rf")


@pytest.mark.skipif(
    not os.environ.get("RUN_EXAMPLE_TESTS"),
    reason="Example tests skipped (set RUN_EXAMPLE_TESTS=1 to run)",
)
class TestFixtureIntegration:
    """Examples of using fixtures with mock LLM."""

    def test_load_fixture_into_mock(self, mock_llm_empty):
        """Example: Load fixture response into mock."""
        # Given: Load fixture response
        hello_response = load_fixture_response("common", "hello")
        mock_llm_empty.add_response("greet", hello_response)

        # When: Trigger the response
        result = mock_llm_empty.prompt("greet me")

        # Then: Should get fixture content
        assert "test LLM" in result

    def test_structured_json_response(self, mock_llm_empty):
        """Example: Use JSON fixture for structured responses."""
        # Given: Load JSON fixture
        analysis_json = load_fixture_response("viz", "analyze-slide")
        mock_llm_empty.add_response(r"analyze", analysis_json)

        # When: Request analysis
        result = mock_llm_empty.prompt("analyze this slide")

        # Then: Should be parseable JSON
        data = json.loads(result)
        assert "slide_type" in data
        assert data["slide_type"] == "bullet_list"

    def test_multiple_category_fixtures(self, mock_llm_empty):
        """Example: Use fixtures from multiple categories."""
        # Given: Load fixtures from different categories
        hello = load_fixture_response("common", "hello")
        formal = load_fixture_response("tov", "rewrite-formal")

        mock_llm_empty.add_response(r"hello", hello)
        mock_llm_empty.add_response(r"formal", formal)

        # When: Use both
        result1 = mock_llm_empty.prompt("say hello")
        result2 = mock_llm_empty.prompt("make it formal")

        # Then: Both should work
        assert "test LLM" in result1
        assert "Executive Summary" in result2


@pytest.mark.skipif(
    not os.environ.get("RUN_EXAMPLE_TESTS"),
    reason="Example tests skipped (set RUN_EXAMPLE_TESTS=1 to run)",
)
class TestAdvancedPatterns:
    """Examples of advanced testing patterns."""

    def test_conditional_responses(self, mock_llm_empty):
        """Example: Different responses based on prompt content."""
        # Given: Configure responses for different scenarios
        mock_llm_empty.add_response(r"error|bug|issue", "I found the problem!")
        mock_llm_empty.add_response(
            r"improve|enhance|optimize", "Here's how to improve it"
        )
        mock_llm_empty.add_response(r"explain|describe", "Let me explain...")

        # When: Ask different types of questions
        error_response = mock_llm_empty.prompt("What's the error here?")
        improve_response = mock_llm_empty.prompt("How can I improve this?")
        explain_response = mock_llm_empty.prompt("Please explain this code")

        # Then: Each gets appropriate response
        assert "problem" in error_response
        assert "improve" in improve_response
        assert "explain" in explain_response

    def test_stateful_interaction(self, mock_llm_with_history):
        """Example: Test with pre-existing call history."""
        # Given: Mock already has history
        assert mock_llm_with_history.get_call_count() == 3

        # When: Add more calls
        mock_llm_with_history.prompt("Fourth call")
        mock_llm_with_history.prompt("Fifth call")

        # Then: Total history includes both old and new
        assert_llm_call_count(mock_llm_with_history, 5)
        prompts = get_llm_call_prompts(mock_llm_with_history)
        assert "First test prompt" in prompts
        assert "Fourth call" in prompts

    def test_clear_and_restart(self, mock_llm_with_history):
        """Example: Clear history and start fresh."""
        # Given: Mock has existing history
        assert mock_llm_with_history.get_call_count() > 0

        # When: Clear and restart
        mock_llm_with_history.clear_history()
        mock_llm_with_history.prompt("Fresh start")

        # Then: Only new call in history
        assert_llm_call_count(mock_llm_with_history, 1)
        prompts = get_llm_call_prompts(mock_llm_with_history)
        assert prompts == ["Fresh start"]
