"""Tests for prompt management utilities."""

import tempfile
import unittest
from pathlib import Path

from quarto4sbp.llm.prompts import (
    PromptLoader,
    PromptNotFoundError,
    get_loader,
    load_and_format_prompt,
    load_prompt,
)


class TestPromptLoader(unittest.TestCase):
    """Test cases for PromptLoader class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a temporary directory for test prompts
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_dir = Path(self.temp_dir) / "prompts"
        self.prompts_dir.mkdir()

        # Create test prompt directories
        (self.prompts_dir / "test_category").mkdir()
        (self.prompts_dir / "other_category").mkdir()

        # Create test prompts
        (self.prompts_dir / "simple.txt").write_text("Simple prompt text")
        (self.prompts_dir / "test_category" / "prompt1.txt").write_text(
            "Category prompt 1"
        )
        (self.prompts_dir / "test_category" / "prompt2.md").write_text(
            "Category prompt 2 in markdown"
        )
        (self.prompts_dir / "other_category" / "prompt3.txt").write_text(
            "Other category prompt"
        )

        # Create a template prompt with variables
        (self.prompts_dir / "template.txt").write_text(
            "Hello {name}, your value is {value}."
        )

        # Create nested directory structure
        (self.prompts_dir / "nested" / "deep").mkdir(parents=True)
        (self.prompts_dir / "nested" / "deep" / "prompt.txt").write_text(
            "Deeply nested prompt"
        )

        self.loader = PromptLoader(self.prompts_dir)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_load_simple_prompt(self) -> None:
        """Test loading a simple prompt file."""
        prompt = self.loader.load("simple")
        self.assertEqual(prompt, "Simple prompt text")

    def test_load_category_prompt(self) -> None:
        """Test loading a prompt from a category subdirectory."""
        prompt = self.loader.load("test_category/prompt1")
        self.assertEqual(prompt, "Category prompt 1")

    def test_load_markdown_prompt(self) -> None:
        """Test loading a .md file when .txt doesn't exist."""
        prompt = self.loader.load("test_category/prompt2")
        self.assertEqual(prompt, "Category prompt 2 in markdown")

    def test_load_nested_prompt(self) -> None:
        """Test loading a prompt from nested directories."""
        prompt = self.loader.load("nested/deep/prompt")
        self.assertEqual(prompt, "Deeply nested prompt")

    def test_load_nonexistent_prompt(self) -> None:
        """Test that loading a nonexistent prompt raises PromptNotFoundError."""
        with self.assertRaises(PromptNotFoundError) as context:
            self.loader.load("nonexistent")

        self.assertIn("not found", str(context.exception))
        self.assertIn("nonexistent", str(context.exception))

    def test_load_and_format_simple(self) -> None:
        """Test loading and formatting a prompt with variables."""
        formatted = self.loader.load_and_format("template", name="Alice", value="42")
        self.assertEqual(formatted, "Hello Alice, your value is 42.")

    def test_load_and_format_missing_variable(self) -> None:
        """Test that missing template variables raise KeyError."""
        with self.assertRaises(KeyError):
            self.loader.load_and_format("template", name="Alice")

    def test_list_prompts_all(self) -> None:
        """Test listing all prompts."""
        prompts = self.loader.list_prompts()
        self.assertIn("simple", prompts)
        self.assertIn("test_category/prompt1", prompts)
        self.assertIn("test_category/prompt2", prompts)
        self.assertIn("other_category/prompt3", prompts)
        self.assertIn("nested/deep/prompt", prompts)

    def test_list_prompts_by_category(self) -> None:
        """Test listing prompts filtered by category."""
        prompts = self.loader.list_prompts(category="test_category")
        self.assertEqual(len(prompts), 2)
        self.assertIn("test_category/prompt1", prompts)
        self.assertIn("test_category/prompt2", prompts)
        self.assertNotIn("other_category/prompt3", prompts)

    def test_list_prompts_nonexistent_category(self) -> None:
        """Test listing prompts for a nonexistent category returns empty list."""
        prompts = self.loader.list_prompts(category="nonexistent")
        self.assertEqual(prompts, [])

    def test_prompt_caching(self) -> None:
        """Test that prompts are cached after first load."""
        # Load prompt
        prompt1 = self.loader.load("simple")

        # Modify the file
        (self.prompts_dir / "simple.txt").write_text("Modified content")

        # Load again - should get cached version
        prompt2 = self.loader.load("simple")
        self.assertEqual(prompt1, prompt2)
        self.assertEqual(prompt2, "Simple prompt text")

    def test_clear_cache(self) -> None:
        """Test that clearing cache allows loading updated prompts."""
        # Load prompt
        prompt1 = self.loader.load("simple")
        self.assertEqual(prompt1, "Simple prompt text")

        # Modify the file
        (self.prompts_dir / "simple.txt").write_text("Modified content")

        # Clear cache and load again
        self.loader.clear_cache()
        prompt2 = self.loader.load("simple")
        self.assertEqual(prompt2, "Modified content")

    def test_default_prompts_dir(self) -> None:
        """Test that default prompts directory is set correctly."""
        loader = PromptLoader()
        # Should point to package_root/prompts
        expected = Path(__file__).parent.parent.parent / "prompts"
        self.assertEqual(loader.prompts_dir, expected)

    def test_strips_whitespace(self) -> None:
        """Test that loaded prompts have leading/trailing whitespace stripped."""
        (self.prompts_dir / "whitespace.txt").write_text("\n\n  Content  \n\n")
        prompt = self.loader.load("whitespace")
        self.assertEqual(prompt, "Content")


