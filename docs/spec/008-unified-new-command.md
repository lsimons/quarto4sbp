# 008 - Unified New Command with Double Extension PDF Naming

**Purpose:** Unified `new` command that creates a single Quarto document configured to output to both PowerPoint (.pptx) and Word (.docx) formats, with double-extension PDF naming to preserve both PDF outputs

**Related Issues:** q4s-41, q4s-42

**Requirements:**
- `q4s new <directory>` command to create a document with both PPTX and DOCX outputs
- Single `.qmd` file with multiple output formats in YAML frontmatter
- Symlinks to both PowerPoint and Word templates
- Unified render script that generates both formats
- Double extension PDF naming (`.pptx.pdf` and `.docx.pdf`) to preserve both PDFs

**Design Rationale:**

Unlike the `pdf` unified command which calls both `pdf-pptx` and `pdf-docx` separately, the `new` command creates a single `.qmd` file configured for multiple outputs. This approach:

1. Leverages Quarto's native multi-format support
2. Avoids naming conflicts (both commands would try to create `<dir>/<dir>.qmd`)
3. Provides a single source for both presentation and document
4. Simplifies maintenance (one file to edit instead of two)

**PDF Naming Design:**

The system uses double extension naming for PDF exports:
- `my-project.pptx` → `my-project.pptx.pdf`
- `my-project.docx` → `my-project.docx.pdf`

This approach:
1. **Preserves all outputs:** Both PDFs are created without conflicts
2. **Clear provenance:** Filename shows which source format created the PDF
3. **Common pattern:** Similar to `.tar.gz`, `.html.erb`, `.spec.ts`, etc.
4. **Minimal implementation:** Simple path construction change

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

## PDF Export with Double Extension Naming

**Implementation in `quarto4sbp/commands/pdf_pptx.py`:**

```python
def export_pptx_to_pdf(pptx_path: Path) -> bool:
    # Use double extension to preserve source format
    pdf_path = Path(str(pptx_path) + ".pdf")
    # ... rest of export logic
```

**Implementation in `quarto4sbp/commands/pdf_docx.py`:**

```python
def export_docx_to_pdf(docx_path: Path) -> bool:
    # Use double extension to preserve source format
    pdf_path = Path(str(docx_path) + ".pdf")
    # ... rest of export logic
```

**Staleness Detection:**

Both `find_stale_pptx()` and `find_stale_docx()` check for double extension PDFs:

```python
# In find_stale_pptx()
pdf_path = Path(str(pptx_path) + ".pdf")

# In find_stale_docx()
pdf_path = Path(str(docx_path) + ".pdf")
```

**Console Messages:**

```
Exporting: presentation.pptx -> presentation.pptx.pdf
Exporting: document.docx -> document.docx.pdf
```

## Testing Strategy:

**Unit Tests (`tests/commands/test_new.py`):**
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

**PDF Export Tests (`tests/commands/test_pdf_pptx.py`, `test_pdf_docx.py`):**
- Test PDF path construction with double extension
- Test staleness detection with double extension PDFs
- Test export success/failure with new naming
- Test console output shows double extension filenames
- Verify `.pptx.pdf` and `.docx.pdf` files are created

**Integration Tests:**
1. Create project with unified `new` command
2. Run `./render.sh` to generate both formats
3. Verify both `.pptx.pdf` and `.docx.pdf` are created
4. Verify neither overwrites the other
5. Test that re-running doesn't re-export if PDFs are newer

**Manual Testing:**
```bash
# Test unified workflow
q4s new test-project
cd test-project
./render.sh
ls -la *.pdf
# Should show: test-project.pptx.pdf and test-project.docx.pdf

# Test individual commands
q4s new-pptx presentation
cd presentation
./render.sh
ls -la *.pdf
# Should show: presentation.pptx.pdf

q4s new-docx document
cd document
./render.sh
ls -la *.pdf
# Should show: document.docx.pdf
```

## CLI Integration:

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

## File Structure:

