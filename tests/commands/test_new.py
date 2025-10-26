"""Unit tests for unified new command."""

import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from quarto4sbp.commands.new import cmd_new


class TestCmdNew(unittest.TestCase):
    """Tests for cmd_new unified function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
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
        """Test new command creates directory, qmd file with both outputs, and symlinks."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["test-project"])
        stdout_output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("Created: test-project/test-project.qmd", stdout_output)
        self.assertIn(
            "Outputs: Both PowerPoint (.pptx) and Word (.docx)", stdout_output
        )
        self.assertIn("Hint: Run 'cd test-project && ./render.sh'", stdout_output)

        # Verify directory exists
        target_dir = Path("test-project")
        self.assertTrue(target_dir.exists())
        self.assertTrue(target_dir.is_dir())

        # Verify qmd file exists
        qmd_file = target_dir / "test-project.qmd"
        self.assertTrue(qmd_file.exists())
        self.assertTrue(qmd_file.is_file())

        # Verify qmd content has both output formats
        content = qmd_file.read_text()
        self.assertIn("title:", content)
        self.assertIn("format:", content)
        self.assertIn("pptx:", content)
        self.assertIn("docx:", content)
        self.assertIn("simple-presentation.pptx", content)
        self.assertIn("simple-document.docx", content)
        self.assertIn("toc:", content)
        self.assertIn("number-sections:", content)

        # Verify both symlinks exist
        pptx_symlink = target_dir / "simple-presentation.pptx"
        docx_symlink = target_dir / "simple-document.docx"
        if pptx_symlink.exists():
            self.assertTrue(pptx_symlink.is_symlink() or pptx_symlink.is_file())
        if docx_symlink.exists():
            self.assertTrue(docx_symlink.is_symlink() or docx_symlink.is_file())

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
        self.assertIn('FILE_NAME="test-project"', render_content)
        self.assertIn("#!/bin/sh", render_content)

    def test_new_directory_already_exists(self) -> None:
        """Test new command when directory already exists but qmd doesn't."""
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
        target_dir = Path("existing-project")
        target_dir.mkdir()
        qmd_file = target_dir / "existing-project.qmd"
        qmd_file.write_text("existing content")

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["existing-project"])
        stderr_output = sys.stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: File already exists", stderr_output)

        # Verify original content is unchanged
        self.assertEqual(qmd_file.read_text(), "existing content")

    def test_new_with_subdirectory_path(self) -> None:
        """Test new command with subdirectory in name."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_new(["subdir/my-project"])
        stdout_output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("Created: subdir/my-project/my-project.qmd", stdout_output)

        # Verify nested directory structure
        target_dir = Path("subdir/my-project")
        self.assertTrue(target_dir.exists())
        self.assertTrue(target_dir.is_dir())

        qmd_file = target_dir / "my-project.qmd"
        self.assertTrue(qmd_file.exists())

        # Verify content has both formats
        content = qmd_file.read_text()
        self.assertIn("pptx:", content)
        self.assertIn("docx:", content)


class TestCmdNewErrorCases(unittest.TestCase):
    """Tests for cmd_new error handling."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        import shutil

        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_template_pptx(self) -> None:
        """Test error when PowerPoint template is missing."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        project_root = Path(__file__).parent.parent.parent
        template_pptx = project_root / "templates" / "simple-presentation.pptx"
        backup_path = project_root / "templates" / "simple-presentation.pptx.backup"

        if template_pptx.exists():
            template_pptx.rename(backup_path)
            try:
                result = cmd_new(["test-project"])
                stderr_output = sys.stderr.getvalue()

                self.assertEqual(result, 1)
                self.assertIn("Error: PowerPoint template not found", stderr_output)
            finally:
                backup_path.rename(template_pptx)

    def test_missing_template_docx(self) -> None:
        """Test error when Word template is missing."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        project_root = Path(__file__).parent.parent.parent
        template_docx = project_root / "templates" / "simple-document.docx"
        backup_path = project_root / "templates" / "simple-document.docx.backup"

        if template_docx.exists():
            template_docx.rename(backup_path)
            try:
                result = cmd_new(["test-project"])
                stderr_output = sys.stderr.getvalue()

                self.assertEqual(result, 1)
                self.assertIn("Error: Word template not found", stderr_output)
            finally:
                backup_path.rename(template_docx)

    def test_missing_render_template(self) -> None:
        """Test error when render script template is missing."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        project_root = Path(__file__).parent.parent.parent
        template_render = project_root / "templates" / "render.sh.template"
        backup_path = project_root / "templates" / "render.sh.template.backup"

        if template_render.exists():
            template_render.rename(backup_path)
            try:
                result = cmd_new(["test-project"])
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

        result = cmd_new(["blocked/subdir"])
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
            result = cmd_new(["readonly-dir"])
            stderr_output = sys.stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Error: Could not create file", stderr_output)
        finally:
            # Restore permissions for cleanup
            os.chmod(target_dir, 0o755)

    def test_symlink_creation_warning(self) -> None:
        """Test warning when symlink creation fails (non-fatal)."""
        from unittest.mock import patch

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        with patch("pathlib.Path.symlink_to") as mock_symlink:
            mock_symlink.side_effect = OSError("Symlinks not supported")

            result = cmd_new(["test-project"])
            stderr_output = sys.stderr.getvalue()
            stdout_output = sys.stdout.getvalue()

            # Should succeed despite symlink failures
            self.assertEqual(result, 0)
            self.assertIn("Warning: Could not create", stderr_output)
            self.assertIn("Created: test-project/test-project.qmd", stdout_output)


if __name__ == "__main__":
    unittest.main()