class TestPromptLoaderRealPrompts(unittest.TestCase):
    """Test cases using actual prompts from the prompts/ directory."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.loader = PromptLoader()

    def test_load_tov_system_prompt(self) -> None:
        """Test loading the ToV system prompt."""
        prompt = self.loader.load("tov/system")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("tone of voice", prompt.lower())

    def test_load_tov_rewrite_slide_prompt(self) -> None:
        """Test loading the ToV rewrite-slide prompt template."""
        prompt = self.loader.load("tov/rewrite-slide")
        self.assertIsInstance(prompt, str)
        self.assertIn("{tone_guidelines}", prompt)
        self.assertIn("{slide_content}", prompt)

    def test_load_viz_analyze_slide_prompt(self) -> None:
        """Test loading the viz analyze-slide prompt."""
        prompt = self.loader.load("viz/analyze-slide")
        self.assertIsInstance(prompt, str)
        self.assertIn("{slide_content}", prompt)

    def test_load_viz_generate_image_prompt(self) -> None:
        """Test loading the viz generate-image prompt."""
        prompt = self.loader.load("viz/generate-image")
        self.assertIsInstance(prompt, str)
        self.assertIn("{image_description}", prompt)
        self.assertIn("{slide_content}", prompt)

    def test_load_common_format_json_prompt(self) -> None:
        """Test loading the common format-json prompt."""
        prompt = self.loader.load("common/format-json")
        self.assertIsInstance(prompt, str)
        self.assertIn("JSON", prompt)

    def test_format_tov_rewrite_slide(self) -> None:
        """Test formatting the ToV rewrite-slide prompt with variables."""
        formatted = self.loader.load_and_format(
            "tov/rewrite-slide",
            tone_guidelines="Be concise and direct",
            slide_content="# Test Slide\n- Point 1\n- Point 2",
        )
        self.assertIn("Be concise and direct", formatted)
        self.assertIn("# Test Slide", formatted)
        self.assertNotIn("{tone_guidelines}", formatted)
        self.assertNotIn("{slide_content}", formatted)

    def test_list_tov_prompts(self) -> None:
        """Test listing prompts in the tov category."""
        prompts = self.loader.list_prompts(category="tov")
        self.assertGreater(len(prompts), 0)
        self.assertTrue(
            any("tov/system" in p for p in prompts),
            "tov/system not found in prompts",
        )
        self.assertTrue(
            any("tov/rewrite-slide" in p for p in prompts),
            "tov/rewrite-slide not found in prompts",
        )

    def test_list_viz_prompts(self) -> None:
        """Test listing prompts in the viz category."""
        prompts = self.loader.list_prompts(category="viz")
        self.assertGreater(len(prompts), 0)
        self.assertTrue(
            any("viz/analyze-slide" in p for p in prompts),
            "viz/analyze-slide not found in prompts",
        )
        self.assertTrue(
            any("viz/generate-image" in p for p in prompts),
            "viz/generate-image not found in prompts",
        )

    def test_list_common_prompts(self) -> None:
        """Test listing prompts in the common category."""
        prompts = self.loader.list_prompts(category="common")
        self.assertGreater(len(prompts), 0)
        self.assertTrue(
            any("common/format-json" in p for p in prompts),
            "common/format-json not found in prompts",
        )


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global convenience functions."""

    def test_get_loader_singleton(self) -> None:
        """Test that get_loader returns the same instance."""
        loader1 = get_loader()
        loader2 = get_loader()
        self.assertIs(loader1, loader2)

    def test_load_prompt_convenience(self) -> None:
        """Test the load_prompt convenience function."""
        prompt = load_prompt("tov/system")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_load_and_format_prompt_convenience(self) -> None:
        """Test the load_and_format_prompt convenience function."""
        formatted = load_and_format_prompt(
            "tov/rewrite-slide",
            tone_guidelines="Test guidelines",
            slide_content="Test content",
        )
        self.assertIn("Test guidelines", formatted)
        self.assertIn("Test content", formatted)


if __name__ == "__main__":
    unittest.main()
