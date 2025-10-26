"""Unit tests for new command."""

import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from quarto4sbp.commands.new import cmd_new


class TestCmdNew(unittest.TestCase):
    """Tests for cmd_new function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        # Change to temp directory for tests
        import os

        os.chdir(self.temp_dir)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        import os
        import shutil

        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_new_no_args(self) -> None:
        """Test new command with no arguments."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new([])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: Directory name required", stderr_output)
        self.assertIn("Usage: q4s new <directory>", stderr_output)

    def test_new_invalid_directory_name(self) -> None:
        """Test new command with invalid directory name."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["-invalid"])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: Invalid directory name", stderr_output)

    def test_new_creates_directory_and_files(self) -> None:
        """Test new command creates directory, qmd file, and symlink."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["test-presentation"])
        stdout_output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("Created: test-presentation/test-presentation.qmd", stdout_output)
        self.assertIn("Hint: Run 'cd test-presentation && ./render.sh'", stdout_output)

        # Verify directory exists
        target_dir = Path("test-presentation")
        self.assertTrue(target_dir.exists())
        self.assertTrue(target_dir.is_dir())

        # Verify qmd file exists
        qmd_file = target_dir / "test-presentation.qmd"
        self.assertTrue(qmd_file.exists())
        self.assertTrue(qmd_file.is_file())

        # Verify qmd content
        content = qmd_file.read_text()
        self.assertIn("title:", content)
        self.assertIn("format:", content)
        self.assertIn("pptx:", content)
        self.assertIn("simple-presentation.pptx", content)

        # Verify symlink exists (may not work on all platforms)
        symlink = target_dir / "simple-presentation.pptx"
        # Don't fail test if symlink creation is not supported
        if symlink.exists():
            self.assertTrue(symlink.is_symlink() or symlink.is_file())

        # Verify render.sh script exists
        render_script = target_dir / "render.sh"
        self.assertTrue(render_script.exists())
        self.assertTrue(render_script.is_file())

        # Verify render.sh is executable
        import stat

        file_stat = render_script.stat()
        self.assertTrue(file_stat.st_mode & stat.S_IXUSR)

        # Verify render.sh content
        render_content = render_script.read_text()
        self.assertIn("quarto render", render_content)
        self.assertIn('PRESENTATION_NAME="test-presentation"', render_content)
        self.assertIn("${PRESENTATION_NAME}.qmd", render_content)
        self.assertIn("#!/bin/sh", render_content)

    def test_new_directory_already_exists(self) -> None:
        """Test new command when directory already exists but qmd doesn't."""
        # Create directory first
        Path("existing-dir").mkdir()

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["existing-dir"])
        stdout_output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("Created: existing-dir/existing-dir.qmd", stdout_output)

        # Verify qmd file exists
        qmd_file = Path("existing-dir/existing-dir.qmd")
        self.assertTrue(qmd_file.exists())

    def test_new_qmd_file_already_exists(self) -> None:
        """Test new command when qmd file already exists."""
        # Create directory and qmd file
        target_dir = Path("existing-presentation")
        target_dir.mkdir()
        qmd_file = target_dir / "existing-presentation.qmd"
        qmd_file.write_text("existing content")

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["existing-presentation"])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: File already exists", stderr_output)

        # Verify original content is unchanged
        self.assertEqual(qmd_file.read_text(), "existing content")

    def test_new_with_subdirectory_path(self) -> None:
        """Test new command with subdirectory in name."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["subdir/my-presentation"])
        stdout_output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn(
            "Created: subdir/my-presentation/my-presentation.qmd", stdout_output
        )

        # Verify nested directory structure
        target_dir = Path("subdir/my-presentation")
        self.assertTrue(target_dir.exists())
        self.assertTrue(target_dir.is_dir())

        qmd_file = target_dir / "my-presentation.qmd"
        self.assertTrue(qmd_file.exists())


if __name__ == "__main__":
    unittest.main()
