"""Integration tests for pdf command (requires PowerPoint).

These tests are skipped by default and only run when RUN_INTEGRATION_TESTS
environment variable is set.

To run these tests:
    RUN_INTEGRATION_TESTS=1 uv run pytest tests/commands/test_pdf_integration.py -v
"""

import os
import shutil
import sys
import unittest
from io import StringIO
from pathlib import Path
from time import sleep

from quarto4sbp.commands.pdf import cmd_pdf, export_pptx_to_pdf

# Check if integration tests should run
RUN_INTEGRATION_TESTS = os.environ.get("RUN_INTEGRATION_TESTS", "0") == "1"


@unittest.skipUnless(
    RUN_INTEGRATION_TESTS, "Integration tests disabled (set RUN_INTEGRATION_TESTS=1)"
)
class TestPdfIntegration(unittest.TestCase):
    """Integration tests that require PowerPoint to be installed."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Get path to template PPTX file
        self.project_root = Path(__file__).parent.parent.parent
        self.template_pptx = (
            self.project_root / "templates" / "simple-presentation.pptx"
        )

        # Verify template exists
        if not self.template_pptx.exists():
            self.skipTest(f"Template not found: {self.template_pptx}")

        # Create test directory for integration tests
        self.test_dir = self.project_root / "test-pdf-integration"
        self.test_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        """Clean up test files."""
        # Remove all test files
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_export_real_pptx(self) -> None:
        """Test exporting a real PPTX file to PDF.

        This test requires:
        1. Microsoft PowerPoint to be installed
        2. RUN_INTEGRATION_TESTS=1 environment variable
        """
        # Copy template to test directory
        test_pptx = self.test_dir / "test-presentation.pptx"
        shutil.copy2(self.template_pptx, test_pptx)

        # Export to PDF
        result = export_pptx_to_pdf(test_pptx)

        # Verify export succeeded
        self.assertTrue(result, "Export should succeed")

        # Verify PDF was created
        pdf_path = test_pptx.with_suffix(".pdf")
        self.assertTrue(pdf_path.exists(), "PDF should be created")
        self.assertGreater(pdf_path.stat().st_size, 0, "PDF should not be empty")

        # Verify PDF is larger than a minimal size (real PDFs are substantial)
        self.assertGreater(
            pdf_path.stat().st_size,
            1000,
            "PDF should be at least 1KB (indicates real content)",
        )

    def test_export_does_not_update_when_pdf_newer(self) -> None:
        """Test that export is skipped when PDF is already up to date."""
        # Copy template and export
        test_pptx = self.test_dir / "test-presentation2.pptx"
        shutil.copy2(self.template_pptx, test_pptx)

        result = export_pptx_to_pdf(test_pptx)
        self.assertTrue(result, "First export should succeed")

        pdf_path = test_pptx.with_suffix(".pdf")
        self.assertTrue(pdf_path.exists())

        # Sleep to ensure time difference
        sleep(0.1)

        # Touch PDF to make it newer
        pdf_path.touch()

        # Verify PDF is now newer than PPTX
        self.assertGreater(pdf_path.stat().st_mtime, test_pptx.stat().st_mtime)

        # find_stale_pptx should not include this file
        from quarto4sbp.commands.pdf import find_stale_pptx

        stale = find_stale_pptx(self.test_dir)
        self.assertEqual(len(stale), 0, "PDF is up to date, should not be stale")

    def test_export_updates_when_pptx_newer(self) -> None:
        """Test that export happens when PPTX is modified after PDF creation."""
        # Copy template and export
        test_pptx = self.test_dir / "test-presentation3.pptx"
        shutil.copy2(self.template_pptx, test_pptx)

        result = export_pptx_to_pdf(test_pptx)
        self.assertTrue(result, "First export should succeed")

        pdf_path = test_pptx.with_suffix(".pdf")

        # Sleep to ensure time difference
        sleep(0.1)

        # Touch PPTX to make it newer
        test_pptx.touch()

        # Verify PPTX is now newer than PDF
        self.assertGreater(test_pptx.stat().st_mtime, pdf_path.stat().st_mtime)

        # find_stale_pptx should include this file
        from quarto4sbp.commands.pdf import find_stale_pptx

        stale = find_stale_pptx(self.test_dir)
        self.assertEqual(len(stale), 1, "PPTX is newer, should be stale")
        self.assertEqual(stale[0], test_pptx)

    def test_cmd_pdf_integration(self) -> None:
        """Test complete pdf command with real PowerPoint export."""
        # Create multiple PPTX files
        test_pptx1 = self.test_dir / "presentation1.pptx"
        test_pptx2 = self.test_dir / "presentation2.pptx"
        shutil.copy2(self.template_pptx, test_pptx1)
        shutil.copy2(self.template_pptx, test_pptx2)

        # Run command
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = cmd_pdf([str(self.test_dir)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0, "Command should succeed")
            self.assertIn("Found 2 file(s) to export", output)
            self.assertIn("Exported 2 file(s)", output)
        finally:
            sys.stdout = old_stdout

        # Verify both PDFs were created
        pdf1 = self.test_dir / "presentation1.pdf"
        pdf2 = self.test_dir / "presentation2.pdf"
        self.assertTrue(pdf1.exists(), "First PDF should be created")
        self.assertTrue(pdf2.exists(), "Second PDF should be created")
        self.assertGreater(pdf1.stat().st_size, 1000)
        self.assertGreater(pdf2.stat().st_size, 1000)

    def test_cmd_pdf_skips_up_to_date(self) -> None:
        """Test that command skips files with up-to-date PDFs."""
        # Copy template and export once
        test_pptx = self.test_dir / "test4.pptx"
        shutil.copy2(self.template_pptx, test_pptx)

        # First run
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = cmd_pdf([str(self.test_dir)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("Found 1 file(s) to export", output)
        finally:
            sys.stdout = old_stdout

        # Touch PDF to make it newer
        pdf_path = self.test_dir / "test4.pdf"
        sleep(0.1)
        pdf_path.touch()

        # Second run should skip
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = cmd_pdf([str(self.test_dir)])
            output = sys.stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn("No PPTX files need exporting", output)
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
