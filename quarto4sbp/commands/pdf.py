"""PDF command for q4s CLI."""

import shutil
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

    # TODO: Implement actual PDF export
    print("\nPDF export not yet implemented")
    return 0
