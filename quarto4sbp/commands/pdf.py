"""PDF command for q4s CLI."""

import shutil
import subprocess
import tempfile
from pathlib import Path


def find_stale_pptx(directory: Path) -> list[Path]:
    """Find PPTX files that need PDF export.

    A PPTX file needs export if:
    - No corresponding PDF exists, OR
    - The PPTX file is newer than the PDF file

    Excludes:
    - Symlinks
    - Files in 'templates' directory

    Args:
        directory: Directory to scan for PPTX files

    Returns:
        List of PPTX files that need PDF export
    """
    stale_files: list[Path] = []

    # Scan for PPTX files (non-recursive)
    for pptx_path in directory.glob("*.pptx"):
        # Skip symlinks
        if pptx_path.is_symlink():
            continue

        # Skip files in templates directory
        if pptx_path.parent.name == "templates":
            continue

        # Check if PDF exists and compare modification times
        pdf_path = pptx_path.with_suffix(".pdf")

        if not pdf_path.exists():
            # No PDF exists - needs export
            stale_files.append(pptx_path)
        else:
            # Compare modification times
            pptx_mtime = pptx_path.stat().st_mtime
            pdf_mtime = pdf_path.stat().st_mtime

            if pptx_mtime > pdf_mtime:
                # PPTX is newer - needs export
                stale_files.append(pptx_path)

    return stale_files


def create_temp_export_dir() -> Path:
    """Create a temporary directory for PowerPoint export.

    Returns:
        Path to temporary directory

    Raises:
        OSError: If temporary directory creation fails
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="q4s-pdf-"))
    return temp_dir


def prepare_file_for_export(pptx_path: Path, temp_dir: Path) -> tuple[Path, Path]:
    """Copy PPTX file to temporary directory for export.

    Args:
        pptx_path: Path to original PPTX file
        temp_dir: Temporary directory for export

    Returns:
        Tuple of (temp_pptx_path, temp_pdf_path) for export

    Raises:
        OSError: If file copy fails
    """
    temp_pptx = temp_dir / pptx_path.name
    shutil.copy2(pptx_path, temp_pptx)

    # Calculate where PDF will be created
    temp_pdf = temp_pptx.with_suffix(".pdf")

    return temp_pptx, temp_pdf


def copy_pdf_to_destination(temp_pdf: Path, dest_pdf: Path) -> None:
    """Copy exported PDF from temporary directory to destination.

    Args:
        temp_pdf: Path to PDF in temporary directory
        dest_pdf: Destination path for PDF

    Raises:
        OSError: If file copy fails
    """
    shutil.copy2(temp_pdf, dest_pdf)


def cleanup_temp_dir(temp_dir: Path) -> None:
    """Remove temporary directory and all its contents.

    Args:
        temp_dir: Temporary directory to remove
    """
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        # Best effort cleanup - don't fail if cleanup fails
        pass


def export_pptx_to_pdf(pptx_path: Path) -> bool:
    """Export a PPTX file to PDF using PowerPoint via AppleScript.

    This function handles the complete export workflow:
    1. Creates temporary directory for sandboxed PowerPoint
    2. Copies PPTX to temp directory
    3. Invokes PowerPoint via AppleScript to export PDF
    4. Copies PDF back to original location
    5. Cleans up temporary directory

    Args:
        pptx_path: Path to PPTX file to export

    Returns:
        True if export succeeded, False otherwise
    """
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = create_temp_export_dir()

        # Prepare file for export
        temp_pptx, temp_pdf = prepare_file_for_export(pptx_path, temp_dir)

        # Build AppleScript to export PDF
        applescript = f"""
tell application "Microsoft PowerPoint"
    open POSIX file "{temp_pptx}"
    set theDoc to active presentation
    save theDoc in POSIX file "{temp_pdf}" as save as PDF
    close theDoc
end tell
"""

        # Execute AppleScript
        _ = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check if PDF was created
        if not temp_pdf.exists():
            print(f"Error: PowerPoint did not create PDF for {pptx_path.name}")
            return False

        # Copy PDF to destination
        dest_pdf = pptx_path.with_suffix(".pdf")
        copy_pdf_to_destination(temp_pdf, dest_pdf)

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: AppleScript failed for {pptx_path.name}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False
    except OSError as e:
        print(f"Error: File operation failed for {pptx_path.name}: {e}")
        return False
    finally:
        # Always clean up temp directory
        if temp_dir:
            cleanup_temp_dir(temp_dir)


def cmd_pdf(args: list[str]) -> int:
    """Handle the pdf subcommand.

    Args:
        args: Optional directory argument (defaults to current directory)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Determine target directory
    if args:
        directory = Path(args[0])
        if not directory.exists():
            print(f"Error: Directory '{directory}' does not exist")
            return 1
        if not directory.is_dir():
            print(f"Error: '{directory}' is not a directory")
            return 1
    else:
        directory = Path.cwd()

    # Find stale PPTX files
    stale_pptx = find_stale_pptx(directory)

    if not stale_pptx:
        print("No PPTX files need exporting")
        return 0

    print(f"Found {len(stale_pptx)} file(s) to export:")
    for pptx_path in stale_pptx:
        print(f"  - {pptx_path.name}")

    # Export each file
    exported_count = 0
    skipped_count = 0

    for pptx_path in stale_pptx:
        print(f"Exporting: {pptx_path.name} -> {pptx_path.stem}.pdf")
        if export_pptx_to_pdf(pptx_path):
            exported_count += 1
        else:
            skipped_count += 1

    # Print summary
    print(f"\nExported {exported_count} file(s), skipped {skipped_count} file(s)")
    return 0
