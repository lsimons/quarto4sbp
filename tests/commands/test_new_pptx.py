"""Unit tests for new-pptx command."""

import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from quarto4sbp.commands.new_pptx import cmd_new_pptx


class TestCmdNewPptx(unittest.TestCase):
    """Tests for cmd_new_pptx function."""

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

    def test_new_pptx_no_args(self) -> None:
        """Test new-pptx command with no arguments."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new_pptx([])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: Directory name required", stderr_output)
        self.assertIn("Usage: q4s new-pptx <directory>", stderr_output)

    def test_new_pptx_invalid_directory_name(self) -> None:
        """Test new-pptx command with invalid directory name."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new_pptx(["-invalid"])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: Invalid directory name", stderr_output)

    def test_new_pptx_creates_directory_and_files(self) -> None:
        """Test new-pptx command creates directory, qmd file, and symlink."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new_pptx(["test-presentation"])
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
        self.assertIn('FILE_NAME="test-presentation"', render_content)
        self.assertIn("${FILE_NAME}.qmd", render_content)
        self.assertIn("#!/bin/sh", render_content)
        self.assertIn("q4s pdf", render_content)
        self.assertIn("Successfully exported to PDF", render_content)

    def test_new_pptx_directory_already_exists(self) -> None:
        """Test new-pptx command when directory already exists but qmd doesn't."""
        # Create directory first
        Path("existing-dir").mkdir()

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new_pptx(["existing-dir"])
        stdout_output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("Created: existing-dir/existing-dir.qmd", stdout_output)

        # Verify qmd file exists
        qmd_file = Path("existing-dir/existing-dir.qmd")
        self.assertTrue(qmd_file.exists())

    def test_new_pptx_qmd_file_already_exists(self) -> None:
        """Test new-pptx command when qmd file already exists."""
        # Create directory and qmd file
        target_dir = Path("existing-presentation")
        target_dir.mkdir()
        qmd_file = target_dir / "existing-presentation.qmd"
        qmd_file.write_text("existing content")

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new_pptx(["existing-presentation"])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: File already exists", stderr_output)

        # Verify original content is unchanged
        self.assertEqual(qmd_file.read_text(), "existing content")

    def test_new_pptx_with_subdirectory_path(self) -> None:
        """Test new-pptx command with subdirectory in name."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new_pptx(["subdir/my-presentation"])
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


class TestCmdNewPptxErrorCases(unittest.TestCase):
    """Tests for cmd_new_pptx error handling."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
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

    def test_missing_template_qmd(self) -> None:
        """Test error when template qmd file is missing."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Temporarily hide the template by renaming it
        project_root = Path(__file__).parent.parent.parent
        template_qmd = project_root / "templates" / "simple-presentation.qmd"
        backup_path = project_root / "templates" / "simple-presentation.qmd.backup"

        if template_qmd.exists():
            template_qmd.rename(backup_path)
            try:
                result = cmd_new_pptx(["test-pres"])
                stderr_output = sys.stderr.getvalue()

                self.assertEqual(result, 1)
                self.assertIn("Error: Template not found", stderr_output)
            finally:
                backup_path.rename(template_qmd)

    def test_missing_template_pptx(self) -> None:
        """Test error when PowerPoint template is missing."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Temporarily hide the PowerPoint template
        project_root = Path(__file__).parent.parent.parent
        template_pptx = project_root / "templates" / "simple-presentation.pptx"
        backup_path = project_root / "templates" / "simple-presentation.pptx.backup"

        if template_pptx.exists():
            template_pptx.rename(backup_path)
            try:
                result = cmd_new_pptx(["test-pres"])
                stderr_output = sys.stderr.getvalue()

                self.assertEqual(result, 1)
                self.assertIn("Error: PowerPoint template not found", stderr_output)
            finally:
                backup_path.rename(template_pptx)

    def test_missing_render_template(self) -> None:
        """Test error when render script template is missing."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Temporarily hide the render template
        project_root = Path(__file__).parent.parent.parent
        template_render = project_root / "templates" / "render.sh.template"
        backup_path = project_root / "templates" / "render.sh.template.backup"

        if template_render.exists():
            template_render.rename(backup_path)
            try:
                result = cmd_new_pptx(["test-pres"])
                stderr_output = sys.stderr.getvalue()

                self.assertEqual(result, 1)
                self.assertIn("Error: Render script template not found", stderr_output)
            finally:
                backup_path.rename(template_render)

    def test_directory_creation_error(self) -> None:
        """Test error when directory creation fails."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Create a file with the same name to cause mkdir to fail
        Path("blocked").write_text("blocking file")

        result = cmd_new_pptx(["blocked/subdir"])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: Could not create directory", stderr_output)

    def test_qmd_file_write_error(self) -> None:
        """Test error when qmd file cannot be written."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Create directory but make it read-only
        target_dir = Path("readonly-dir")
        target_dir.mkdir()
        os.chmod(target_dir, 0o555)

        try:
            result = cmd_new_pptx(["readonly-dir"])
            stderr_output = sys.stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Error: Could not create file", stderr_output)
        finally:
            # Restore permissions for cleanup
            os.chmod(target_dir, 0o755)

    def test_render_script_write_error(self) -> None:
        """Test error when render script cannot be written."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        with patch("pathlib.Path.write_text") as mock_write:
            # Make the second write_text call (render script) fail
            call_count = [0]

            def write_side_effect(content: str) -> None:
                call_count[0] += 1
                if call_count[0] == 2:  # Second call is for render script
                    raise OSError("Permission denied")

            mock_write.side_effect = write_side_effect

            result = cmd_new_pptx(["test-pres"])
            stderr_output = sys.stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Error: Could not create render script", stderr_output)

    def test_symlink_creation_warning(self) -> None:
        """Test warning when symlink creation fails (non-fatal)."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        with patch("pathlib.Path.symlink_to") as mock_symlink:
            mock_symlink.side_effect = OSError("Symlinks not supported")

            result = cmd_new_pptx(["test-pres"])
            stderr_output = sys.stderr.getvalue()
            stdout_output = sys.stdout.getvalue()

            # Should succeed despite symlink failure
            self.assertEqual(result, 0)
            self.assertIn("Warning: Could not create symlink", stderr_output)
            self.assertIn("Created: test-pres/test-pres.qmd", stdout_output)


if __name__ == "__main__":
    unittest.main()
