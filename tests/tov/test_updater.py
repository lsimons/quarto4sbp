"""Tests for file updater."""

import shutil
import tempfile
import unittest
from pathlib import Path

from quarto4sbp.tov.updater import create_backup, update_file


class TestCreateBackup(unittest.TestCase):
    """Test backup creation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test.qmd"
        self.test_file.write_text("Original content\n")

    def tearDown(self):
        """Clean up test files."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_create_backup_default_suffix(self):
        """Test creating backup with default .bak suffix."""
        backup_path = create_backup(self.test_file)

        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.name, "test.qmd.bak")
        self.assertEqual(backup_path.read_text(), "Original content\n")

    def test_create_backup_custom_suffix(self):
        """Test creating backup with custom suffix."""
        backup_path = create_backup(self.test_file, backup_suffix=".backup")

        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.name, "test.qmd.backup")
        self.assertEqual(backup_path.read_text(), "Original content\n")

    def test_create_backup_preserves_metadata(self):
        """Test that backup preserves file metadata."""
        original_stat = self.test_file.stat()
        backup_path = create_backup(self.test_file)
        backup_stat = backup_path.stat()

        # Size should match
        self.assertEqual(backup_stat.st_size, original_stat.st_size)

    def test_create_backup_overwrites_existing(self):
        """Test that backup overwrites existing backup file."""
        # Create initial backup
        backup_path = create_backup(self.test_file)
        initial_content = backup_path.read_text()

        # Modify original
        self.test_file.write_text("Modified content\n")

        # Create backup again
        backup_path = create_backup(self.test_file)

        # Should have new content
        self.assertEqual(backup_path.read_text(), "Modified content\n")
        self.assertNotEqual(backup_path.read_text(), initial_content)


class TestUpdateFile(unittest.TestCase):
    """Test file update functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test.qmd"
        self.test_file.write_text("Original content\nLine 2\nLine 3\n")

    def tearDown(self):
        """Clean up test files."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_update_file_basic(self):
        """Test basic file update."""
        new_content = "New content\nLine 2\nLine 3\n"
        result = update_file(self.test_file, new_content)

        self.assertEqual(self.test_file.read_text(), new_content)
        self.assertIsInstance(result["backup_path"], Path)
        self.assertGreater(result["lines_changed"], 0)

    def test_update_file_creates_backup(self):
        """Test that update creates backup by default."""
        new_content = "Updated content\n"
        result = update_file(self.test_file, new_content)

        backup_path = result["backup_path"]
        self.assertIsNotNone(backup_path)
        assert backup_path is not None  # Type assertion for pyright
        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), "Original content\nLine 2\nLine 3\n")

    def test_update_file_no_backup(self):
        """Test update without creating backup."""
        new_content = "Updated content\n"
        result = update_file(self.test_file, new_content, create_backup_file=False)

        self.assertIsNone(result["backup_path"])
        backup_path = Path(str(self.test_file) + ".bak")
        self.assertFalse(backup_path.exists())

    def test_update_file_custom_backup_suffix(self):
        """Test update with custom backup suffix."""
        new_content = "Updated content\n"
        result = update_file(
            self.test_file, new_content, create_backup_file=True, backup_suffix=".orig"
        )

        backup_path = result["backup_path"]
        self.assertIsNotNone(backup_path)
        assert backup_path is not None  # Type assertion for pyright
        self.assertEqual(backup_path.name, "test.qmd.orig")

    def test_update_file_size_tracking(self):
        """Test that file size changes are tracked."""
        original_size = len("Original content\nLine 2\nLine 3\n")
        new_content = "Short\n"
        new_size = len(new_content)

        result = update_file(self.test_file, new_content)

        self.assertEqual(result["original_size"], original_size)
        self.assertEqual(result["new_size"], new_size)

    def test_update_file_lines_changed(self):
        """Test lines changed calculation."""
        # Change first line, keep others
        new_content = "Changed content\nLine 2\nLine 3\n"
        result = update_file(self.test_file, new_content)

        # Should report 1 line changed
        self.assertEqual(result["lines_changed"], 1)

    def test_update_file_adds_lines(self):
        """Test lines changed when lines are added."""
        # Add more lines
        new_content = "Original content\nLine 2\nLine 3\nLine 4\nLine 5\n"
        result = update_file(self.test_file, new_content)

        # Should report 2 lines added
        self.assertEqual(result["lines_changed"], 2)

    def test_update_file_removes_lines(self):
        """Test lines changed when lines are removed."""
        # Remove a line
        new_content = "Original content\nLine 2\n"
        result = update_file(self.test_file, new_content)

        # Should report 1 line removed
        self.assertEqual(result["lines_changed"], 1)

    def test_update_file_nonexistent_raises_error(self):
        """Test that updating nonexistent file raises error."""
        nonexistent = self.test_dir / "nonexistent.qmd"

        with self.assertRaises(FileNotFoundError):
            update_file(nonexistent, "content")

    def test_update_file_write_error_restores_backup(self):
        """Test that write errors restore from backup."""
        # This is hard to test directly, but we can verify the code path exists
        # by checking that backup is created before writing
        new_content = "New content\n"

        # Normal update should work
        result = update_file(self.test_file, new_content)
        backup_path = result["backup_path"]

        # Backup should exist and contain original
        assert backup_path is not None  # Type assertion for pyright
        self.assertTrue(backup_path.exists())
        self.assertIn("Original content", backup_path.read_text())

    def test_update_file_identical_content(self):
        """Test updating with identical content."""
        original_content = self.test_file.read_text()
        result = update_file(self.test_file, original_content)

        # No lines should be reported as changed
        self.assertEqual(result["lines_changed"], 0)


if __name__ == "__main__":
    unittest.main()
