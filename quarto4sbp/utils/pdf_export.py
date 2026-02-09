"""Utilities for exporting Office documents to PDF via AppleScript."""

import subprocess
from collections.abc import Callable
from pathlib import Path


def find_stale_files(directory: Path, extension: str) -> list[Path]:
    """Find files that need PDF export.

    A file needs export if:
    - No corresponding PDF exists, OR
    - The source file is newer than the PDF file

    Excludes:
    - Symlinks
    - Files in 'templates' directory

    Args:
        directory: Directory to scan for files
        extension: File extension to search for (e.g., "pptx", "docx")

    Returns:
        List of files that need PDF export
    """
    stale_files: list[Path] = []

    # Scan for files with specified extension (non-recursive)
    for source_path in directory.glob(f"*.{extension}"):
        # Skip symlinks
        if source_path.is_symlink():
            continue

        # Skip files in templates directory
        if source_path.parent.name == "templates":
            continue

        # Check if PDF exists and compare modification times
        # Use double extension to preserve source format
        pdf_path = Path(str(source_path) + ".pdf")

        if not pdf_path.exists():
            # No PDF exists - needs export
            stale_files.append(source_path)
        else:
            # Compare modification times
            source_mtime = source_path.stat().st_mtime
            pdf_mtime = pdf_path.stat().st_mtime

            if source_mtime > pdf_mtime:
                # Source is newer - needs export
                stale_files.append(source_path)

    return stale_files


def export_to_pdf_via_applescript(
    source_path: Path, applescript: str, app_name: str
) -> bool:
    """Export a file to PDF using an Office app via AppleScript.

    Args:
        source_path: Path to source file to export
        applescript: AppleScript code to execute
        app_name: Name of the app for error messages (e.g., "PowerPoint", "Word")

    Returns:
        True if export succeeded, False otherwise
    """
    try:
        # Calculate PDF path using double extension
        pdf_path = Path(str(source_path) + ".pdf")

        # Execute AppleScript
        _ = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check if PDF was created
        if not pdf_path.exists():
            print(f"Error: {app_name} did not create PDF for {source_path.name}")
            return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: AppleScript failed for {source_path.name}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False
    except OSError as e:
        print(f"Error: File operation failed for {source_path.name}: {e}")
        return False


def validate_directory(args: list[str]) -> Path | None:
    """Validate and return the target directory from command arguments.

    Args:
        args: Command-line arguments (optional directory path)

    Returns:
        Path object if valid, None otherwise (prints error message)
    """
    if args:
        directory = Path(args[0])
        if not directory.exists():
            print(f"Error: Directory '{directory}' does not exist")
            return None
        if not directory.is_dir():
            print(f"Error: '{directory}' is not a directory")
            return None
        return directory
    else:
        return Path.cwd()


def process_files(
    stale_files: list[Path], export_func: Callable[[Path], bool], file_type: str
) -> int:
    """Process a list of files for PDF export.

    Args:
        stale_files: List of files to export
        export_func: Function to call for each file (returns bool)
        file_type: Human-readable file type for messages (e.g., "PPTX", "DOCX")

    Returns:
        Exit code (0 for success)
    """
    if not stale_files:
        print(f"No {file_type} files need exporting")
        return 0

    print(f"Found {len(stale_files)} file(s) to export:")
    for file_path in stale_files:
        print(f"  - {file_path.name}")

    # Export each file
    exported_count = 0
    skipped_count = 0

    for file_path in stale_files:
        print(f"Exporting: {file_path.name} -> {file_path.name}.pdf")
        if export_func(file_path):
            exported_count += 1
        else:
            skipped_count += 1

    # Print summary
    print(f"\nExported {exported_count} file(s), skipped {skipped_count} file(s)")
    return 0
