# 008 - Unified New Command with Double Extension PDF Naming

**Purpose:** Unified `new` command that creates a single Quarto document configured to output to both PowerPoint (.pptx) and Word (.docx) formats, with double-extension PDF naming to preserve both PDF outputs

**Requirements:**
- `q4s new <directory>` command to create a document with both PPTX and DOCX outputs
- Single `.qmd` file with multiple output formats in YAML frontmatter
- Symlinks to both PowerPoint and Word templates
- Unified render script that generates both formats
- Double extension PDF naming (`.pptx.pdf` and `.docx.pdf`) to preserve both PDFs

**Design Approach:**
- Leverage Quarto's native multi-format support
- Single source file avoids naming conflicts and content duplication
- Uses multi-format YAML frontmatter (see `000-shared-patterns.md`)
- Double extension naming pattern (similar to `.tar.gz`, `.html.erb`)

**Multi-Format QMD Structure:**
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
```

## Command: new

**Behavior:**
- Create directory if doesn't exist
- Create `<directory>/<directory>.qmd` with multi-format YAML frontmatter
- Create symlinks to both PowerPoint and Word templates
- Generate unified render script
- Print confirmation indicating both formats will be created

**Implementation Notes:**
- See `000-shared-patterns.md` for template creation command pattern
- Uses same render script as format-specific commands
- Provides single source for both presentation and document

## PDF Double Extension Naming

**Purpose:** Preserve both PDF outputs without conflicts

**Design:**
- `file.pptx` → `file.pptx.pdf`
- `file.docx` → `file.docx.pdf`

**Benefits:**
- Preserves all outputs (no conflicts)
- Clear provenance (filename shows source format)
- Common pattern (like `.tar.gz`, `.spec.ts`)
- Minimal implementation (simple path construction)

**Implementation:**
```python
# In pdf_pptx.py and pdf_docx.py
pdf_path = Path(str(source_path) + ".pdf")
```

**Staleness Detection:**
Both `find_stale_pptx()` and `find_stale_docx()` check for double extension PDFs.

## Comparison with Format-Specific Commands

| Command | QMD Files | Output Formats | Use Case |
|---------|-----------|----------------|----------|
| `q4s new` | 1 file | Both PPTX + DOCX | Need both formats from same content |
| `q4s new-pptx` | 1 file | PPTX only | Only need presentation |
| `q4s new-docx` | 1 file | DOCX only | Only need document |

**Status:** Implemented