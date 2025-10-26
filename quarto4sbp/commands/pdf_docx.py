"""PDF export command for Word documents."""

import subprocess
from pathlib import Path


def find_stale_docx(directory: Path) -> list[Path]:
    """Find DOCX files that need PDF export.

    A DOCX file needs export if:
    - No corresponding PDF exists, OR
    - The DOCX file is newer than the PDF file

    Excludes:
    - Symlinks
    - Files in 'templates' directory

    Args:
        directory: Directory to scan for DOCX files

    Returns:
        List of DOCX files that need PDF export
    """
    stale_files: list[Path] = []

    # Scan for DOCX files (non-recursive)
    for docx_path in directory.glob("*.docx"):
        # Skip symlinks
        if docx_path.is_symlink():
            continue

        # Skip files in templates directory
        if docx_path.parent.name == "templates":
            continue

        # Check if PDF exists and compare modification times
        pdf_path = docx_path.with_suffix(".pdf")

        if not pdf_path.exists():
            # No PDF exists - needs export
            stale_files.append(docx_path)
        else:
            # Compare modification times
            docx_mtime = docx_path.stat().st_mtime
            pdf_mtime = pdf_path.stat().st_mtime

            if docx_mtime > pdf_mtime:
                # DOCX is newer - needs export
                stale_files.append(docx_path)

    return stale_files


def export_docx_to_pdf(docx_path: Path) -> bool:
    """Export a DOCX file to PDF using Word via AppleScript.

    Exports directly in the current directory where the DOCX file is located.

    Args:
        docx_path: Path to DOCX file to export

    Returns:
        True if export succeeded, False otherwise
    """
    try:
        # Calculate PDF path
        pdf_path = docx_path.with_suffix(".pdf")

        # Build AppleScript to export PDF
        applescript = f"""
tell application "Microsoft Word"
    open POSIX file "{docx_path.resolve()}"
    set theDoc to active document
    save as theDoc file name POSIX file "{pdf_path.resolve()}" file format format PDF
    close theDoc saving no
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
            print(f"Error: Word did not create PDF for {docx_path.name}")
            return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: AppleScript failed for {docx_path.name}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False
    except OSError as e:
        print(f"Error: File operation failed for {docx_path.name}: {e}")
        return False


def cmd_pdf_docx(args: list[str]) -> int:
    """Handle the pdf-docx subcommand.

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

    # Find stale DOCX files
    stale_docx = find_stale_docx(directory)

    if not stale_docx:
        print("No DOCX files need exporting")
        return 0

    print(f"Found {len(stale_docx)} file(s) to export:")
    for docx_path in stale_docx:
        print(f"  - {docx_path.name}")

    # Export each file
    exported_count = 0
    skipped_count = 0

    for docx_path in stale_docx:
        print(f"Exporting: {docx_path.name} -> {docx_path.stem}.pdf")
        if export_docx_to_pdf(docx_path):
            exported_count += 1
        else:
            skipped_count += 1

    # Print summary
    print(f"\nExported {exported_count} file(s), skipped {skipped_count} file(s)")
    return 0
