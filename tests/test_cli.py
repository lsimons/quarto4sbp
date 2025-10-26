"""Unit tests for q4s CLI tool."""

import subprocess
import sys
import unittest
from io import StringIO
from tempfile import TemporaryDirectory

from quarto4sbp.cli import main


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

    def test_echo_command(self) -> None:
        """Test echo command with arguments."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = main(["echo", "hello", "world"])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertEqual(output.strip(), "hello world")
        finally:
            sys.stdout = old_stdout

    def test_echo_no_args(self) -> None:
        """Test echo command with no arguments."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = main(["echo"])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertEqual(output.strip(), "")
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

    def test_pdf_command(self) -> None:
        """Test pdf command integration."""
        with TemporaryDirectory() as tmpdir:
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            try:
                result = main(["pdf", tmpdir])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("No PPTX files need exporting", output)
            finally:
                sys.stdout = old_stdout


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for the q4s CLI."""

    def test_cli_new(self) -> None:
        """Test CLI new command via subprocess."""
        import shutil
        import tempfile
        from pathlib import Path

        # Create a temporary directory for the test
        temp_dir = tempfile.mkdtemp()
        try:
            result = subprocess.run(
                ["uv", "run", "q4s", "new", "test-pres"],
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
        self.assertIn("echo", result.stdout)

    def test_cli_echo(self) -> None:
        """Test CLI echo via subprocess."""
        result = subprocess.run(
            ["uv", "run", "q4s", "echo", "hello", "world"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "hello world")

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
