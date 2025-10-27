"""Tests for pytest fixtures and LLM assertion helpers."""

import pytest

from tests.helpers.llm import (
    assert_llm_called_with,
    assert_llm_not_called_with,
    assert_llm_call_count,
    get_llm_call_prompts,
)

# pyright: reportUnknownParameterType=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false
# pyright: reportMissingParameterType=false


class TestPytestFixtures:
    """Test pytest fixtures for LLM testing."""

    def test_mock_llm_fixture(self, mock_llm):
        """Test basic mock_llm fixture."""
        assert mock_llm is not None
        assert mock_llm.get_call_count() == 0

        # Should have pre-configured responses
        result = mock_llm.prompt("hello")
        assert "test LLM" in result

    def test_mock_llm_common_fixture(self, mock_llm_common):
        """Test mock_llm_common fixture with loaded fixtures."""
        assert mock_llm_common is not None

        # Should have common fixtures loaded
        result = mock_llm_common.prompt("hello")
        assert "test LLM" in result

    def test_mock_llm_tov_fixture(self, mock_llm_tov):
        """Test mock_llm_tov fixture for tone-of-voice testing."""
        assert mock_llm_tov is not None

        # Should respond to formal prompts
        result = mock_llm_tov.prompt("Make this formal")
        assert len(result) > 0

        # Should respond to casual prompts
        result = mock_llm_tov.prompt("Make this casual")
        assert len(result) > 0

    def test_mock_llm_viz_fixture(self, mock_llm_viz):
        """Test mock_llm_viz fixture for visualization testing."""
        assert mock_llm_viz is not None

        # Should respond to analysis prompts
        result = mock_llm_viz.prompt("Analyze this slide")
        assert len(result) > 0

        # Should respond to image generation prompts
        result = mock_llm_viz.prompt("Generate image prompt")
        assert len(result) > 0

    def test_mock_llm_empty_fixture(self, mock_llm_empty):
        """Test mock_llm_empty fixture for custom configuration."""
        assert mock_llm_empty is not None
        assert len(mock_llm_empty.responses) == 0

        # Can add custom responses
        mock_llm_empty.add_response("custom", "Custom response")
        result = mock_llm_empty.prompt("custom")
        assert result == "Custom response"

    def test_mock_llm_with_history_fixture(self, mock_llm_with_history):
        """Test mock_llm_with_history fixture."""
        assert mock_llm_with_history is not None
        assert mock_llm_with_history.get_call_count() == 3

        # Should have history populated
        prompts = get_llm_call_prompts(mock_llm_with_history)
        assert "First test prompt" in prompts
        assert "Second test prompt" in prompts
        assert "Third test prompt" in prompts


