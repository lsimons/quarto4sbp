"""Unified new command for creating documents with both PowerPoint and Word outputs."""

import os
import sys
from pathlib import Path


def cmd_new(args: list[str]) -> int:
    """Create a new Quarto document with both PowerPoint and Word outputs.

    Creates a single .qmd file configured to output to both .pptx and .docx formats.

    Args:
        args: Command-line arguments (should contain directory name)

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    if len(args) == 0:
        print("Error: Directory name required", file=sys.stderr)
        print("Usage: q4s new <directory>", file=sys.stderr)
        return 1

    dir_name = args[0]

    # Validate directory name
    if not dir_name or dir_name.startswith("-"):
        print(f"Error: Invalid directory name '{dir_name}'", file=sys.stderr)
        return 1

    # Get paths
    target_dir = Path(dir_name)
    base_name = target_dir.name
    qmd_file = target_dir / f"{base_name}.qmd"
    pptx_symlink = target_dir / "simple-presentation.pptx"
    docx_symlink = target_dir / "simple-document.docx"
    render_script = target_dir / "render.sh"

    # Find the templates directory
    project_root = Path(__file__).parent.parent.parent
    template_pptx = project_root / "templates" / "simple-presentation.pptx"
    template_docx = project_root / "templates" / "simple-document.docx"
    template_render = project_root / "templates" / "render.sh.template"

    # Verify templates exist
    if not template_pptx.exists():
        print(
            f"Error: PowerPoint template not found at {template_pptx}",
            file=sys.stderr,
        )
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

    # Create QMD content with both output formats
    qmd_content = f"""---
title: "{base_name}"
format:
  pptx:
    reference-doc: simple-presentation.pptx
  docx:
    reference-doc: simple-document.docx
    toc: true
    number-sections: true
---

## Introduction

This is a sample document that outputs to both PowerPoint and Word formats.

## Key Points

- Edit this `.qmd` file with your content
- Run `./render.sh` to generate both `.pptx` and `.docx` files
- The unified `q4s pdf` command will export both to PDF

## Code Example

```python
def hello():
    print("Hello, world!")
```

## Conclusion

- Quarto makes it easy to create multiple output formats
- Single source, multiple outputs
"""

    # Write QMD file
    try:
        qmd_file.write_text(qmd_content)
    except OSError as e:
        print(f"Error: Could not create file '{qmd_file}': {e}", file=sys.stderr)
        return 1

    # Create render.sh script from template
    try:
        render_content = template_render.read_text()
        render_content = render_content.replace("{{FILE_NAME}}", base_name)
        render_script.write_text(render_content)
        render_script.chmod(0o755)
    except OSError as e:
        print(
            f"Error: Could not create render script '{render_script}': {e}",
            file=sys.stderr,
        )
        return 1

    # Create symlinks to both templates
    created_symlinks = []
    failed_symlinks = []

    # PowerPoint symlink
    try:
        rel_path_pptx = os.path.relpath(template_pptx, target_dir)
        pptx_symlink.symlink_to(rel_path_pptx)
        created_symlinks.append("PowerPoint")
    except OSError as e:
        failed_symlinks.append(("PowerPoint", template_pptx, e))

    # Word symlink
    try:
        rel_path_docx = os.path.relpath(template_docx, target_dir)
        docx_symlink.symlink_to(rel_path_docx)
        created_symlinks.append("Word")
    except OSError as e:
        failed_symlinks.append(("Word", template_docx, e))

    # Print warnings for failed symlinks (non-fatal)
    if failed_symlinks:
        for format_name, template_path, error in failed_symlinks:
            print(
                f"Warning: Could not create {format_name} symlink: {error}",
                file=sys.stderr,
            )
            print(
                f"You may need to manually copy or link to {template_path}",
                file=sys.stderr,
            )

    # Success output
    print(f"Created: {qmd_file}")
    print(f"Outputs: Both PowerPoint (.pptx) and Word (.docx)")
    print(f"Hint: Run 'cd {target_dir} && ./render.sh' to generate both formats")

    return 0
