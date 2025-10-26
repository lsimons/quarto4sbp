# 007 - Word Support

**Purpose:** Add comprehensive Microsoft Word (.docx) support parallel to PowerPoint (.pptx) support, including template creation, PDF export, and rendering workflow

**Epic Tasks:**
1. Rename `new` command to `new-pptx` and update spec-005 (q4s-38)
2. Rename `pdf` command to `pdf-pptx` and update spec-006 (q4s-37)
3. Implement `new-doc` command for Word documents
4. Implement `pdf-doc` command for Word PDF export
5. Create unified `pdf` command that calls both `pdf-pptx` and `pdf-doc` (q4s-36)
6. Create Word templates (qmd, docx, render.sh)
7. Update README.md to document PowerPoint and Word as dependencies (q4s-39)
8. Update documentation

**Requirements:**
- `q4s new-pptx <directory>` command to create new PowerPoint presentations (renamed from `new`)
- `q4s new-doc <directory>` command to create new Word documents from template
- `q4s pdf-pptx` command to export PPTX files to PDF (renamed from `pdf`)
- `q4s pdf-doc` command to export DOCX files to PDF (when DOCX is newer than PDF)
- `q4s pdf` unified command to export both PPTX and DOCX files to PDF
- Word document template with proper Quarto frontmatter
- Unified render script supporting both PowerPoint and Word documents
- AppleScript-based PDF export via Microsoft Word application
- Follow same patterns as PowerPoint support (spec-005, spec-006)

**Design Approach:**
- Mirror PowerPoint implementation patterns for consistency
- Use Microsoft Word via AppleScript for PDF export (macOS)
- Template based on Quarto docx format specifications
- Support Word-specific features: TOC, section numbering, custom styles
- Follow dependency-free core philosophy (stdlib only)

**File Structure:**
```
quarto4sbp/
  commands/
    new_pptx.py         # cmd_new_pptx() implementation (renamed from new.py)
    new_doc.py          # cmd_new_doc() implementation (new)
    pdf_pptx.py         # cmd_pdf_pptx() implementation (renamed from pdf.py)
    pdf_doc.py          # cmd_pdf_doc() implementation (new)
    pdf.py              # cmd_pdf() unified implementation (new)
templates/
  simple-presentation.qmd   # PowerPoint template (existing)
  simple-presentation.pptx  # PowerPoint reference doc (existing)
  simple-document.qmd       # Word template file (new)
  simple-document.docx      # Word reference doc (new)
  render.sh.template        # Unified render script (updated - works for both formats)
tests/
  commands/
    test_new_pptx.py    # Unit tests for new-pptx command (renamed)
    test_new_doc.py     # Unit tests for new-doc command (new)
    test_pdf_pptx.py    # Unit tests for pdf-pptx command (renamed)
    test_pdf_doc.py     # Unit tests for pdf-doc command (new)
    test_pdf.py         # Unit tests for unified pdf command (new)
    test_pdf_pptx_integration.py  # Integration tests for pptx (renamed)
    test_pdf_doc_integration.py   # Integration tests for docx (new)
```

**Template Design - simple-document.qmd:**
- Title, subtitle, author, date placeholders
- Word-specific YAML frontmatter:
  ```yaml
  format:
    docx:
      reference-doc: simple-document.docx
      toc: true
      number-sections: true
  ```
- Sample content demonstrating:
  - Headings (H1, H2, H3)
  - Lists (bullet and numbered)
  - Tables
  - Code blocks
  - Block quotes
  - Images (optional/placeholder)
  - Custom styles with `{custom-style="StyleName"}`

**Template Design - simple-document.docx:**
- Reference document created via: `quarto pandoc -o simple-document.docx --print-default-data-file reference.docx`
- Can be customized with Word styles (Heading 1-6, Code, Quote, etc.)
- Stored in `templates/` directory
- Symlinked into document directories (like PowerPoint template)

## new-doc Command

**API Design:**
- `cmd_new_doc(args: list[str]) -> int` - Handle new-doc subcommand
  - Takes directory name as argument
  - Returns 0 on success, 1 on error

**Behavior:**
1. Validate directory name argument provided
2. Create directory if doesn't exist (error if file exists with same name)
3. Create `<directory>/<directory>.qmd` from `templates/simple-document.qmd`
4. Create symlink `<directory>/simple-document.docx` → `../templates/simple-document.docx`
5. Create `<directory>/render.sh` from template with document name substituted
6. Make `render.sh` executable
7. Print: `Created: <directory>/<directory>.qmd`
8. Print: `Hint: Run 'cd <directory> && ./render.sh' to generate the document`

