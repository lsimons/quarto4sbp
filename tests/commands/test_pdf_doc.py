"""Unit tests for pdf-doc command."""

import sys
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from unittest.mock import MagicMock, patch

from quarto4sbp.commands.pdf_doc import (
    cmd_pdf_doc,
    export_docx_to_pdf,
    find_stale_docx,
)


class TestFindStaleDocx(unittest.TestCase):
    """Tests for find_stale_docx function."""

    def test_no_docx_files(self) -> None:
        """Test with directory containing no DOCX files."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            # Create some other files
            (directory / "test.txt").write_text("test")
            (directory / "test.pdf").write_text("pdf")

            result = find_stale_docx(directory)
            self.assertEqual(result, [])

    def test_docx_without_pdf(self) -> None:
        """Test DOCX file with no corresponding PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            docx_file.write_text("docx content")

            result = find_stale_docx(directory)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], docx_file)

    def test_docx_with_older_pdf(self) -> None:
        """Test DOCX file that is newer than its PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            pdf_file = directory / "document.pdf"

            # Create PDF first
            pdf_file.write_text("old pdf")
            sleep(0.01)  # Ensure different modification times
            # Create/modify DOCX after
            docx_file.write_text("new docx")

            result = find_stale_docx(directory)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], docx_file)

    def test_docx_with_newer_pdf(self) -> None:
        """Test DOCX file with up-to-date PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            pdf_file = directory / "document.pdf"

            # Create DOCX first
            docx_file.write_text("docx")
            sleep(0.01)  # Ensure different modification times
            # Create PDF after
            pdf_file.write_text("newer pdf")

            result = find_stale_docx(directory)
            self.assertEqual(result, [])

    def test_excludes_symlinks(self) -> None:
        """Test that symlinks are excluded."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            real_file = directory / "real.docx"
            real_file.write_text("real docx")

            symlink = directory / "link.docx"
            try:
                symlink.symlink_to(real_file)
            except OSError:
                # Skip test if symlinks not supported (e.g., Windows without admin)
                self.skipTest("Symlinks not supported on this platform")

            result = find_stale_docx(directory)
            # Should only find real_file, not symlink
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], real_file)

    def test_excludes_templates_directory(self) -> None:
        """Test that files in templates directory are excluded."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            templates_dir = directory / "templates"
            templates_dir.mkdir()

            # Create DOCX in templates directory
            template_file = templates_dir / "template.docx"
            template_file.write_text("template")

            # Create DOCX in main directory
            main_file = directory / "document.docx"
            main_file.write_text("main document")

            result = find_stale_docx(directory)
            # Should only find main_file, not template
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], main_file)

    def test_multiple_stale_files(self) -> None:
        """Test with multiple DOCX files needing export."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)

            # File 1: No PDF
            file1 = directory / "document1.docx"
            file1.write_text("docx1")

            # File 2: Older PDF
            file2 = directory / "document2.docx"
            pdf2 = directory / "document2.pdf"
            pdf2.write_text("old pdf")
            sleep(0.01)
            file2.write_text("new docx")

            # File 3: Up-to-date PDF (should be excluded)
            file3 = directory / "document3.docx"
            pdf3 = directory / "document3.pdf"
            file3.write_text("docx3")
            sleep(0.01)
            pdf3.write_text("new pdf")

            result = find_stale_docx(directory)
            self.assertEqual(len(result), 2)
            self.assertIn(file1, result)
            self.assertIn(file2, result)
            self.assertNotIn(file3, result)


class TestExportDocxToPdf(unittest.TestCase):
    """Tests for export_docx_to_pdf function."""

    @patch("quarto4sbp.commands.pdf_doc.subprocess.run")
    def test_export_success(self, mock_run: MagicMock) -> None:
        """Test successful PDF export."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            docx_file.write_text("docx content")

            # Mock successful subprocess execution
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            # Mock PDF creation since AppleScript won't actually run
            def create_pdf(*args: object, **kwargs: object) -> MagicMock:
                pdf_file = directory / "document.pdf"
                pdf_file.write_text("pdf content")
                return mock_run.return_value

            mock_run.side_effect = create_pdf

            result = export_docx_to_pdf(docx_file)

            self.assertTrue(result)
            # Check PDF was created in original location
            pdf_file = directory / "document.pdf"
            self.assertTrue(pdf_file.exists())
            self.assertEqual(pdf_file.read_text(), "pdf content")

    @patch("quarto4sbp.commands.pdf_doc.subprocess.run")
    def test_export_applescript_fails(self, mock_run: MagicMock) -> None:
        """Test handling of AppleScript failure."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            docx_file.write_text("docx content")

            # Mock failed subprocess execution
            import subprocess

            mock_run.side_effect = subprocess.CalledProcessError(
                1, "osascript", stderr="Word error"
            )

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = export_docx_to_pdf(docx_file)
                output = sys.stdout.getvalue()

                self.assertFalse(result)
                self.assertIn("Error:", output)
                self.assertIn("AppleScript failed", output)
            finally:
                sys.stdout = old_stdout

    @patch("quarto4sbp.commands.pdf_doc.subprocess.run")
    def test_export_pdf_not_created(self, mock_run: MagicMock) -> None:
        """Test handling when PDF is not created."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            docx_file.write_text("docx content")

            # Mock successful subprocess but no PDF created
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = export_docx_to_pdf(docx_file)
                output = sys.stdout.getvalue()

                self.assertFalse(result)
                self.assertIn("Error:", output)
                self.assertIn("Word did not create PDF", output)
            finally:
                sys.stdout = old_stdout


