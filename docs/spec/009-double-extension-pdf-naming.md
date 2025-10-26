# 009 - Double Extension PDF Naming

**Purpose:** Change PDF export naming from single to double extension to prevent file conflicts when a single QMD outputs to multiple formats

**Related Issues:** q4s-42

**Problem Statement:**

Currently, both `pdf-pptx` and `pdf-docx` commands create PDF files by replacing the source extension with `.pdf`:
- `my-project.pptx` → `my-project.pdf`
- `my-project.docx` → `my-project.pdf`

This works fine when using format-specific commands (`new-pptx` or `new-docx`) which create only one output format. However, with the unified `new` command (q4s-41), Quarto renders both formats:
- `my-project.pptx`
- `my-project.docx`

When `render.sh` calls `q4s pdf`, the unified command runs both `pdf-pptx` and `pdf-docx`, causing:
1. `pdf-pptx` exports `my-project.pptx` → `my-project.pdf`
2. `pdf-docx` exports `my-project.docx` → `my-project.pdf` (overwrites!)

Users lose one of the two PDFs they explicitly requested.

**Solution:**

Use double extension naming to preserve the source format in the PDF filename:
- `my-project.pptx` → `my-project.pptx.pdf`
- `my-project.docx` → `my-project.docx.pdf`

**Design Rationale:**

1. **Preserves all outputs:** Users get both PDFs when using unified `new` command
2. **Clear provenance:** Filename shows which source format created the PDF
3. **Common pattern:** Similar to `.tar.gz`, `.html.erb`, `.spec.ts`, etc.
4. **Minimal changes:** Only affects PDF path construction
5. **Backwards incompatible but acceptable:** Project is new enough to handle this

**Implementation Details:**

## Files to Modify:

### 1. `quarto4sbp/commands/pdf_pptx.py`

**Current:**
```python
def export_pptx_to_pdf(pptx_path: Path) -> bool:
    pdf_path = pptx_path.with_suffix(".pdf")
```

**Change to:**
```python
def export_pptx_to_pdf(pptx_path: Path) -> bool:
    # Use double extension to preserve source format
    pdf_path = Path(str(pptx_path) + ".pdf")
```

### 2. `quarto4sbp/commands/pdf_docx.py`

**Current:**
```python
def export_docx_to_pdf(docx_path: Path) -> bool:
    pdf_path = docx_path.with_suffix(".pdf")
```

**Change to:**
```python
def export_docx_to_pdf(docx_path: Path) -> bool:
    # Use double extension to preserve source format
    pdf_path = Path(str(docx_path) + ".pdf")
```

### 3. Update `find_stale_pptx()` and `find_stale_docx()`

These functions check if PDF is newer than source. Update the PDF path calculation:

**Current:**
```python
pdf_path = pptx_path.with_suffix(".pdf")
```

**Change to:**
```python
pdf_path = Path(str(pptx_path) + ".pdf")
```

### 4. Update Console Messages

Change output messages to reflect new naming:

**Current:**
```
Exporting: presentation.pptx -> presentation.pdf
```

**New:**
```
Exporting: presentation.pptx -> presentation.pptx.pdf
```

## Tests to Update:

### 1. `tests/commands/test_pdf_pptx.py`

Update all assertions and mock expectations:
- Change `"document.pdf"` → `"document.pptx.pdf"`
- Update `with_suffix(".pdf")` → `Path(str(path) + ".pdf")`
- Update test output expectations

**Affected tests:**
- `TestExportPptxToPdf::test_export_success`
- `TestExportPptxToPdf::test_export_pdf_not_created`
- `TestCmdPdfPptx::test_export_integration`
- All tests checking PDF filenames

### 2. `tests/commands/test_pdf_docx.py`

Update all assertions and mock expectations:
- Change `"document.pdf"` → `"document.docx.pdf"`
- Update path construction
- Update test output expectations

**Affected tests:**
- `TestExportDocxToPdf::test_export_success`
- `TestExportDocxToPdf::test_export_pdf_not_created`
- `TestCmdPdfDocx::test_export_single_file`
- All tests checking PDF filenames

### 3. `tests/commands/test_pdf_pptx_integration.py`

Update integration tests if they check PDF filenames.

### 4. `tests/commands/test_pdf.py`

Verify unified command works with double extensions (likely no changes needed as it delegates to sub-commands).

## Documentation Updates:

### 1. `README.md`

Update examples to show new naming:

**Current:**
```bash
$ q4s pdf-pptx
Found 1 file(s) to export:
  - presentation.pptx
Exporting: presentation.pptx -> presentation.pdf
```

**New:**
```bash
$ q4s pdf-pptx
Found 1 file(s) to export:
  - presentation.pptx
Exporting: presentation.pptx -> presentation.pptx.pdf

$ q4s pdf-docx
Found 1 file(s) to export:
  - document.docx
Exporting: document.docx -> document.docx.pdf

# When using unified 'new' command:
$ q4s new my-project
$ cd my-project && ./render.sh
$ ls *.pdf
my-project.pptx.pdf
my-project.docx.pdf
```

### 2. `docs/spec/006-pdf-export.md` (if exists)

Update spec to document double extension naming pattern.

### 3. `docs/spec/007-word-support.md`

Update examples showing PDF export to use new naming.

### 4. `docs/spec/008-unified-new-command.md`

Already updated to document the issue and solution.

## Implementation Checklist:

- [ ] Update `pdf_pptx.py::export_pptx_to_pdf()` path construction
- [ ] Update `pdf_pptx.py::find_stale_pptx()` path construction
- [ ] Update `pdf_docx.py::export_docx_to_pdf()` path construction
- [ ] Update `pdf_docx.py::find_stale_docx()` path construction
- [ ] Update console output messages in both commands
- [ ] Update all tests in `test_pdf_pptx.py`
- [ ] Update all tests in `test_pdf_docx.py`
- [ ] Update integration tests if needed
- [ ] Update README.md examples
- [ ] Update spec documentation
- [ ] Run full test suite to verify
- [ ] Test with real PPTX and DOCX files
- [ ] Test unified `new` command workflow end-to-end
- [ ] Update any other references to PDF naming

## Testing Strategy:

### Unit Tests:
1. Test PDF path construction with double extension
2. Test staleness detection with double extension PDFs
3. Test export success/failure with new naming
4. Test that old single-extension PDFs are not detected (fresh export)

### Integration Tests:
1. Create project with unified `new` command
2. Run `./render.sh` to generate both formats
3. Verify both `.pptx.pdf` and `.docx.pdf` are created
4. Verify neither overwrites the other
5. Test that re-running doesn't re-export if PDFs are newer

### Manual Testing:
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

## Migration Notes:

**For existing users:**

This is a breaking change. Existing workflows that expect `file.pdf` will now get `file.pptx.pdf` or `file.docx.pdf`.

Users should:
1. Update any scripts/automation that reference PDF filenames
2. Note that old `.pdf` files will not be automatically updated/renamed
3. Re-export to get new naming convention

Since the project is in early stages, migration impact should be minimal.

## Alternative Approaches Considered:

1. **Suffix naming** (`file-pptx.pdf`, `file-docx.pdf`) - Rejected as less clear
2. **Subdirectories** (`pdf/pptx/file.pdf`) - Rejected as too complex
3. **Last wins** (accept overwrite) - Rejected as loses data
4. **Smart detection** (only export "primary") - Rejected as too magical

## Future Considerations:

- Could add a `--naming` flag to allow users to choose between conventions
- Could add a config file option for naming preference
- Consider documenting pattern in a central "naming conventions" doc

**Status:** Implemented (q4s-42)