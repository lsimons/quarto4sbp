"""Unit tests for pdf-pptx command."""

import sys
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from unittest.mock import MagicMock, patch

from quarto4sbp.commands.pdf_pptx import (
    cmd_pdf_pptx,
    export_pptx_to_pdf,
    find_stale_pptx,
)


class TestFindStalePptx(unittest.TestCase):
    """Tests for find_stale_pptx function."""

    def test_no_pptx_files(self) -> None:
        """Test with directory containing no PPTX files."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            # Create some other files
            (directory / "test.txt").write_text("test")
            (directory / "test.pdf").write_text("pdf")

            result = find_stale_pptx(directory)
            self.assertEqual(result, [])

    def test_pptx_without_pdf(self) -> None:
        """Test PPTX file with no corresponding PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "presentation.pptx"
            pptx_file.write_text("pptx content")

            result = find_stale_pptx(directory)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], pptx_file)

    def test_pptx_with_older_pdf(self) -> None:
        """Test PPTX file that is newer than its PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "presentation.pptx"
            pdf_file = directory / "presentation.pdf"

            # Create PDF first
            pdf_file.write_text("old pdf")
            sleep(0.01)  # Ensure different modification times
            # Create/modify PPTX after
            pptx_file.write_text("new pptx")

            result = find_stale_pptx(directory)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], pptx_file)

    def test_pptx_with_newer_pdf(self) -> None:
        """Test PPTX file with up-to-date PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "presentation.pptx"
            pdf_file = directory / "presentation.pdf"

            # Create PPTX first
            pptx_file.write_text("pptx")
            sleep(0.01)  # Ensure different modification times
            # Create PDF after
            pdf_file.write_text("newer pdf")

            result = find_stale_pptx(directory)
            self.assertEqual(result, [])

    def test_excludes_symlinks(self) -> None:
        """Test that symlinks are excluded."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            real_file = directory / "real.pptx"
            real_file.write_text("real pptx")

            symlink = directory / "link.pptx"
            try:
                symlink.symlink_to(real_file)
            except OSError:
                # Skip test if symlinks not supported (e.g., Windows without admin)
                self.skipTest("Symlinks not supported on this platform")

            result = find_stale_pptx(directory)
            # Should only find real_file, not symlink
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], real_file)

    def test_excludes_templates_directory(self) -> None:
        """Test that files in templates directory are excluded."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            templates_dir = directory / "templates"
            templates_dir.mkdir()

            # Create PPTX in templates directory
            template_file = templates_dir / "template.pptx"
            template_file.write_text("template")

            # Create PPTX in main directory
            main_file = directory / "presentation.pptx"
            main_file.write_text("main presentation")

            result = find_stale_pptx(directory)
            # Should only find main_file, not template
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], main_file)

    def test_multiple_stale_files(self) -> None:
        """Test with multiple PPTX files needing export."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)

            # File 1: No PDF
            file1 = directory / "presentation1.pptx"
            file1.write_text("pptx1")

            # File 2: Older PDF
            file2 = directory / "presentation2.pptx"
            pdf2 = directory / "presentation2.pdf"
            pdf2.write_text("old pdf")
            sleep(0.01)
            file2.write_text("new pptx")

            # File 3: Up-to-date PDF (should be excluded)
            file3 = directory / "presentation3.pptx"
            pdf3 = directory / "presentation3.pdf"
            file3.write_text("pptx3")
            sleep(0.01)
            pdf3.write_text("new pdf")

            result = find_stale_pptx(directory)
            self.assertEqual(len(result), 2)
            self.assertIn(file1, result)
            self.assertIn(file2, result)
            self.assertNotIn(file3, result)


class TestExportPptxToPdf(unittest.TestCase):
    """Tests for export_pptx_to_pdf function."""

    @patch("quarto4sbp.commands.pdf_pptx.subprocess.run")
    def test_export_success(self, mock_run: MagicMock) -> None:
        """Test successful PDF export."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "presentation.pptx"
            pptx_file.write_text("pptx content")

            # Mock successful subprocess execution
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            # Mock PDF creation since AppleScript won't actually run
            def create_pdf(*args: object, **kwargs: object) -> MagicMock:
                pdf_file = directory / "presentation.pdf"
                pdf_file.write_text("pdf content")
                return mock_run.return_value

            mock_run.side_effect = create_pdf

            result = export_pptx_to_pdf(pptx_file)

            self.assertTrue(result)
            # Check PDF was created in original location
            pdf_file = directory / "presentation.pdf"
            self.assertTrue(pdf_file.exists())
            self.assertEqual(pdf_file.read_text(), "pdf content")

    @patch("quarto4sbp.commands.pdf_pptx.subprocess.run")
    def test_export_applescript_fails(self, mock_run: MagicMock) -> None:
        """Test handling of AppleScript failure."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "presentation.pptx"
            pptx_file.write_text("pptx content")

            # Mock failed subprocess execution
            import subprocess

            mock_run.side_effect = subprocess.CalledProcessError(
                1, "osascript", stderr="PowerPoint error"
            )

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = export_pptx_to_pdf(pptx_file)
                output = sys.stdout.getvalue()

                self.assertFalse(result)
                self.assertIn("Error:", output)
                self.assertIn("AppleScript failed", output)
            finally:
                sys.stdout = old_stdout

    @patch("quarto4sbp.commands.pdf_pptx.subprocess.run")
    def test_export_pdf_not_created(self, mock_run: MagicMock) -> None:
        """Test handling when PowerPoint doesn't create PDF."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "presentation.pptx"
            pptx_file.write_text("pptx content")

            # Mock successful subprocess but don't create PDF
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = export_pptx_to_pdf(pptx_file)
                output = sys.stdout.getvalue()

                self.assertFalse(result)
                self.assertIn("Error:", output)
                self.assertIn("did not create PDF", output)
            finally:
                sys.stdout = old_stdout


