# 007 - Word Support

**Purpose:** Add comprehensive Microsoft Word (.docx) support parallel to PowerPoint (.pptx) support, including template creation, PDF export, and rendering workflow

**Requirements:**
- `q4s new-docx <directory>` command to create new Word documents from template
- `q4s pdf-docx` command to export DOCX files to PDF (when DOCX is newer than PDF)
- `q4s pdf` unified command to export both PPTX and DOCX files to PDF
- Word document template with proper Quarto frontmatter
- AppleScript-based PDF export via Microsoft Word application (macOS)
- Follow same patterns as PowerPoint support (spec-005, spec-006)

**Design Approach:**
- Mirror PowerPoint implementation patterns for consistency
- Use Microsoft Word via AppleScript for PDF export
- Support Word-specific features: TOC, section numbering, custom styles
- Template based on Quarto docx format specifications
- Unified render script works for both PowerPoint and Word

**Template Structure:**
- `simple-document.qmd` - QMD template with sample content
- `simple-document.docx` - Word reference document (created via `quarto pandoc --print-default-data-file reference.docx`)
- `render.sh.template` - Unified render script (see `000-shared-patterns.md`)

**Word-Specific YAML Frontmatter:**
```yaml
format:
  docx:
    reference-doc: simple-document.docx
    toc: true
    number-sections: true
```

## Command: new-docx

**Purpose:** Create new Word documents from template

**Behavior:**
- Create directory structure from Word template
- Symlink to reference document in `templates/`
- Generate render script from template
- Print creation confirmation and usage hint

**Implementation Notes:**
- See `000-shared-patterns.md` for template creation command pattern
- Uses unified render script that works for both PowerPoint and Word formats

## Command: pdf-docx

**Purpose:** Export Word documents to PDF when DOCX is newer than PDF

**Behavior:**
- Scan directory for stale DOCX files needing export
- Use AppleScript to control Word for PDF export
- Export directly in place (no temporary directory)
- Graceful error handling if Word unavailable

**Implementation Notes:**
- See `000-shared-patterns.md` for PDF export command pattern
- See `000-shared-patterns.md` for AppleScript Word export pattern
- Integration tests use `@unittest.skipUnless` with `RUN_INTEGRATION_TESTS` env var

## Command: pdf (unified)

**Purpose:** Provide single command to export all Office documents (PPTX and DOCX) to PDF

**Behavior:**
- Call `cmd_pdf_pptx()` to export all PowerPoint files
- Call `cmd_pdf_docx()` to export all Word documents
- Aggregate results and print combined summary
- Return 0 if both succeed, 1 if either fails

**Implementation Notes:**
- Rename existing `pdf.py` to `pdf_pptx.py`
- Rename existing `new.py` to `new_pptx.py`
- Create new `pdf.py` that imports and calls both format-specific commands
- See `000-shared-patterns.md` for CLI integration pattern

## Unified Render Script

**Purpose:** Single `render.sh` script that works for both PowerPoint and Word documents

**Design:**
- One `render.sh.template` in `templates/` directory
- Used by both `new-pptx` and `new-docx` commands
- Calls `quarto render` followed by unified `q4s pdf` command
- Template uses `{{FILE_NAME}}` placeholder

**Benefits:**
- Single template to maintain
- Works automatically for any Quarto format
- Unified `pdf` command handles format detection
- Consistent user experience across formats

**Status:** Implemented