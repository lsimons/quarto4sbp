"""Unit tests for help command."""

import sys
import unittest
from io import StringIO

from quarto4sbp.commands.help import cmd_help


class TestCmdHelp(unittest.TestCase):
    """Tests for cmd_help function."""

    def test_help_returns_zero(self) -> None:
        """Test that help command returns exit code 0."""
        result = cmd_help()
        self.assertEqual(result, 0)

    def test_help_output(self) -> None:
        """Test that help command outputs expected content."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            _ = cmd_help()
            output = sys.stdout.getvalue()

            # Check for key content
            self.assertIn("q4s", output)
            self.assertIn("help", output)
            self.assertIn("Usage:", output)
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
