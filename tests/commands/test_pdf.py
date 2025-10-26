"""Unit tests for pdf command."""

import sys
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

from quarto4sbp.commands.pdf import (
    cleanup_temp_dir,
    cmd_pdf,
    copy_pdf_to_destination,
    create_temp_export_dir,
    find_stale_pptx,
    prepare_file_for_export,
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


class TestTempFolderManagement(unittest.TestCase):
    """Tests for temporary folder management functions."""

    def test_create_temp_export_dir(self) -> None:
        """Test creating temporary export directory."""
        temp_dir = create_temp_export_dir()
        try:
            self.assertTrue(temp_dir.exists())
            self.assertTrue(temp_dir.is_dir())
            # Check that directory name has correct prefix
            self.assertTrue(temp_dir.name.startswith("q4s-pdf-"))
        finally:
            cleanup_temp_dir(temp_dir)

    def test_prepare_file_for_export(self) -> None:
        """Test preparing PPTX file for export."""
        with TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            source_dir.mkdir()
            pptx_file = source_dir / "presentation.pptx"
            pptx_file.write_text("pptx content")

            temp_dir = create_temp_export_dir()
            try:
                temp_pptx, temp_pdf = prepare_file_for_export(pptx_file, temp_dir)

                # Check temp PPTX was created
                self.assertTrue(temp_pptx.exists())
                self.assertEqual(temp_pptx.name, "presentation.pptx")
                self.assertEqual(temp_pptx.read_text(), "pptx content")

                # Check temp PDF path is correct
                self.assertEqual(temp_pdf.name, "presentation.pdf")
                self.assertEqual(temp_pdf.parent, temp_dir)
            finally:
                cleanup_temp_dir(temp_dir)

    def test_copy_pdf_to_destination(self) -> None:
        """Test copying PDF from temp directory to destination."""
        with TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir) / "temp"
            temp_dir.mkdir()
            temp_pdf = temp_dir / "presentation.pdf"
            temp_pdf.write_text("pdf content")

            dest_dir = Path(tmpdir) / "dest"
            dest_dir.mkdir()
            dest_pdf = dest_dir / "presentation.pdf"

            copy_pdf_to_destination(temp_pdf, dest_pdf)

            self.assertTrue(dest_pdf.exists())
            self.assertEqual(dest_pdf.read_text(), "pdf content")

    def test_cleanup_temp_dir(self) -> None:
        """Test cleaning up temporary directory."""
        temp_dir = create_temp_export_dir()
        # Create some files in temp dir
        (temp_dir / "file1.txt").write_text("test1")
        (temp_dir / "file2.txt").write_text("test2")

        cleanup_temp_dir(temp_dir)

        self.assertFalse(temp_dir.exists())

    def test_cleanup_temp_dir_nonexistent(self) -> None:
        """Test cleanup doesn't fail on nonexistent directory."""
        temp_dir = Path("/tmp/nonexistent-q4s-pdf-dir")
        # Should not raise an exception
        cleanup_temp_dir(temp_dir)

    def test_prepare_file_preserves_timestamps(self) -> None:
        """Test that prepare_file_for_export preserves timestamps."""
        with TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            source_dir.mkdir()
            pptx_file = source_dir / "presentation.pptx"
            pptx_file.write_text("pptx content")

            original_mtime = pptx_file.stat().st_mtime

            temp_dir = create_temp_export_dir()
            try:
                temp_pptx, _ = prepare_file_for_export(pptx_file, temp_dir)
                temp_mtime = temp_pptx.stat().st_mtime

                # shutil.copy2 should preserve timestamps
                self.assertEqual(temp_mtime, original_mtime)
            finally:
                cleanup_temp_dir(temp_dir)


class TestCmdPdf(unittest.TestCase):
    """Tests for cmd_pdf function."""

    def test_no_directory_argument(self) -> None:
        """Test running command in current directory."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "test.pptx"
            pptx_file.write_text("pptx")

            # Change to temp directory
            import os

            old_cwd = os.getcwd()
            try:
                os.chdir(directory)

                old_stdout = sys.stdout
                sys.stdout = StringIO()
                try:
                    result = cmd_pdf([])
                    output = sys.stdout.getvalue()

                    self.assertEqual(result, 0)
                    self.assertIn("Found 1 file(s) to export", output)
                    self.assertIn("test.pptx", output)
                finally:
                    sys.stdout = old_stdout
            finally:
                os.chdir(old_cwd)

    def test_with_directory_argument(self) -> None:
        """Test running command with directory argument."""
        with TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            pptx_file = directory / "test.pptx"
            pptx_file.write_text("pptx")

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = cmd_pdf([str(directory)])
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
            result = cmd_pdf(["/nonexistent/directory/path"])
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
                result = cmd_pdf([str(file_path)])
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
                result = cmd_pdf([str(directory)])
                output = sys.stdout.getvalue()

                self.assertEqual(result, 0)
                self.assertIn("No PPTX files need exporting", output)
            finally:
                sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
