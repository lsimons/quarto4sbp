"""Unit tests for echo command."""

import sys
import unittest
from io import StringIO

from quarto4sbp.commands.echo import cmd_echo


class TestCmdEcho(unittest.TestCase):
    """Tests for cmd_echo function."""

    def test_echo_empty_args(self) -> None:
        """Test echo with no arguments."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = cmd_echo([])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertEqual(output.strip(), "")
        finally:
            sys.stdout = old_stdout

    def test_echo_single_arg(self) -> None:
        """Test echo with single argument."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = cmd_echo(["hello"])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertEqual(output.strip(), "hello")
        finally:
            sys.stdout = old_stdout

    def test_echo_multiple_args(self) -> None:
        """Test echo with multiple arguments."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = cmd_echo(["hello", "world", "test"])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertEqual(output.strip(), "hello world test")
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
