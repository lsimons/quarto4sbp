"""Tests for LLM fixture loading helpers."""

import json
import unittest

from tests.helpers.llm import (
    get_fixtures_dir,
    load_all_fixtures,
    load_fixture_json,
    load_fixture_response,
)


class TestLLMFixtures(unittest.TestCase):
    """Test LLM fixture loading functionality."""

    def test_get_fixtures_dir(self):
        """Test that fixtures directory path is correct."""
        fixtures_dir = get_fixtures_dir()
        self.assertTrue(fixtures_dir.exists())
        self.assertTrue(fixtures_dir.is_dir())
        self.assertEqual(fixtures_dir.name, "llm")

    def test_load_fixture_response_txt(self):
        """Test loading text fixture."""
        content = load_fixture_response("common", "hello")
        self.assertIsInstance(content, str)
        self.assertIn("test LLM", content)

    def test_load_fixture_response_json(self):
        """Test loading JSON fixture as text."""
        content = load_fixture_response("viz", "analyze-slide")
        self.assertIsInstance(content, str)
        # Should be valid JSON
        parsed = json.loads(content)
        self.assertIn("slide_type", parsed)

    def test_load_fixture_json(self):
        """Test loading and parsing JSON fixture."""
        data = load_fixture_json("viz", "analyze-slide")
        self.assertIsInstance(data, dict)
        self.assertEqual(data["slide_type"], "bullet_list")
        self.assertFalse(data["has_images"])
        self.assertIn("image_suggestions", data)

    def test_load_fixture_not_found(self):
        """Test error when fixture doesn't exist."""
        with self.assertRaises(FileNotFoundError) as cm:
            load_fixture_response("common", "nonexistent")
        self.assertIn("Fixture not found", str(cm.exception))
        self.assertIn("common/nonexistent", str(cm.exception))

    def test_load_all_fixtures_common(self):
        """Test loading all fixtures from common category."""
        fixtures = load_all_fixtures("common")
        self.assertIsInstance(fixtures, dict)
        self.assertIn("hello", fixtures)
        self.assertIn("test LLM", fixtures["hello"])

    def test_load_all_fixtures_tov(self):
        """Test loading all fixtures from tov category."""
        fixtures = load_all_fixtures("tov")
        self.assertIsInstance(fixtures, dict)
        self.assertIn("rewrite-formal", fixtures)
        self.assertIn("rewrite-casual", fixtures)
        self.assertIn("formal", fixtures["rewrite-formal"].lower())
        # Check for informal language markers
        self.assertIn("cool", fixtures["rewrite-casual"].lower())

    def test_load_all_fixtures_viz(self):
        """Test loading all fixtures from viz category."""
        fixtures = load_all_fixtures("viz")
        self.assertIsInstance(fixtures, dict)
        self.assertIn("analyze-slide", fixtures)
        self.assertIn("generate-prompt", fixtures)

    def test_load_all_fixtures_empty_category(self):
        """Test loading from non-existent category returns empty dict."""
        fixtures = load_all_fixtures("nonexistent")
        self.assertIsInstance(fixtures, dict)
        self.assertEqual(len(fixtures), 0)

    def test_fixture_content_formal(self):
        """Test formal tone fixture content."""
        content = load_fixture_response("tov", "rewrite-formal")
        self.assertIn("Executive Summary", content)
        self.assertIn("strategic", content.lower())
        # Should be more formal
        self.assertNotIn("👋", content)
        self.assertNotIn("cool", content.lower())

    def test_fixture_content_casual(self):
        """Test casual tone fixture content."""
        content = load_fixture_response("tov", "rewrite-casual")
        self.assertIn("👋", content)
        self.assertIn("cool", content.lower())
        # Should be less formal
        self.assertNotIn("Executive Summary", content)

    def test_fixture_content_image_prompt(self):
        """Test image generation prompt fixture."""
        content = load_fixture_response("viz", "generate-prompt")
        self.assertIn("dashboard", content.lower())
        self.assertIn("professional", content.lower())
        self.assertIn("16:9", content)


if __name__ == "__main__":
    unittest.main()
