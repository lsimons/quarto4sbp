"""Tests for tov command."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from quarto4sbp.commands.tov import cmd_tov
from tests.mocks.llm_client import MockLLMClient


class TestCmdTov(unittest.TestCase):
    """Test tov command functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test.qmd"
        self.test_file.write_text("""---
title: "Test Presentation"
format:
  pptx:
    reference-doc: simple-presentation.pptx
---

# Introduction

This is the original content that needs rewriting.

# Section Two

More content here.
""")

    def tearDown(self):
        """Clean up test files."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_no_args_shows_usage(self):
        """Test that no arguments shows usage message."""
        result = cmd_tov([])
        self.assertEqual(result, 1)

    def test_nonexistent_file_returns_error(self):
        """Test that nonexistent file returns error."""
        result = cmd_tov([str(self.test_dir / "nonexistent.qmd")])
        self.assertEqual(result, 1)

    def test_nonexistent_directory_returns_error(self):
        """Test that nonexistent directory returns error."""
        result = cmd_tov([str(self.test_dir / "nonexistent")])
        self.assertEqual(result, 1)

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_process_single_file(self, mock_llm_class: MagicMock) -> None:
        """Test processing a single file."""
        # Set up mock
        mock_client = MockLLMClient()
        mock_client.add_response(r".*", "# Rewritten Content\n\nRewritten text.\n")
        mock_llm_class.return_value = mock_client

        result = cmd_tov([str(self.test_file)])

        self.assertEqual(result, 0)
        # Check backup was created
        backup_path = Path(str(self.test_file) + ".bak")
        self.assertTrue(backup_path.exists())

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_process_file_dry_run(self, mock_llm_class: MagicMock) -> None:
        """Test dry-run mode doesn't modify file."""
        # Set up mock
        mock_client = MockLLMClient()
        mock_client.add_response(r".*", "# Rewritten\n\nNew text.\n")
        mock_llm_class.return_value = mock_client

        original_content = self.test_file.read_text()
        result = cmd_tov([str(self.test_file), "--dry-run"])

        self.assertEqual(result, 0)
        # File should be unchanged
        self.assertEqual(self.test_file.read_text(), original_content)
        # No backup should be created
        backup_path = Path(str(self.test_file) + ".bak")
        self.assertFalse(backup_path.exists())

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_process_file_no_backup(self, mock_llm_class: MagicMock) -> None:
        """Test no-backup flag skips backup creation."""
        # Set up mock
        mock_client = MockLLMClient()
        mock_client.add_response(r".*", "# Rewritten\n\nNew text.\n")
        mock_llm_class.return_value = mock_client

        result = cmd_tov([str(self.test_file), "--no-backup"])

        self.assertEqual(result, 0)
        # No backup should be created
        backup_path = Path(str(self.test_file) + ".bak")
        self.assertFalse(backup_path.exists())

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_process_directory(self, mock_llm_class: MagicMock) -> None:
        """Test processing all files in a directory."""
        # Create additional files
        file2 = self.test_dir / "file2.qmd"
        file2.write_text("# File 2\n\nContent.\n")

        # Set up mock
        mock_client = MockLLMClient()
        mock_client.add_response(r".*", "Rewritten\n")
        mock_llm_class.return_value = mock_client

        result = cmd_tov([str(self.test_dir)])

        self.assertEqual(result, 0)
        # Both files should have backups
        self.assertTrue(
            (self.test_file.parent / (self.test_file.name + ".bak")).exists()
        )
        self.assertTrue((file2.parent / (file2.name + ".bak")).exists())

    def test_directory_with_no_qmd_files(self):
        """Test directory with no .qmd files returns error."""
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir()

        result = cmd_tov([str(empty_dir)])

        self.assertEqual(result, 1)

    def test_non_qmd_file_shows_warning(self):
        """Test that non-.qmd file shows warning but processes."""
        txt_file = self.test_dir / "test.txt"
        txt_file.write_text("# Not a QMD\n\nContent.\n")

        with patch("quarto4sbp.commands.tov.LLMClient") as mock_llm_class:
            mock_client = MockLLMClient()
            mock_client.add_response(r".*", "Rewritten\n")
            mock_llm_class.return_value = mock_client

            result = cmd_tov([str(txt_file)])

            # Should still succeed but with warning
            self.assertEqual(result, 0)

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_llm_config_error_returns_failure(self, mock_llm_class: MagicMock) -> None:
        """Test that LLM configuration error returns failure."""
        # Make LLMClient raise ValueError on init
        mock_llm_class.side_effect = ValueError("API key not configured")

        result = cmd_tov([str(self.test_file)])

        self.assertEqual(result, 1)

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_file_with_only_yaml(self, mock_llm_class: MagicMock) -> None:
        """Test file with only YAML frontmatter."""
        yaml_only = self.test_dir / "yaml-only.qmd"
        yaml_only.write_text("""---
title: "Test"
---
""")

        mock_client = MockLLMClient()
        mock_llm_class.return_value = mock_client

        result = cmd_tov([str(yaml_only)])

        # Should succeed but note no content to rewrite
        self.assertEqual(result, 0)

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_combined_flags(self, mock_llm_class: MagicMock) -> None:
        """Test using multiple flags together."""
        mock_client = MockLLMClient()
        mock_client.add_response(r".*", "Rewritten\n")
        mock_llm_class.return_value = mock_client

        original_content = self.test_file.read_text()
        result = cmd_tov([str(self.test_file), "--dry-run", "--no-backup"])

        self.assertEqual(result, 0)
        # File unchanged (dry-run)
        self.assertEqual(self.test_file.read_text(), original_content)
        # No backup (dry-run + no-backup)
        backup_path = Path(str(self.test_file) + ".bak")
        self.assertFalse(backup_path.exists())


if __name__ == "__main__":
    unittest.main()
