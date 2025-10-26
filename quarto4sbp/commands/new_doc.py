"""Command to create a new Quarto Word document from template."""

import os
import sys
from pathlib import Path


def cmd_new_doc(args: list[str]) -> int:
    """Create a new Quarto Word document from template.

    Args:
        args: Command-line arguments (should contain directory name)

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    if len(args) == 0:
        print("Error: Directory name required", file=sys.stderr)
        print("Usage: q4s new-doc <directory>", file=sys.stderr)
        return 1

    dir_name = args[0]

    # Validate directory name
    if not dir_name or dir_name.startswith("-"):
        print(f"Error: Invalid directory name '{dir_name}'", file=sys.stderr)
        return 1

    # Get paths
    target_dir = Path(dir_name)
    # Use base name (last component) for the qmd filename
    base_name = target_dir.name
    qmd_file = target_dir / f"{base_name}.qmd"
    symlink_target = target_dir / "simple-document.docx"
    render_script = target_dir / "render.sh"

    # Find the templates directory relative to this file
    # quarto4sbp/commands/new_doc.py -> quarto4sbp -> project root -> templates
    project_root = Path(__file__).parent.parent.parent
    template_qmd = project_root / "templates" / "simple-document.qmd"
    template_docx = project_root / "templates" / "simple-document.docx"
    template_render = project_root / "templates" / "render.sh.template"

    # Verify template exists
    if not template_qmd.exists():
        print(f"Error: Template not found at {template_qmd}", file=sys.stderr)
        return 1

    if not template_docx.exists():
        print(f"Error: Word template not found at {template_docx}", file=sys.stderr)
        return 1

    if not template_render.exists():
        print(
            f"Error: Render script template not found at {template_render}",
            file=sys.stderr,
        )
        return 1

    # Check if qmd file already exists
    if qmd_file.exists():
        print(f"Error: File already exists: {qmd_file}", file=sys.stderr)
        return 1

    # Create directory if it doesn't exist
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create directory '{target_dir}': {e}", file=sys.stderr)
        return 1

    # Copy template content to new qmd file
    try:
        content = template_qmd.read_text()
        qmd_file.write_text(content)
    except OSError as e:
        print(f"Error: Could not create file '{qmd_file}': {e}", file=sys.stderr)
        return 1

    # Create render.sh script from template
    try:
        render_content = template_render.read_text()
        # Replace placeholder with actual file name
        render_content = render_content.replace("{{FILE_NAME}}", base_name)
        render_script.write_text(render_content)
        # Make it executable
        render_script.chmod(0o755)
    except OSError as e:
        print(
            f"Error: Could not create render script '{render_script}': {e}",
            file=sys.stderr,
        )
        return 1

    # Create symlink to Word template
    # Use relative path from target_dir to templates/simple-document.docx
    try:
        # Calculate relative path from target_dir to template_docx
        rel_path = os.path.relpath(template_docx, target_dir)
        symlink_target.symlink_to(rel_path)
    except OSError as e:
        # On Windows, symlinks may fail without admin/developer mode
        # Print warning but don't fail the command
        print(f"Warning: Could not create symlink: {e}", file=sys.stderr)
        print(
            f"You may need to manually copy or link to {template_docx}", file=sys.stderr
        )

    # Success output
    print(f"Created: {qmd_file}")
    print(f"Hint: Run 'cd {target_dir} && ./render.sh' to generate the document")

    return 0