```
quarto4sbp/
  commands/
    new.py              # cmd_new() - unified command
    new_pptx.py         # cmd_new_pptx() - PPTX only
    new_docx.py         # cmd_new_docx() - DOCX only
    pdf.py              # cmd_pdf() - unified PDF export
    pdf_pptx.py         # cmd_pdf_pptx() - PPTX PDF export (double extension)
    pdf_docx.py         # cmd_pdf_docx() - DOCX PDF export (double extension)
templates/
  simple-presentation.pptx  # PowerPoint template
  simple-document.docx      # Word template
  render.sh.template        # Unified render script
tests/
  commands/
    test_new.py         # Unit tests for unified new command
    test_new_pptx.py    # Tests for PPTX-only command
    test_new_docx.py    # Tests for DOCX-only command
    test_pdf_pptx.py    # Tests with double extension naming
    test_pdf_docx.py    # Tests with double extension naming
```

## Usage Examples:

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

=== Exporting PowerPoint files ===
Found 1 file(s) to export:
  - my-project.pptx
Exporting: my-project.pptx -> my-project.pptx.pdf
Exported 1 file(s), skipped 0 file(s)

=== Exporting Word documents ===
Found 1 file(s) to export:
  - my-project.docx
Exporting: my-project.docx -> my-project.docx.pdf
Exported 1 file(s), skipped 0 file(s)

✓ All exports completed successfully

Output files created in current directory

# Files created:
# - my-project.qmd          (source)
# - my-project.pptx         (PowerPoint output)
# - my-project.docx         (Word output)
# - my-project.pptx.pdf     (PDF from PowerPoint)
# - my-project.docx.pdf     (PDF from Word)
# - simple-presentation.pptx (symlink to template)
# - simple-document.docx     (symlink to template)
# - render.sh               (render script)
```

## Comparison with Format-Specific Commands:

| Command | QMD Files | Output Formats | PDF Naming | Use Case |
|---------|-----------|----------------|------------|----------|
| `q4s new` | 1 file | Both PPTX + DOCX | `.pptx.pdf` + `.docx.pdf` | Need both formats from same content |
| `q4s new-pptx` | 1 file | PPTX only | `.pptx.pdf` | Only need presentation |
| `q4s new-docx` | 1 file | DOCX only | `.docx.pdf` | Only need document |

## Documentation Updates:

**README.md:**
- Add `new` command to usage section
- Add examples showing unified document creation
- Update PDF export examples to show double extension naming
- Explain difference between `new`, `new-pptx`, and `new-docx`

**Example updates:**
```bash
$ q4s pdf
=== Exporting PowerPoint files ===
Found 1 file(s) to export:
  - presentation.pptx
Exporting: presentation.pptx -> presentation.pptx.pdf
Exported 1 file(s), skipped 0 file(s)

=== Exporting Word documents ===
Found 1 file(s) to export:
  - document.docx
Exporting: document.docx -> document.docx.pdf
Exported 1 file(s), skipped 0 file(s)

✓ All exports completed successfully
```

## Advantages of Unified Approach:

1. **Single Source:** Edit one file, get both outputs
2. **Consistency:** Content automatically synced between formats
3. **Efficiency:** One command instead of two
4. **Quarto Native:** Uses built-in multi-format support
5. **Flexibility:** Can still use format-specific commands when needed
6. **No Conflicts:** Double extension naming preserves both PDFs

## Alternative Approaches Considered:

**For unified command:**
- Creating separate QMD files for each format - Rejected (maintenance burden, sync issues)
- Calling both `new-pptx` and `new-docx` - Rejected (naming conflicts)

**For PDF naming:**
- Suffix naming (`file-pptx.pdf`, `file-docx.pdf`) - Rejected as less clear
- Subdirectories (`pdf/pptx/file.pdf`) - Rejected as too complex
- Last wins (accept overwrite) - Rejected as loses data
- Smart detection (only export "primary") - Rejected as too magical

## Future Considerations:

- Could add a `--naming` flag to allow users to choose between conventions
- Could add a config file option for naming preference
- Consider adding `--format` flag to `new` command to specify which formats to include
- Could add validation to ensure both templates exist before creating unified document

**Status:** Implemented (q4s-41 for unified command, q4s-42 for double extension naming)