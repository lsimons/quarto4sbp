"""File updater for safe backup and writing of QMD files.

This module handles creating backups and safely writing updated QMD content
while preserving file attributes and reporting changes.
"""

import shutil
from pathlib import Path
from typing import Optional, TypedDict


def create_backup(file_path: Path, backup_suffix: str = ".bak") -> Path:
    """Create a backup of the file.

    Args:
        file_path: Path to the file to backup
        backup_suffix: Suffix for backup file (default: .bak)

    Returns:
        Path to the created backup file

    Raises:
        IOError: If backup creation fails
    """
    backup_path = Path(str(file_path) + backup_suffix)

    # Copy file preserving metadata
    shutil.copy2(file_path, backup_path)

    return backup_path


class UpdateResult(TypedDict):
    """Result from update_file operation."""

    backup_path: Optional[Path]
    original_size: int
    new_size: int
    lines_changed: int


def update_file(
    file_path: Path,
    new_content: str,
    create_backup_file: bool = True,
    backup_suffix: str = ".bak",
) -> UpdateResult:
    """Update a file with new content, optionally creating a backup.

    Args:
        file_path: Path to the file to update
        new_content: New content to write
        create_backup_file: Whether to create a backup (default: True)
        backup_suffix: Suffix for backup file (default: .bak)

    Returns:
        UpdateResult with update information:
            - backup_path: Path to backup file (if created, else None)
            - original_size: Original file size in bytes
            - new_size: New file size in bytes
            - lines_changed: Estimated number of lines changed

    Raises:
        IOError: If file operations fail
    """
    # Verify file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read original content for comparison
    original_content = file_path.read_text()
    original_size = len(original_content)
    new_size = len(new_content)

    # Estimate lines changed (simple diff count)
    original_lines = original_content.splitlines()
    new_lines = new_content.splitlines()
    lines_changed = sum(1 for old, new in zip(original_lines, new_lines) if old != new)
    # Add lines added or removed
    lines_changed += abs(len(original_lines) - len(new_lines))

    # Create backup if requested
    backup_path: Optional[Path] = None
    if create_backup_file:
        backup_path = create_backup(file_path, backup_suffix)

    # Write new content
    try:
        file_path.write_text(new_content)
    except Exception as e:
        # If write failed and we created a backup, restore it
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, file_path)
        raise IOError(f"Failed to write file: {e}") from e

    return UpdateResult(
        backup_path=backup_path,
        original_size=original_size,
        new_size=new_size,
        lines_changed=lines_changed,
    )
