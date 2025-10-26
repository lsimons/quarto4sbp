"""Integration tests for pdf command (requires PowerPoint).

These tests are skipped by default and only run when RUN_INTEGRATION_TESTS
environment variable is set.

To run these tests:
    RUN_INTEGRATION_TESTS=1 uv run pytest tests/commands/test_pdf_integration.py -v
"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# Check if integration tests should run
RUN_INTEGRATION_TESTS = os.environ.get("RUN_INTEGRATION_TESTS", "0") == "1"


@unittest.skipUnless(
    RUN_INTEGRATION_TESTS, "Integration tests disabled (set RUN_INTEGRATION_TESTS=1)"
)
class TestPdfIntegration(unittest.TestCase):
    """Integration tests that require PowerPoint to be installed."""

    def setUp(self) -> None:
        """Create a minimal PPTX file for testing."""
        # Note: For real testing, you'll need actual PPTX files
        # This is a placeholder that shows the test structure
        pass

    def test_export_real_pptx(self) -> None:
        """Test exporting a real PPTX file to PDF.

        This test requires:
        1. Microsoft PowerPoint to be installed
        2. A valid PPTX file to test with
        3. RUN_INTEGRATION_TESTS=1 environment variable

        Manual testing steps:
        1. Create a test PPTX file in a temp directory
        2. Run: RUN_INTEGRATION_TESTS=1 uv run pytest tests/commands/test_pdf_integration.py -v
        3. Verify PDF is created with correct content
        """
        with TemporaryDirectory() as tmpdir:
            _ = Path(tmpdir)

            # For manual testing, you would:
            # 1. Copy a real PPTX file to the temp directory
            # 2. Or create one programmatically using python-pptx
            # Example:
            # test_pptx = directory / "test.pptx"
            # shutil.copy("path/to/real/test.pptx", test_pptx)

            # For now, skip this test with a message
            self.skipTest(
                "Requires manual setup: copy a real PPTX file to test directory"
            )

            # Uncomment and modify once you have a real PPTX file:
            # result = export_pptx_to_pdf(test_pptx)
            # self.assertTrue(result, "Export should succeed")
            #
            # pdf_path = test_pptx.with_suffix(".pdf")
            # self.assertTrue(pdf_path.exists(), "PDF should be created")
            # self.assertGreater(pdf_path.stat().st_size, 0, "PDF should not be empty")

    def test_cmd_pdf_integration(self) -> None:
        """Test complete pdf command with real PowerPoint export.

        Manual testing recommended instead of automated test.
        See README for manual testing instructions.
        """
        with TemporaryDirectory() as tmpdir:
            _ = Path(tmpdir)

            # For manual testing:
            # 1. Create multiple PPTX files
            # 2. Run q4s pdf command
            # 3. Verify all PDFs are created

            self.skipTest("Requires manual testing with real PowerPoint")

            # Uncomment for manual testing:
            # old_stdout = sys.stdout
            # sys.stdout = StringIO()
            # try:
            #     result = cmd_pdf([str(directory)])
            #     output = sys.stdout.getvalue()
            #
            #     self.assertEqual(result, 0)
            #     self.assertIn("Exported", output)
            # finally:
            #     sys.stdout = old_stdout

    def test_powerpoint_not_installed(self) -> None:
        """Test error handling when PowerPoint is not available.

        This test can only run on systems without PowerPoint installed,
        or by temporarily renaming the PowerPoint app.
        """
        # This is difficult to test automatically
        self.skipTest("Cannot reliably test PowerPoint absence")


if __name__ == "__main__":
    unittest.main()