class TestCmdPdfPptx(unittest.TestCase):
    """Tests for cmd_pdf_pptx function."""

    @patch("quarto4sbp.commands.pdf_pptx.export_pptx_to_pdf")
    def test_no_directory_argument(self, mock_export: MagicMock) -> None:
        """Test running command in current directory."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "test.pptx"
            pptx_file.write_text("pptx")

            # Mock export to prevent actual PowerPoint invocation
            mock_export.return_value = True

            # Change to temp directory
            import os

            old_cwd = os.getcwd()
            try:
                os.chdir(directory)

                old_stdout = sys.stdout
                sys.stdout = StringIO()
                try:
                    result = cmd_pdf_pptx([])
                    output = sys.stdout.getvalue()

                    self.assertEqual(result, 0)
                    self.assertIn("Found 1 file(s) to export", output)
                    self.assertIn("test.pptx", output)
                finally:
                    sys.stdout = old_stdout
            finally:
                os.chdir(old_cwd)

    @patch("quarto4sbp.commands.pdf_pptx.export_pptx_to_pdf")
    def test_with_directory_argument(self, mock_export: MagicMock) -> None:
        """Test running command with directory argument."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "test.pptx"
            pptx_file.write_text("pptx")

            # Mock export to prevent actual PowerPoint invocation
            mock_export.return_value = True

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = cmd_pdf_pptx([str(directory)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("Found 1 file(s) to export", output)
                self.assertIn("test.pptx", output)
            finally:
                sys.stdout = old_stdout

    def test_nonexistent_directory(self) -> None:
        """Test with nonexistent directory argument."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = cmd_pdf_pptx(["/nonexistent/directory/path"])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Error:", output)
            self.assertIn("does not exist", output)
        finally:
            sys.stdout = old_stdout

    def test_file_instead_of_directory(self) -> None:
        """Test with file path instead of directory."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            file_path = directory / "test.txt"
            file_path.write_text("test")

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = cmd_pdf_pptx([str(file_path)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 1)
                self.assertIn("Error:", output)
                self.assertIn("not a directory", output)
            finally:
                sys.stdout = old_stdout

    def test_no_files_to_export(self) -> None:
        """Test with directory containing no PPTX files."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = cmd_pdf_pptx([str(directory)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("No PPTX files need exporting", output)
            finally:
                sys.stdout = old_stdout

    @patch("quarto4sbp.commands.pdf_pptx.export_pptx_to_pdf")
    def test_export_integration(self, mock_export: MagicMock) -> None:
        """Test command with successful export."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "test.pptx"
            pptx_file.write_text("pptx")

            # Mock successful export
            mock_export.return_value = True

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = cmd_pdf_pptx([str(directory)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("Found 1 file(s) to export", output)
                self.assertIn("Exporting: test.pptx", output)
                self.assertIn("Exported 1 file(s)", output)
                mock_export.assert_called_once()
            finally:
                sys.stdout = old_stdout

    @patch("quarto4sbp.commands.pdf_pptx.export_pptx_to_pdf")
    def test_export_with_failure(self, mock_export: MagicMock) -> None:
        """Test command when export fails."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "test.pptx"
            pptx_file.write_text("pptx")

            # Mock failed export
            mock_export.return_value = False

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = cmd_pdf_pptx([str(directory)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("skipped 1 file(s)", output)
            finally:
                sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
