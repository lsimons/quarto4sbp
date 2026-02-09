"""Tone of voice command for rewriting QMD files.

This command rewrites .qmd file content to match company tone of voice
guidelines using LLM, while preserving structure, YAML frontmatter, and code blocks.
"""

import sys
from pathlib import Path

from quarto4sbp.llm.client import LLMClient
from quarto4sbp.tov.parser import parse_qmd, reconstruct_qmd
from quarto4sbp.tov.rewriter import rewrite_content
from quarto4sbp.tov.updater import update_file


def show_diff(original: str, rewritten: str, file_path: Path) -> None:
    """Show a simple before/after comparison.

    Args:
        original: Original content
        rewritten: Rewritten content
        file_path: Path to the file being processed
    """
    print(f"\n{'=' * 60}")
    print(f"Changes for: {file_path}")
    print(f"{'=' * 60}")

    orig_lines = original.splitlines()
    new_lines = rewritten.splitlines()

    # Show line count changes
    print(f"Original: {len(orig_lines)} lines")
    print(f"Rewritten: {len(new_lines)} lines")
    print(f"Difference: {len(new_lines) - len(orig_lines):+d} lines")
    print()

    # Show first few changed sections for preview
    print("Preview of changes:")
    print("-" * 60)
    changes_shown = 0
    for i, (old, new) in enumerate(zip(orig_lines, new_lines, strict=False)):
        if old != new and changes_shown < 10:
            print(f"Line {i + 1}:")
            print(f"  - {old[:70]}")
            print(f"  + {new[:70]}")
            changes_shown += 1

    if changes_shown == 10:
        print("... (additional changes not shown)")

    print(f"{'=' * 60}\n")


def process_file(
    file_path: Path,
    dry_run: bool = False,
    no_backup: bool = False,
) -> bool:
    """Process a single QMD file.

    Args:
        file_path: Path to the .qmd file
        dry_run: If True, show changes without modifying file
        no_backup: If True, don't create backup file

    Returns:
        True on success, False on failure
    """
    print(f"Processing: {file_path}")

    try:
        # Read and parse file
        content = file_path.read_text()
        doc = parse_qmd(content)

        print(f"  Found {len(doc.sections)} section(s) to rewrite")

        if not doc.sections:
            print("  No content to rewrite (file may be empty or only contain YAML)")
            return True

        # Create LLM client
        try:
            client = LLMClient()
        except ValueError as e:
            print(f"  ✗ LLM configuration error: {e}", file=sys.stderr)
            print("  Hint: Set OPENAI_API_KEY environment variable", file=sys.stderr)
            return False

        # Rewrite sections with progress
        def progress(current: int, total: int) -> None:
            print(f"  Rewriting section {current}/{total}...")

        rewritten_sections = rewrite_content(
            doc.sections, client=client, progress_callback=progress
        )

        # Reconstruct file
        rewritten_content = reconstruct_qmd(doc, rewritten_sections)

        # Dry run: show diff and exit
        if dry_run:
            show_diff(content, rewritten_content, file_path)
            print("  [DRY RUN] File not modified")
            return True

        # Update file
        result = update_file(
            file_path, rewritten_content, create_backup_file=not no_backup
        )

        # Report results
        print("  ✓ File updated successfully")
        if result["backup_path"]:
            print(f"  Backup created: {result['backup_path']}")
        print(f"  Lines changed: {result['lines_changed']}")

        return True

    except FileNotFoundError:
        print(f"  ✗ File not found: {file_path}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ✗ Error processing file: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return False


def cmd_tov(args: list[str]) -> int:
    """Handle tov subcommand for tone of voice rewriting.

    Args:
        args: Command-line arguments

    Returns:
        0 on success, 1 on error
    """
    # Parse arguments
    if not args:
        print("Usage: q4s tov <file.qmd> [--dry-run] [--no-backup]", file=sys.stderr)
        print("       q4s tov <directory> [--dry-run] [--no-backup]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Rewrite .qmd files to match company tone of voice.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print(
            "  --dry-run     Preview changes without modifying files", file=sys.stderr
        )
        print("  --no-backup   Don't create .bak backup files", file=sys.stderr)
        return 1

    # Extract path and flags
    path_arg: str | None = None
    dry_run = False
    no_backup = False

    for arg in args:
        if arg == "--dry-run":
            dry_run = True
        elif arg == "--no-backup":
            no_backup = True
        elif not arg.startswith("-"):
            path_arg = arg

    if not path_arg:
        print("Error: No file or directory specified", file=sys.stderr)
        return 1

    target_path = Path(path_arg)

    if not target_path.exists():
        print(f"Error: Path not found: {target_path}", file=sys.stderr)
        return 1

    # Process file or directory
    files_to_process: list[Path] = []

    if target_path.is_file():
        if target_path.suffix != ".qmd":
            print(f"Warning: {target_path} is not a .qmd file", file=sys.stderr)
        files_to_process.append(target_path)
    elif target_path.is_dir():
        # Find all .qmd files in directory
        files_to_process = list(target_path.glob("*.qmd"))
        files_to_process.extend(target_path.glob("**/*.qmd"))
        # Remove duplicates and sort
        files_to_process = sorted(set(files_to_process))

        if not files_to_process:
            print(f"No .qmd files found in: {target_path}", file=sys.stderr)
            return 1

        print(f"Found {len(files_to_process)} .qmd file(s) to process")
    else:
        print(f"Error: {target_path} is not a file or directory", file=sys.stderr)
        return 1

    # Process all files
    success_count = 0
    for file_path in files_to_process:
        if process_file(file_path, dry_run=dry_run, no_backup=no_backup):
            success_count += 1
        print()  # Blank line between files

    # Summary
    total = len(files_to_process)
    print(f"Processed {success_count}/{total} file(s) successfully")

    return 0 if success_count == total else 1
