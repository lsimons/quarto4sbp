"""Unit tests for unified pdf command."""

import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from quarto4sbp.commands.pdf import cmd_pdf


class TestCmdPdf(unittest.TestCase):
    """Tests for cmd_pdf unified function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    @patch("quarto4sbp.commands.pdf.cmd_pdf_pptx")
    @patch("quarto4sbp.commands.pdf.cmd_pdf_doc")
    def test_both_commands_succeed(
        self, mock_pdf_doc: MagicMock, mock_pdf_pptx: MagicMock
    ) -> None:
        """Test unified command when both format exports succeed."""
        mock_pdf_pptx.return_value = 0
        mock_pdf_doc.return_value = 0

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf([])
        output = sys.stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn("=== Exporting PowerPoint files ===", output)
        self.assertIn("=== Exporting Word documents ===", output)
        self.assertIn("✓ All exports completed successfully", output)

        # Verify both commands were called
        mock_pdf_pptx.assert_called_once_with([])
        mock_pdf_doc.assert_called_once_with([])

    @patch("quarto4sbp.commands.pdf.cmd_pdf_pptx")
    @patch("quarto4sbp.commands.pdf.cmd_pdf_doc")
    def test_pptx_fails(
        self, mock_pdf_doc: MagicMock, mock_pdf_pptx: MagicMock
    ) -> None:
        """Test unified command when PowerPoint export fails."""
        mock_pdf_pptx.return_value = 1
        mock_pdf_doc.return_value = 0

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf([])
        output = sys.stdout.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("✗ Some exports failed", output)

        # Verify both commands were called despite failure
        mock_pdf_pptx.assert_called_once_with([])
        mock_pdf_doc.assert_called_once_with([])

    @patch("quarto4sbp.commands.pdf.cmd_pdf_pptx")
    @patch("quarto4sbp.commands.pdf.cmd_pdf_doc")
    def test_doc_fails(self, mock_pdf_doc: MagicMock, mock_pdf_pptx: MagicMock) -> None:
        """Test unified command when Word export fails."""
        mock_pdf_pptx.return_value = 0
        mock_pdf_doc.return_value = 1

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf([])
        output = sys.stdout.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("✗ Some exports failed", output)

        # Verify both commands were called
        mock_pdf_pptx.assert_called_once_with([])
        mock_pdf_doc.assert_called_once_with([])

    @patch("quarto4sbp.commands.pdf.cmd_pdf_pptx")
    @patch("quarto4sbp.commands.pdf.cmd_pdf_doc")
    def test_both_fail(self, mock_pdf_doc: MagicMock, mock_pdf_pptx: MagicMock) -> None:
        """Test unified command when both exports fail."""
        mock_pdf_pptx.return_value = 1
        mock_pdf_doc.return_value = 1

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf([])
        output = sys.stdout.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("✗ Some exports failed", output)

        # Verify both commands were called
        mock_pdf_pptx.assert_called_once_with([])
        mock_pdf_doc.assert_called_once_with([])

    @patch("quarto4sbp.commands.pdf.cmd_pdf_pptx")
    @patch("quarto4sbp.commands.pdf.cmd_pdf_doc")
    def test_with_directory_argument(
        self, mock_pdf_doc: MagicMock, mock_pdf_pptx: MagicMock
    ) -> None:
        """Test unified command with directory argument."""
        mock_pdf_pptx.return_value = 0
        mock_pdf_doc.return_value = 0

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf(["/some/directory"])

        self.assertEqual(result, 0)

        # Verify both commands received the directory argument
        mock_pdf_pptx.assert_called_once_with(["/some/directory"])
        mock_pdf_doc.assert_called_once_with(["/some/directory"])

    @patch("quarto4sbp.commands.pdf.cmd_pdf_pptx")
    @patch("quarto4sbp.commands.pdf.cmd_pdf_doc")
    def test_output_sections(
        self, mock_pdf_doc: MagicMock, mock_pdf_pptx: MagicMock
    ) -> None:
        """Test that output is clearly sectioned."""
        mock_pdf_pptx.return_value = 0
        mock_pdf_doc.return_value = 0

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf([])
        output = sys.stdout.getvalue()

        # Verify clear section headers
        lines = output.split("\n")
        pptx_section_idx = next(
            i for i, line in enumerate(lines) if "PowerPoint" in line
        )
        doc_section_idx = next(i for i, line in enumerate(lines) if "Word" in line)

        # Word section should come after PowerPoint section
        self.assertLess(pptx_section_idx, doc_section_idx)

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
