# 000 - Shared Patterns Reference

This document contains templates and boilerplate code that specs can reference to avoid repetition. For architectural decisions, see [DESIGN.md](../../DESIGN.md).

## Spec Template

Standard template for new specification documents:

```markdown
# XXX - Feature Name

**Purpose:** One-line description of what this does and why

**Requirements:**
- Key functional requirement 1
- Key functional requirement 2
- Important constraints or non-functional requirements

**Design Approach:**
- High-level design decision 1
- High-level design decision 2
- Key technical choices and rationale

**Implementation Notes:**
- Critical implementation details only
- Dependencies or special considerations
- Integration points with existing code

**Status:** [Draft/Approved/Implemented]
```

## Common Command Patterns

### CLI Command Function Signature
```python
def cmd_<command_name>(args: list[str]) -> int:
    """Handle <command-name> subcommand.
    
    Args:
        args: Command-line arguments
        
    Returns:
        0 on success, 1 on error
    """
```

### CLI Integration Pattern
Add to `quarto4sbp/cli.py`:
```python
elif command == "command-name":
    from quarto4sbp.commands.command_name import cmd_command_name
    return cmd_command_name(args[1:])
```

Add to `quarto4sbp/commands/__init__.py`:
```python
from quarto4sbp.commands.command_name import cmd_command_name
```

### Standard Error Handling
- Return exit code 0 on success, 1 on error
- Print clear error messages to stderr
- Continue processing other items when one fails (where appropriate)
- Graceful degradation when external tools unavailable

## Template Creation Commands

### Standard Template Command Structure
Commands that create from templates follow this pattern:

1. Validate directory argument provided
2. Create directory if doesn't exist
3. Copy/generate `.qmd` file from template
4. Create symlinks to reference documents
5. Generate `render.sh` script from template
6. Make scripts executable
7. Print creation confirmation and usage hint

### Template Directory Structure
```
<directory>/
  <directory>.qmd           # Source file (same name as directory)
  reference-doc.{pptx,docx} # Symlink to ../templates/reference-doc.*
  render.sh                 # Generated render script
```

### Render Script Template Pattern
```bash
#!/bin/sh
# Render Quarto file and export to PDF
set -e

FILE_NAME="{{FILE_NAME}}"

echo "Rendering ${FILE_NAME}.qmd..."
quarto render "${FILE_NAME}.qmd"

if [ $? -eq 0 ]; then
    echo "✓ Successfully rendered ${FILE_NAME}.qmd"
    echo "Exporting to PDF..."
    q4s pdf
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully exported to PDF"
        echo ""
        echo "Output files created in current directory"
    else
        echo "✗ PDF export failed"
        exit 1
    fi
else
    echo "✗ Rendering failed"
    exit 1
fi
```

## PDF Export Commands

### Standard PDF Export Pattern
Commands that export Office files to PDF follow this pattern:

1. **Find files:** Scan directory for `.{pptx,docx}` files
2. **Filter:** Exclude symlinks and template files
3. **Check staleness:** Compare modification times
4. **Export:** Use AppleScript to invoke Office application
5. **Report:** Print summary of exported/skipped files

### File Staleness Detection
```python
def find_stale_<format>(directory: Path) -> list[Path]:
    """Find files needing PDF export.
    
    Returns files where:
    - Corresponding PDF doesn't exist, OR
    - Source file is newer than PDF
    
    Excludes:
    - Symlinks
    - Files in templates/ directory
    """
```

### AppleScript Export Pattern (PowerPoint)
```applescript
tell application "Microsoft PowerPoint"
    open POSIX file "/full/path/to/file.pptx"
    set theDoc to active presentation
    save theDoc in POSIX file "/full/path/to/file.pdf" as save as PDF
    close theDoc
end tell
```

### AppleScript Export Pattern (Word)
```applescript
tell application "Microsoft Word"
    open POSIX file "/full/path/to/file.docx"
    set theDoc to active document
    save as theDoc file name POSIX file "/full/path/to/file.pdf" file format format PDF
    close theDoc saving no
end tell
```

### PDF Export Function Pattern
```python
def export_<format>_to_pdf(<format>_path: Path) -> bool:
    """Export single file to PDF via AppleScript.
    
    Args:
        <format>_path: Path to source file
        
    Returns:
        True on success, False on failure
    """
    pdf_path = Path(str(<format>_path) + ".pdf")
    # Use subprocess.run(['osascript', '-e', script])
    # Handle CalledProcessError gracefully
```

## Testing Patterns

### Standard Test Structure
```python
# tests/commands/test_<command>.py
import unittest
from pathlib import Path
from quarto4sbp.commands.<command> import cmd_<command>

class Test<Command>(unittest.TestCase):
    def setUp(self):
        # Create temporary directory
        pass
        
    def tearDown(self):
        # Clean up temporary directory
        pass
        
    def test_success_case(self):
        # Test successful execution
        pass
        
    def test_error_case(self):
        # Test error handling
        pass
```

### Integration Test Pattern
```python
@unittest.skipUnless(
    os.environ.get('RUN_INTEGRATION_TESTS') == '1',
    "Integration tests skipped (set RUN_INTEGRATION_TESTS=1 to run)"
)
class TestIntegration(unittest.TestCase):
    # Tests that require external applications
    pass
```

## Quarto Template Patterns

### PowerPoint QMD Template
```yaml
---
title: "{{TITLE}}"
format:
  pptx:
    reference-doc: simple-presentation.pptx
---
```

### Word QMD Template
```yaml
---
title: "{{TITLE}}"
format:
  docx:
    reference-doc: simple-document.docx
    toc: true
    number-sections: true
---
```

### Multi-Format QMD Template
```yaml
---
title: "{{TITLE}}"
format:
  pptx:
    reference-doc: simple-presentation.pptx
  docx:
    reference-doc: simple-document.docx
    toc: true
    number-sections: true
---
```

## File Naming Conventions

### Command Files
- Format-specific commands: `<command>_<format>.py` (e.g., `new_pptx.py`, `pdf_docx.py`)
- Unified commands: `<command>.py` (e.g., `new.py`, `pdf.py`)
- Function names match filenames: `cmd_<command>_<format>()` or `cmd_<command>()`

### Template Files
- PowerPoint: `simple-presentation.{qmd,pptx}`
- Word: `simple-document.{qmd,docx}`
- Render scripts: `render.sh.template`

### Output Files
- Double extension for PDFs: `file.pptx.pdf`, `file.docx.pdf`
- Preserves provenance and prevents conflicts

## Dependency-Free Philosophy

All core commands use only Python standard library:
- `pathlib` - Path manipulation
- `subprocess` - External process execution
- `os`, `sys` - System operations
- `argparse` - CLI parsing (main entry point only)

External dependencies only for:
- Testing: `pytest`
- Type checking: `pyright`
- Development: `uv` (not runtime)

## Status Tracking

Specs progress through these states:
- **Draft** - Initial design, under discussion
- **Approved** - Design reviewed and approved
- **Implemented** - Code written and tests passing