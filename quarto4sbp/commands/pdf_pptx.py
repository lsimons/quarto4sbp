"""PDF export command for PowerPoint files."""

import subprocess
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
        # Use double extension to preserve source format
        pdf_path = Path(str(pptx_path) + ".pdf")

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


def export_pptx_to_pdf(pptx_path: Path) -> bool:
    """Export a PPTX file to PDF using PowerPoint via AppleScript.

    Exports directly in the current directory where the PPTX file is located.

    Args:
        pptx_path: Path to PPTX file to export

    Returns:
        True if export succeeded, False otherwise
    """
    try:
        # Calculate PDF path
        # Use double extension to preserve source format
        pdf_path = Path(str(pptx_path) + ".pdf")

        # Build AppleScript to export PDF
        applescript = f"""
tell application "Microsoft PowerPoint"
    open POSIX file "{pptx_path.resolve()}"
    set theDoc to active presentation
    save theDoc in POSIX file "{pdf_path.resolve()}" as save as PDF
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
        if not pdf_path.exists():
            print(f"Error: PowerPoint did not create PDF for {pptx_path.name}")
            return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: AppleScript failed for {pptx_path.name}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False
    except OSError as e:
        print(f"Error: File operation failed for {pptx_path.name}: {e}")
        return False


def cmd_pdf_pptx(args: list[str]) -> int:
    """Handle the pdf-pptx subcommand.

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
        print(f"Exporting: {pptx_path.name} -> {pptx_path.name}.pdf")
        if export_pptx_to_pdf(pptx_path):
            exported_count += 1
        else:
            skipped_count += 1

    # Print summary
    print(f"\nExported {exported_count} file(s), skipped {skipped_count} file(s)")
    return 0
