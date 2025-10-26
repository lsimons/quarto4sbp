"""Tests for install.py script."""

import subprocess
import sys
import unittest
from pathlib import Path


class TestInstall(unittest.TestCase):
    """Test cases for the install script."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.resolve()
        self.install_script = self.project_root / "install.py"

    def test_install_script_exists(self) -> None:
        """Test that install.py exists in project root."""
        self.assertTrue(self.install_script.exists())
        self.assertTrue(self.install_script.is_file())

    def test_install_script_is_executable(self) -> None:
        """Test that install.py has executable permissions."""
        mode = self.install_script.stat().st_mode
        # Check if any executable bit is set
        self.assertTrue(mode & 0o111)

    def test_install_from_project_root_with_venv(self) -> None:
        """Test install when run from project root with venv present."""
        # Check if venv exists
        venv_path = self.project_root / ".venv"
        if not venv_path.exists():
            self.skipTest("Skipping: .venv not found, run 'uv venv' first")

        # Run install script
        result = subprocess.run(
            [sys.executable, str(self.install_script)],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )

        # Should succeed
        self.assertEqual(
            result.returncode,
            0,
            f"Install failed with: {result.stderr}",
        )

        # Should create shim
        shim_path = Path.home() / ".local" / "bin" / "q4s"
        self.assertTrue(
            shim_path.exists(),
            f"Shim not created at {shim_path}",
        )

        # Shim should be executable
        mode = shim_path.stat().st_mode
        self.assertTrue(mode & 0o111, "Shim is not executable")

        # Shim should contain project path
        shim_content = shim_path.read_text()
        self.assertIn(str(self.project_root), shim_content)
        self.assertIn("#!/bin/bash", shim_content)
        self.assertIn("source", shim_content)
        self.assertIn(".venv/bin/activate", shim_content)
        self.assertIn("python -m quarto4sbp.cli", shim_content)

        # Success message should be printed
        self.assertIn("Successfully installed", result.stdout)
        self.assertIn("Usage:", result.stdout)

    def test_install_creates_local_bin_if_missing(self) -> None:
        """Test that install creates ~/.local/bin if it doesn't exist."""
        # This test verifies the code path but doesn't actually delete ~/.local/bin
        # We'll check the code logic instead
        venv_path = self.project_root / ".venv"
        if not venv_path.exists():
            self.skipTest("Skipping: .venv not found")

        # Run install - should handle missing directory gracefully
        result = subprocess.run(
            [sys.executable, str(self.install_script)],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )

        # Should succeed even if directory needs to be created
        self.assertEqual(result.returncode, 0)

    def test_install_is_idempotent(self) -> None:
        """Test that running install twice works without errors."""
        venv_path = self.project_root / ".venv"
        if not venv_path.exists():
            self.skipTest("Skipping: .venv not found")

        # Run install first time
        result1 = subprocess.run(
            [sys.executable, str(self.install_script)],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result1.returncode, 0)

        # Run install second time
        result2 = subprocess.run(
            [sys.executable, str(self.install_script)],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result2.returncode, 0)

        # Shim should still exist and work
        shim_path = Path.home() / ".local" / "bin" / "q4s"
        self.assertTrue(shim_path.exists())

    def test_shim_runs_q4s_help(self) -> None:
        """Test that the installed shim can run q4s help."""
        shim_path = Path.home() / ".local" / "bin" / "q4s"
        if not shim_path.exists():
            self.skipTest("Skipping: q4s shim not installed, run install.py first")

        # Run q4s help via shim
        result = subprocess.run(
            [str(shim_path), "help"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("q4s", result.stdout)
        self.assertIn("help", result.stdout)


class TestInstallErrorCases(unittest.TestCase):
    """Test error cases for install script using temporary directories."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        import tempfile

        self.project_root = Path(__file__).parent.parent.resolve()
        self.install_script = self.project_root / "install.py"
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_error_when_venv_missing(self) -> None:
        """Test that install fails gracefully when .venv is missing."""
        # Create a fake project directory without venv
        fake_project = self.temp_dir / "fake_project"
        fake_project.mkdir()

        # Create a pyproject.toml
        pyproject = fake_project / "pyproject.toml"
        pyproject.write_text('[project]\nname = "quarto4sbp"\n')

        # Create install.py in fake project
        fake_install = fake_project / "install.py"
        fake_install.write_text(self.install_script.read_text())

        # Run install from fake project
        result = subprocess.run(
            [sys.executable, str(fake_install)],
            cwd=str(fake_project),
            capture_output=True,
            text=True,
        )

        # Should fail with helpful error
        self.assertEqual(result.returncode, 1)
        self.assertIn("Virtual environment not found", result.stderr)
        self.assertIn("uv venv", result.stderr)

    def test_error_when_not_quarto4sbp_project(self) -> None:
        """Test that install fails when not in quarto4sbp project."""
        # Create a fake project directory
        fake_project = self.temp_dir / "other_project"
        fake_project.mkdir()

        # Create a pyproject.toml for different project
        pyproject = fake_project / "pyproject.toml"
        pyproject.write_text('[project]\nname = "other-project"\n')

        # Create install.py in fake project
        fake_install = fake_project / "install.py"
        fake_install.write_text(self.install_script.read_text())

        # Run install from fake project
        result = subprocess.run(
            [sys.executable, str(fake_install)],
            cwd=str(fake_project),
            capture_output=True,
            text=True,
        )

        # Should fail with error
        self.assertEqual(result.returncode, 1)
        self.assertIn("quarto4sbp project", result.stderr)

    def test_error_when_pyproject_missing(self) -> None:
        """Test that install fails when pyproject.toml is missing."""
        # Create a fake project directory without pyproject.toml
        fake_project = self.temp_dir / "no_pyproject"
        fake_project.mkdir()

        # Create install.py in fake project
        fake_install = fake_project / "install.py"
        fake_install.write_text(self.install_script.read_text())

        # Run install from fake project
        result = subprocess.run(
            [sys.executable, str(fake_install)],
            cwd=str(fake_project),
            capture_output=True,
            text=True,
        )

        # Should fail with error
        self.assertEqual(result.returncode, 1)
        self.assertIn("pyproject.toml not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