**Note:** Uses the same unified `render.sh.template` as PowerPoint (see Unified Render Script section below)</parameter>

**Testing Strategy:**
- Test successful creation with new directory
- Test successful creation when directory already exists (but qmd doesn't)
- Test error when qmd file already exists
- Test error when no directory argument provided
- Verify symlink created correctly
- Verify template content copied correctly
- Verify render.sh created and executable
- Verify render.sh contains correct document name
- Use temporary directories for testing

## pdf-doc Command

**API Design:**
- `cmd_pdf_doc(args: list[str]) -> int` - Handle pdf-doc subcommand
  - Takes optional directory argument (defaults to current directory)
  - Returns 0 on success, 1 on error
- `find_stale_docx(directory: Path) -> list[Path]` - Find DOCX files needing export
  - Returns list of DOCX files needing PDF export
  - Excludes symlinks and files in `templates/` directory
- `export_docx_to_pdf(docx_path: Path) -> bool` - Export single DOCX to PDF
  - Invokes Word via AppleScript to export PDF in place
  - Returns True on success, False on failure

**Behavior:**
1. Scan current directory (non-recursively) for `.docx` files
2. Filter out symlinks and template files (reference docs)
3. For each DOCX file:
   - Check if corresponding `.pdf` exists
   - If PDF doesn't exist or is older than DOCX:
     - Print: `Exporting: <filename>.docx -> <filename>.pdf`
     - Invoke AppleScript to export PDF via Word directly in place
   - If PDF is up-to-date:
     - Print: `Skipping: <filename>.pdf is up to date`
4. Print summary: `Exported X file(s), skipped Y file(s)`

**AppleScript Design:**
```applescript
tell application "Microsoft Word"
    open POSIX file "/full/path/to/document.docx"
    set theDoc to active document
    save as theDoc file name POSIX file "/full/path/to/document.pdf" file format format PDF
    close theDoc saving no
end tell
```

**Testing Strategy:**
- **Unit tests** (always run):
  - Test `find_stale_docx()` with various file scenarios
  - Test file filtering (symlinks, templates, reference docs)
  - Test modification time comparison logic
  - Mock AppleScript invocation
  - Use temporary test directories
  
- **Integration tests** (marked as optional, skip in CI):
  - Test actual Word export with real DOCX file
  - Verify PDF is created with correct content
  - Test error handling when Word is not available
  - Marked with `@unittest.skipUnless` decorator checking for `RUN_INTEGRATION_TESTS` env var
  - Document in README how to run: `RUN_INTEGRATION_TESTS=1 uv run pytest tests/commands/test_pdf_doc_integration.py`

**Implementation Notes:**
- Use `pathlib.Path.stat().st_mtime` for modification time comparison
- Use `subprocess.run(['osascript', '-e', script])` to execute AppleScript
- Use `docx_path.resolve()` to get absolute paths for AppleScript
- Catch and report `CalledProcessError` from subprocess with user-friendly messages
- Handle case where Word is not installed gracefully
- Command should work in any directory containing DOCX files
- Follow error handling patterns from DESIGN.md (graceful degradation, clear messages)
- Wire up commands in main CLI dispatcher (`quarto4sbp/cli.py`)

**Error Handling:**
- If Word not installed: Print error, suggest installing Word, exit 1
- If AppleScript fails: Print error with details, continue to next file
- If file operations fail: Print error, skip file, continue

**CLI Integration:**
Add to `cli.py` command dispatcher:
```python
elif command == "new-doc":
    from quarto4sbp.commands.new_doc import cmd_new_doc
    return cmd_new_doc(args[1:])
elif command == "pdf-doc":
    from quarto4sbp.commands.pdf_doc import cmd_pdf_doc
    return cmd_pdf_doc(args[1:])
```

Update help text to include:
- `new-doc   Create a new Word document from template`
- `pdf-doc   Export DOCX files to PDF (when DOCX is newer)`

**Documentation Updates:**
- Add Word support to README.md with examples
- Document Word-specific Quarto options (toc, number-sections, reference-doc)
- Document custom styles usage
- Document unified render.sh workflow
- Note macOS + Microsoft Word requirement for PDF export
- Update Prerequisites section to list Microsoft Office (PowerPoint and Word) for PDF export

## Unified pdf Command

**Purpose:** Provide a single command to export all Office documents (PPTX and DOCX) to PDF

**API Design:**
- `cmd_pdf(args: list[str]) -> int` - Handle unified pdf subcommand
  - Takes optional directory argument (defaults to current directory)
  - Returns 0 on success, 1 on error
  - Internally calls both `pdf_pptx.cmd_pdf_pptx()` and `pdf_doc.cmd_pdf_doc()`

**Behavior:**
1. Call `cmd_pdf_pptx(args)` to export all PowerPoint files
2. Call `cmd_pdf_doc(args)` to export all Word documents
3. Aggregate results and print combined summary
4. Return 0 if both succeed, 1 if either fails

**Implementation Notes:**
- Rename existing `pdf.py` to `pdf_pptx.py` (and update function names)
- Create new `pdf.py` that imports and calls both format-specific commands
- Wire up in CLI dispatcher to call unified command
- Update help text to show all three commands:
  - `pdf        Export all Office documents (PPTX and DOCX) to PDF`
  - `pdf-pptx   Export PPTX files to PDF (when PPTX is newer)`
  - `pdf-doc    Export DOCX files to PDF (when DOCX is newer)`

## Unified Render Script

**Purpose:** Single `render.sh` script that works for both PowerPoint and Word documents

**Design:**
- One `render.sh.template` in `templates/` directory
- Used by both `new-pptx` and `new-doc` commands
- Calls `quarto render` followed by unified `q4s pdf` command
- The unified `pdf` command automatically handles both PPTX and DOCX files
- Template uses `{{FILE_NAME}}` placeholder (more generic than PRESENTATION_NAME or DOCUMENT_NAME)

**Template Content:**
```bash
#!/bin/sh
# Render Quarto file and export to PDF
# Supports both PowerPoint (.pptx) and Word (.docx) formats

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

**Benefits:**
- Single template to maintain
- Works automatically for any Quarto format (pptx, docx, or even mixed)
- Unified `pdf` command handles format detection
- Consistent user experience across formats
- Simpler mental model for users

## Refactoring Tasks

**Task 1: Rename `new` to `new-pptx` (q4s-38)**
- Rename `commands/new.py` to `commands/new_pptx.py`
- Rename `cmd_new()` to `cmd_new_pptx()`
- Update CLI dispatcher in `cli.py`
- Update help text
- Update spec-005
- Update render.sh.template to use `{{FILE_NAME}}` placeholder and call unified `q4s pdf`
- Update tests in `tests/commands/test_new.py` → `test_new_pptx.py`
- Update README.md examples

**Task 2: Rename `pdf` to `pdf-pptx` (q4s-37)**
- Rename `commands/pdf.py` to `commands/pdf_pptx.py`
- Rename `cmd_pdf()` to `cmd_pdf_pptx()`
- Rename `find_stale_pptx()` to keep same name (already format-specific)
- Rename `export_pptx_to_pdf()` to keep same name (already format-specific)
- Update CLI dispatcher in `cli.py`
- Update help text
- Update spec-006
- No changes needed to render.sh.template (already calls unified `q4s pdf`)
- Update tests in `tests/commands/test_pdf.py` → `test_pdf_pptx.py`
- Update integration tests similarly
- Update README.md examples

**Task 3: Create unified `pdf` command (q4s-36)**
- Create new `commands/pdf.py` with `cmd_pdf()`
- Import and call both `cmd_pdf_pptx()` and `cmd_pdf_doc()`
- Wire up in CLI dispatcher
- Add tests in `tests/commands/test_pdf.py`
- Update help text
- Update README.md examples

**Task 4: Update README.md dependencies (q4s-39)**
- Add Microsoft Office section to Prerequisites
- Document PowerPoint requirement for `pdf-pptx` command
- Document Word requirement for `pdf-doc` command
- Note that unified `pdf` command requires both for full functionality
- Specify macOS requirement for AppleScript-based PDF export
- Add examples for both PowerPoint and Word workflows

**Naming Convention Summary:**
- **PowerPoint:** `new-pptx`, `pdf-pptx`, `simple-presentation.*`
- **Word:** `new-doc`, `pdf-doc`, `simple-document.*`
- **Unified:** `pdf` (calls both `pdf-pptx` and `pdf-doc`), `render.sh` (works for both formats)

**Status:** Not yet implemented