class TestAssertionHelpers:
    """Test LLM assertion helper functions."""

    def test_assert_llm_called_with_success(self, mock_llm):
        """Test assert_llm_called_with when pattern matches."""
        mock_llm.prompt("Hello world")
        # Should not raise
        assert_llm_called_with(mock_llm, "Hello")
        assert_llm_called_with(mock_llm, r"world")

    def test_assert_llm_called_with_failure(self, mock_llm):
        """Test assert_llm_called_with when pattern doesn't match."""
        mock_llm.prompt("Hello world")
        with pytest.raises(AssertionError) as exc_info:
            assert_llm_called_with(mock_llm, "goodbye")
        assert "Expected LLM to be called with pattern" in str(exc_info.value)
        assert "goodbye" in str(exc_info.value)

    def test_assert_llm_not_called_with_success(self, mock_llm):
        """Test assert_llm_not_called_with when pattern doesn't match."""
        mock_llm.prompt("Hello world")
        # Should not raise
        assert_llm_not_called_with(mock_llm, "goodbye")
        assert_llm_not_called_with(mock_llm, "test")

    def test_assert_llm_not_called_with_failure(self, mock_llm):
        """Test assert_llm_not_called_with when pattern matches."""
        mock_llm.prompt("Hello world")
        with pytest.raises(AssertionError) as exc_info:
            assert_llm_not_called_with(mock_llm, "Hello")
        assert "Expected LLM NOT to be called with pattern" in str(exc_info.value)
        assert "Hello" in str(exc_info.value)

    def test_assert_llm_call_count_success(self, mock_llm):
        """Test assert_llm_call_count when count matches."""
        assert_llm_call_count(mock_llm, 0)
        mock_llm.prompt("Test 1")
        assert_llm_call_count(mock_llm, 1)
        mock_llm.prompt("Test 2")
        assert_llm_call_count(mock_llm, 2)

    def test_assert_llm_call_count_failure(self, mock_llm):
        """Test assert_llm_call_count when count doesn't match."""
        mock_llm.prompt("Test")
        with pytest.raises(AssertionError) as exc_info:
            assert_llm_call_count(mock_llm, 5)
        assert "Expected 5 LLM calls, but got 1" in str(exc_info.value)

    def test_get_llm_call_prompts(self, mock_llm):
        """Test get_llm_call_prompts helper."""
        assert get_llm_call_prompts(mock_llm) == []

        mock_llm.prompt("First")
        mock_llm.prompt("Second")
        mock_llm.prompt("Third")

        prompts = get_llm_call_prompts(mock_llm)
        assert len(prompts) == 3
        assert prompts[0] == "First"
        assert prompts[1] == "Second"
        assert prompts[2] == "Third"

    def test_get_llm_call_prompts_empty(self, mock_llm_empty):
        """Test get_llm_call_prompts with no calls."""
        prompts = get_llm_call_prompts(mock_llm_empty)
        assert prompts == []


class TestFixtureIntegration:
    """Test integration between fixtures and helpers."""

    def test_tov_fixture_with_assertions(self, mock_llm_tov):
        """Test tone-of-voice fixture with assertion helpers."""
        mock_llm_tov.prompt("Rewrite in formal tone")
        mock_llm_tov.prompt("Rewrite in casual tone")

        assert_llm_call_count(mock_llm_tov, 2)
        assert_llm_called_with(mock_llm_tov, r"formal")
        assert_llm_called_with(mock_llm_tov, r"casual")
        assert_llm_not_called_with(mock_llm_tov, r"technical")

    def test_viz_fixture_with_assertions(self, mock_llm_viz):
        """Test visualization fixture with assertion helpers."""
        mock_llm_viz.prompt("Analyze this slide content")
        mock_llm_viz.prompt("Generate image prompt for dashboard")

        assert_llm_call_count(mock_llm_viz, 2)
        assert_llm_called_with(mock_llm_viz, r"Analyze")
        assert_llm_called_with(mock_llm_viz, r"image")

    def test_empty_fixture_custom_config(self, mock_llm_empty):
        """Test empty fixture with custom configuration."""
        mock_llm_empty.add_response("pattern1", "Response 1")
        mock_llm_empty.add_response("pattern2", "Response 2")

        mock_llm_empty.prompt("pattern1 test")
        mock_llm_empty.prompt("pattern2 test")

        assert_llm_call_count(mock_llm_empty, 2)
        prompts = get_llm_call_prompts(mock_llm_empty)
        assert "pattern1 test" in prompts
        assert "pattern2 test" in prompts

    def test_multiple_fixtures_isolation(self, mock_llm, mock_llm_empty):
        """Test that fixtures are isolated from each other."""
        mock_llm.prompt("test in mock_llm")
        mock_llm_empty.prompt("test in mock_llm_empty")

        # Each fixture should have its own call history
        assert_llm_call_count(mock_llm, 1)
        assert_llm_call_count(mock_llm_empty, 1)

        prompts1 = get_llm_call_prompts(mock_llm)
        prompts2 = get_llm_call_prompts(mock_llm_empty)

        assert prompts1 == ["test in mock_llm"]
        assert prompts2 == ["test in mock_llm_empty"]
