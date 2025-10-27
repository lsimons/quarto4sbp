"""Unit tests for q4s CLI tool."""

import subprocess
import sys
import unittest
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from quarto4sbp.cli import main
from tests.mocks.llm_client import MockLLMClient


class TestMain(unittest.TestCase):
    """Tests for main function."""

    def test_no_args_shows_help(self) -> None:
        """Test that no arguments defaults to help."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = main([])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("q4s", output)
            self.assertIn("help", output)
        finally:
            sys.stdout = old_stdout

    def test_help_command(self) -> None:
        """Test explicit help command."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = main(["help"])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("q4s", output)
        finally:
            sys.stdout = old_stdout

    def test_invalid_command(self) -> None:
        """Test invalid command returns error."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        try:
            result = main(["invalid"])
            stderr = sys.stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Unknown command", stderr)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def test_pdf_pptx_command(self) -> None:
        """Test pdf-pptx command integration."""
        with TemporaryDirectory() as tmpdir:
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                result = main(["pdf-pptx", tmpdir])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("No PPTX files need exporting", output)
            finally:
                sys.stdout = old_stdout

    def test_new_docx_command(self) -> None:
        """Test new-docx command integration."""
        with TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                os.chdir(tmpdir)
                result = main(["new-docx", "test-doc"])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("Created: test-doc/test-doc.qmd", output)
            finally:
                os.chdir(old_cwd)
                sys.stdout = old_stdout

    def test_pdf_docx_command(self) -> None:
        """Test pdf-docx command integration."""
        with TemporaryDirectory() as tmpdir:
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                result = main(["pdf-docx", tmpdir])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("No DOCX files need exporting", output)
            finally:
                sys.stdout = old_stdout

    def test_new_command(self) -> None:
        """Test unified new command integration."""
        with TemporaryDirectory() as tmpdir:
            import os

            old_cwd = os.getcwd()
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                os.chdir(tmpdir)
                result = main(["new", "test-project"])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("Created: test-project/test-project.qmd", output)
                self.assertIn(
                    "Outputs: Both PowerPoint (.pptx) and Word (.docx)", output
                )
            finally:
                os.chdir(old_cwd)
                sys.stdout = old_stdout

    def test_pdf_command(self) -> None:
        """Test unified pdf command integration."""
        with TemporaryDirectory() as tmpdir:
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                result = main(["pdf", tmpdir])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("=== Exporting PowerPoint files ===", output)
                self.assertIn("=== Exporting Word documents ===", output)
                self.assertIn("✓ All exports completed successfully", output)
            finally:
                sys.stdout = old_stdout

    def test_llm_command(self) -> None:
        """Test llm command integration (without args shows usage)."""
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            result = main(["llm"])
            stderr = sys.stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Usage: q4s llm test", stderr)
        finally:
            sys.stderr = old_stderr

    @patch("quarto4sbp.commands.tov.LLMClient")
    def test_tov_command_with_flags(self, mock_llm_class) -> None:  # type: ignore
        """Test tov command integration with flags."""
        import tempfile
        from pathlib import Path

        # Set up mock
        mock_client = MockLLMClient()
        mock_client.add_response(r".*", "# Rewritten\n\nRewritten content.\n")
        mock_llm_class.return_value = mock_client

        # Create a temporary QMD file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.qmd"
            test_file.write_text("""---
title: "Test"
---

# Introduction

This is test content.
""")

            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                # Test with --dry-run flag
                result = main(["tov", "--dry-run", str(test_file)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("Processing:", output)
                self.assertIn("[DRY RUN]", output)
            finally:
                sys.stdout = old_stdout


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for the q4s CLI."""

    def test_cli_new_pptx(self) -> None:
        """Test CLI new-pptx command via subprocess."""
        import shutil
        import tempfile
        from pathlib import Path

        # Create a temporary directory for the test
        temp_dir = tempfile.mkdtemp()
        try:
            result = subprocess.run(
                ["uv", "run", "q4s", "new-pptx", "test-pres"],
                capture_output=True,
                text=True,
                check=False,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Created: test-pres/test-pres.qmd", result.stdout)
            self.assertIn("Hint: Run 'cd test-pres && ./render.sh'", result.stdout)

            # Verify files were created
            qmd_file = Path(temp_dir) / "test-pres" / "test-pres.qmd"
            self.assertTrue(qmd_file.exists())
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_help(self) -> None:
        """Test CLI help via subprocess."""
        result = subprocess.run(
            ["uv", "run", "q4s", "help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("q4s", result.stdout)
        self.assertIn("help", result.stdout)

    def test_cli_new_docx(self) -> None:
        """Test CLI new-docx command via subprocess."""
        import shutil
        import tempfile
        from pathlib import Path

        # Create a temporary directory for the test
        temp_dir = tempfile.mkdtemp()
        try:
            result = subprocess.run(
                ["uv", "run", "q4s", "new-docx", "test-doc"],
                capture_output=True,
                text=True,
                check=False,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Created: test-doc/test-doc.qmd", result.stdout)
            self.assertIn("Hint: Run 'cd test-doc && ./render.sh'", result.stdout)

            # Verify files were created
            qmd_file = Path(temp_dir) / "test-doc" / "test-doc.qmd"
            self.assertTrue(qmd_file.exists())
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_new(self) -> None:
        """Test CLI new command via subprocess."""
        import shutil
        import tempfile
        from pathlib import Path

        # Create a temporary directory for the test
        temp_dir = tempfile.mkdtemp()
        try:
            result = subprocess.run(
                ["uv", "run", "q4s", "new", "test-project"],
                capture_output=True,
                text=True,
                check=False,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Created: test-project/test-project.qmd", result.stdout)
            self.assertIn(
                "Outputs: Both PowerPoint (.pptx) and Word (.docx)", result.stdout
            )

            # Verify QMD file was created
            qmd_file = Path(temp_dir) / "test-project" / "test-project.qmd"
            self.assertTrue(qmd_file.exists())

            # Verify it has both output formats
            content = qmd_file.read_text()
            self.assertIn("pptx:", content)
            self.assertIn("docx:", content)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_invalid_command(self) -> None:
        """Test CLI with invalid command via subprocess."""
        result = subprocess.run(
            ["uv", "run", "q4s", "invalid"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Unknown command", result.stderr)


if __name__ == "__main__":
    unittest.main()
