# 006 - PDF PowerPoint Command

**Purpose:** Add a `q4s pdf-pptx` command to automatically export PowerPoint presentations to PDF when PPTX files are newer than their PDF counterparts

**Requirements:**
- `q4s pdf-pptx` command to find and export PPTX files to PDF
- Export when source is newer than PDF or PDF doesn't exist
- Use Microsoft PowerPoint via AppleScript for export (macOS)
- Skip template files (symlinks, files in `templates/` directory)
- Integration tests marked as optional (not run in CI)

**Design Approach:**
- Scan directory for stale PPTX files needing export
- Use AppleScript to control PowerPoint for PDF export
- Export directly in place (no temporary directory)
- Graceful error handling if PowerPoint unavailable

**Implementation Notes:**
- See `000-shared-patterns.md` for PDF export command pattern
- See `000-shared-patterns.md` for AppleScript PowerPoint export pattern
- Integration tests use `@unittest.skipUnless` with `RUN_INTEGRATION_TESTS` env var

**Status:** Implemented