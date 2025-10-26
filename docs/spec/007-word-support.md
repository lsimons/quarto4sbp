# 007 - Word Support

**Purpose:** Add comprehensive Microsoft Word (.docx) support parallel to PowerPoint (.pptx) support, including template creation, PDF export, and rendering workflow

**Requirements:**
- `q4s new-doc <directory>` command to create new Word documents from template
- `q4s pdf-doc` command to export DOCX files to PDF (when DOCX is newer than PDF)
- Word document template with proper Quarto frontmatter
- Render script for Word documents
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
    new_doc.py          # cmd_new_doc() implementation
    pdf_doc.py          # cmd_pdf_doc() implementation
templates/
  simple-document.qmd   # Word template file (new)
  simple-document.docx  # Word reference doc (new)
  render-doc.sh.template # Render script for docs (new)
tests/
  commands/
    test_new_doc.py     # Unit tests for new-doc command
    test_pdf_doc.py     # Unit tests for pdf-doc command
    test_pdf_doc_integration.py  # Integration tests (optional)
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
5. Create `<directory>/render-doc.sh` from template with document name substituted
6. Make `render-doc.sh` executable
7. Print: `Created: <directory>/<directory>.qmd`
8. Print: `Hint: Run 'cd <directory> && ./render-doc.sh' to generate the document`

**render-doc.sh.template:**
```bash
#!/bin/sh
# Render Quarto document to DOCX and PDF

set -e

echo "Rendering {{DOCUMENT_NAME}}.qmd to DOCX..."
quarto render {{DOCUMENT_NAME}}.qmd

echo "Exporting DOCX to PDF..."
q4s pdf-doc

echo "Done! Output files:"
echo "  - {{DOCUMENT_NAME}}.docx"
echo "  - {{DOCUMENT_NAME}}.pdf"
```

**Testing Strategy:**
- Test successful creation with new directory
- Test successful creation when directory already exists (but qmd doesn't)
- Test error when qmd file already exists
- Test error when no directory argument provided
- Verify symlink created correctly
- Verify template content copied correctly
- Verify render-doc.sh created and executable
- Verify render-doc.sh contains correct document name
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
- Document render-doc.sh workflow
- Note macOS + Microsoft Word requirement for PDF export

**Parallel with PowerPoint:**
- `new` → `new-doc` (create presentation → create document)
- `pdf` → `pdf-doc` (export pptx → export docx)
- `simple-presentation.*` → `simple-document.*` (template naming)
- `render.sh` → `render-doc.sh` (render script naming)

**Status:** Not yet implemented