class TestCmdPdfDoc(unittest.TestCase):
    """Tests for cmd_pdf_doc function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def test_no_docx_files(self) -> None:
        """Test command with no DOCX files in directory."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            (directory / "test.txt").write_text("test")

            sys.stdout = StringIO()
            sys.stderr = StringIO()

            result = cmd_pdf_doc([str(directory)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("No DOCX files need exporting", output)

    @patch("quarto4sbp.commands.pdf_doc.export_docx_to_pdf")
    def test_export_single_file(self, mock_export: MagicMock) -> None:
        """Test exporting a single DOCX file."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx_file = directory / "document.docx"
            docx_file.write_text("docx content")

            # Mock successful export
            mock_export.return_value = True

            sys.stdout = StringIO()
            sys.stderr = StringIO()

            result = cmd_pdf_doc([str(directory)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("Found 1 file(s) to export", output)
            self.assertIn("document.docx", output)
            self.assertIn("Exporting: document.docx -> document.pdf", output)
            self.assertIn("Exported 1 file(s)", output)
            self.assertIn("skipped 0 file(s)", output)

    @patch("quarto4sbp.commands.pdf_doc.export_docx_to_pdf")
    def test_export_multiple_files(self, mock_export: MagicMock) -> None:
        """Test exporting multiple DOCX files."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx1 = directory / "document1.docx"
            docx1.write_text("docx1")
            docx2 = directory / "document2.docx"
            docx2.write_text("docx2")

            # Mock successful exports
            mock_export.return_value = True

            sys.stdout = StringIO()
            sys.stderr = StringIO()

            result = cmd_pdf_doc([str(directory)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("Found 2 file(s) to export", output)
            self.assertIn("Exported 2 file(s)", output)

    @patch("quarto4sbp.commands.pdf_doc.export_docx_to_pdf")
    def test_export_with_failures(self, mock_export: MagicMock) -> None:
        """Test handling of export failures."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            docx1 = directory / "document1.docx"
            docx1.write_text("docx1")
            docx2 = directory / "document2.docx"
            docx2.write_text("docx2")

            # Mock one success, one failure
            mock_export.side_effect = [True, False]

            sys.stdout = StringIO()
            sys.stderr = StringIO()

            result = cmd_pdf_doc([str(directory)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("Exported 1 file(s)", output)
            self.assertIn("skipped 1 file(s)", output)

    def test_default_to_current_directory(self) -> None:
        """Test that command defaults to current directory."""
        with TemporaryDirectory() as tmpdir:
            import os

            original_cwd = Path.cwd()
            os.chdir(tmpdir)

            try:
                # Create a DOCX file in current directory
                docx_file = Path("document.docx")
                docx_file.write_text("docx")

                sys.stdout = StringIO()
                sys.stderr = StringIO()

                # Call without directory argument
                with patch("quarto4sbp.commands.pdf_doc.export_docx_to_pdf") as mock:
                    mock.return_value = True
                    result = cmd_pdf_doc([])
                    output = sys.stdout.getvalue()

                    self.assertEqual(result, 0)
                    self.assertIn("Found 1 file(s) to export", output)
            finally:
                os.chdir(original_cwd)

    def test_invalid_directory(self) -> None:
        """Test error handling for invalid directory."""
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        result = cmd_pdf_doc(["/nonexistent/directory"])
        output = sys.stdout.getvalue()

        self.assertEqual(result, 1)
        self.assertIn("Error: Directory", output)
        self.assertIn("does not exist", output)

    def test_directory_is_file(self) -> None:
        """Test error handling when path is a file, not directory."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            file_path = directory / "file.txt"
            file_path.write_text("test")

            sys.stdout = StringIO()
            sys.stderr = StringIO()

            result = cmd_pdf_doc([str(file_path)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Error:", output)
            self.assertIn("is not a directory", output)


if __name__ == "__main__":
    unittest.main()
