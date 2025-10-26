# 008 - Unified New Command

**Purpose:** Add a unified `new` command that creates a single Quarto document configured to output to both PowerPoint (.pptx) and Word (.docx) formats

**Related Issues:** q4s-41

**Requirements:**
- `q4s new <directory>` command to create a document with both PPTX and DOCX outputs
- Single `.qmd` file with multiple output formats in YAML frontmatter
- Symlinks to both PowerPoint and Word templates
- Unified render script that generates both formats
- Similar to `pdf` unified command pattern, but for document creation

**Design Rationale:**

Unlike the `pdf` unified command which calls both `pdf-pptx` and `pdf-docx` separately, the `new` command creates a single `.qmd` file configured for multiple outputs. This approach:

1. Leverages Quarto's native multi-format support
2. Avoids naming conflicts (both commands would try to create `<dir>/<dir>.qmd`)
3. Provides a single source for both presentation and document
4. Simplifies maintenance (one file to edit instead of two)

**Implementation:**

## Command: `new`

**API Design:**
- `cmd_new(args: list[str]) -> int` - Handle unified new subcommand
  - Takes directory name as argument
  - Returns 0 on success, 1 on error

**Behavior:**
1. Validate directory name argument provided
2. Create directory if doesn't exist
3. Create `<directory>/<directory>.qmd` with multi-format YAML frontmatter
4. Create symlink `<directory>/simple-presentation.pptx` → `../templates/simple-presentation.pptx`
5. Create symlink `<directory>/simple-document.docx` → `../templates/simple-document.docx`
6. Create `<directory>/render.sh` from template
7. Print success message indicating both formats will be created

**QMD Template Structure:**

```yaml
---
title: "<project-name>"
format:
  pptx:
    reference-doc: simple-presentation.pptx
  docx:
    reference-doc: simple-document.docx
    toc: true
    number-sections: true
---

## Introduction

Content here...
```

**Output Messages:**
```
Created: <directory>/<directory>.qmd
Outputs: Both PowerPoint (.pptx) and Word (.docx)
Hint: Run 'cd <directory> && ./render.sh' to generate both formats
```

**Error Handling:**
- If no directory argument: Print usage, exit 1
- If invalid directory name: Print error, exit 1
- If QMD file already exists: Print error, exit 1
- If templates not found: Print error, exit 1
- If directory creation fails: Print error, exit 1
- If symlink creation fails: Print warning (non-fatal), continue

**Testing Strategy:**

Unit tests (`tests/commands/test_new.py`):
- Test successful creation with new directory
- Test successful creation when directory already exists (but qmd doesn't)
- Test error when qmd file already exists
- Test error when no directory argument provided
- Test error when invalid directory name provided
- Test with subdirectory paths
- Verify QMD content has both output formats
- Verify both symlinks created
- Verify render.sh created and executable
- Test error cases for missing templates
- Test directory creation errors
- Test QMD write errors
- Test symlink creation warnings (non-fatal)

Integration tests (`tests/test_cli.py`):
- Test `main(["new", "test-project"])` succeeds
- Verify QMD file created with both formats
- Test CLI subprocess invocation
- Verify file structure and content

**CLI Integration:**

Add to `cli.py`:
```python
elif command == "new":
    return cmd_new(command_args)
```

Add to `commands/__init__.py`:
```python
from quarto4sbp.commands.new import cmd_new
```

Update help text:
```
Unified commands:
  new        Create both PowerPoint and Word documents from templates
  pdf        Export all Office documents (PPTX and DOCX) to PDF
```

**Documentation Updates:**

README.md:
- Add `new` command to usage section
- Add example showing unified document creation
- Explain difference between `new`, `new-pptx`, and `new-docx`

**File Structure:**

```
quarto4sbp/
  commands/
    new.py              # cmd_new() implementation
    new_pptx.py         # cmd_new_pptx() (existing - for PPTX only)
    new_docx.py         # cmd_new_docx() (existing - for DOCX only)
    pdf.py              # cmd_pdf() (existing - unified PDF export)
templates/
  simple-presentation.pptx  # PowerPoint template (existing)
  simple-document.docx      # Word template (existing)
  render.sh.template        # Unified render script (existing)
tests/
  commands/
    test_new.py         # Unit tests for unified new command
    test_new_pptx.py    # Tests for PPTX-only command (existing)
    test_new_docx.py    # Tests for DOCX-only command (existing)
```

**Usage Examples:**

```bash
# Create both formats in one command
$ q4s new my-project
Created: my-project/my-project.qmd
Outputs: Both PowerPoint (.pptx) and Word (.docx)
Hint: Run 'cd my-project && ./render.sh' to generate both formats

$ cd my-project
$ ./render.sh
Rendering my-project.qmd...
✓ Successfully rendered my-project.qmd
Exporting to PDF...
✓ Successfully exported to PDF

Output files created in current directory

# Files created:
# - my-project.qmd          (source)
# - my-project.pptx         (PowerPoint output)
# - my-project.docx         (Word output)
# - my-project.pptx.pdf     (PDF from PowerPoint, if exported)
# - my-project.docx.pdf     (PDF from Word, if exported)
```

**Comparison with Format-Specific Commands:**

| Command | QMD Files | Output Formats | Use Case |
|---------|-----------|----------------|----------|
| `q4s new` | 1 file | Both PPTX + DOCX | Need both formats from same content |
| `q4s new-pptx` | 1 file | PPTX only | Only need presentation |
| `q4s new-docx` | 1 file | DOCX only | Only need document |

**Advantages of Unified Approach:**

1. **Single Source:** Edit one file, get both outputs
2. **Consistency:** Content automatically synced between formats
3. **Efficiency:** One command instead of two
4. **Quarto Native:** Uses built-in multi-format support
5. **Flexibility:** Can still use format-specific commands when needed

**Known Issue - PDF Naming Conflict:**

When using the unified `new` command, Quarto generates both:
- `my-project.pptx`
- `my-project.docx`

When `render.sh` calls `q4s pdf`, both `pdf-pptx` and `pdf-docx` try to create the same filename:
- `my-project.pptx` → `my-project.pdf`
- `my-project.docx` → `my-project.pdf`

This causes the second PDF to overwrite the first, losing one of the outputs.

**Solution (q4s-42):** Use double extension naming to preserve source format:
- `my-project.pptx` → `my-project.pptx.pdf`
- `my-project.docx` → `my-project.docx.pdf`

This approach:
- Preserves both PDFs
- Makes source format clear
- Uses a common pattern (like `.tar.gz`)
- Requires minimal code changes

Implementation details in issue q4s-42.

**Status:** Implemented (q4s-41), PDF naming conflict tracked in q4s-42