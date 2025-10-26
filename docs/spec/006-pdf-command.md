# 006 - PDF Command

**Purpose:** Add a `q4s pdf` command to automatically export PowerPoint presentations to PDF when PPTX files are newer than their PDF counterparts

**Requirements:**
- `q4s pdf` command to find and export PPTX files to PDF
- Scan current directory for `.pptx` files
- Export PPTX to PDF if:
  - No corresponding PDF exists, OR
  - PPTX modification time is newer than PDF modification time
- Use Microsoft PowerPoint via AppleScript for export
- Handle macOS sandbox restrictions by using temporary folders
- Skip PPTX files that are templates (in `templates/` directory or symlinks)
- Integration tests marked as optional (not run in CI by default)

**Design Approach:**
- Follow dependency-free core philosophy (stdlib only: os, pathlib, sys, subprocess, tempfile, shutil)
- Use AppleScript to control PowerPoint for PDF export
- Work around macOS sandbox by copying files to `/tmp/` subdirectory before export
- Clean up temporary files after export
- Provide clear user feedback on which files are being exported
- Graceful error handling if PowerPoint is not installed or AppleScript fails

**File Structure:**
```
quarto4sbp/
  commands/
    pdf.py              # cmd_pdf() implementation
tests/
  commands/
    test_pdf.py         # Unit tests (file discovery, temp folder logic)
    test_pdf_integration.py  # Integration tests (actual PowerPoint export)
```

**API Design:**
- `cmd_pdf(args: list[str]) -> int` - Handle pdf subcommand
  - Takes optional directory argument (defaults to current directory)
  - Returns 0 on success, 1 on error
- `find_stale_pptx(directory: Path) -> list[Path]` - Find PPTX files needing export
  - Returns list of PPTX files that need PDF export
  - Excludes symlinks and files in `templates/` directory
- `export_pptx_to_pdf(pptx_path: Path) -> bool` - Export single PPTX to PDF
  - Copies PPTX to temporary folder
  - Invokes PowerPoint via AppleScript
  - Copies PDF back to original location
  - Cleans up temporary folder
  - Returns True on success, False on failure

**Behavior:**
1. Scan current directory (non-recursively) for `.pptx` files
2. Filter out symlinks and template files
3. For each PPTX file:
   - Check if corresponding `.pdf` exists
   - If PDF doesn't exist or is older than PPTX:
     - Print: `Exporting: <filename>.pptx -> <filename>.pdf`
     - Create temporary subdirectory in `/tmp/q4s-pdf-<random>/`
     - Copy PPTX to temp directory
     - Invoke AppleScript to export PDF via PowerPoint
     - Copy PDF from temp directory to original location
     - Remove temporary subdirectory
   - If PDF is up-to-date:
     - Print: `Skipping: <filename>.pdf is up to date`
4. Print summary: `Exported X file(s), skipped Y file(s)`

**AppleScript Design:**
```applescript
tell application "Microsoft PowerPoint"
    activate
    open POSIX file "/tmp/q4s-pdf-XXXXX/presentation.pptx"
    set theDoc to active presentation
    save theDoc in POSIX file "/tmp/q4s-pdf-XXXXX/presentation.pdf" as save as PDF
    close theDoc
    quit
end tell
```

**Testing Strategy:**
- **Unit tests** (always run):
  - Test `find_stale_pptx()` with various file scenarios
  - Test file filtering (symlinks, templates)
  - Test modification time comparison logic
  - Test temporary folder creation and cleanup
  - Mock AppleScript invocation
  - Use temporary test directories
  
- **Integration tests** (marked as optional, skip in CI):
  - Test actual PowerPoint export with real PPTX file
  - Verify PDF is created with correct content
  - Test error handling when PowerPoint is not available
  - Marked with `@unittest.skipUnless` decorator checking for `RUN_INTEGRATION_TESTS` env var
  - Document in README how to run: `RUN_INTEGRATION_TESTS=1 uv run pytest tests/commands/test_pdf_integration.py`

**CI Configuration:**
- Default pytest run (in `.github/workflows/`) does NOT set `RUN_INTEGRATION_TESTS`
- Integration tests automatically skipped in CI
- Can be manually enabled locally for testing

**Implementation Notes:**
- Use `pathlib.Path.stat().st_mtime` for modification time comparison
- Use `tempfile.mkdtemp(prefix='q4s-pdf-')` for temporary directory
- Use `shutil.copy2()` to preserve timestamps when copying
- Use `subprocess.run(['osascript', '-e', script])` to execute AppleScript
- Catch and report `CalledProcessError` from subprocess with user-friendly messages
- Ensure temporary directory cleanup even on errors (try/finally)
- Handle case where PowerPoint is not installed gracefully
- Command should work in any directory containing PPTX files
- Follow error handling patterns from DESIGN.md (graceful degradation, clear messages)

**Error Handling:**
- If PowerPoint not installed: Print error, suggest installing PowerPoint, exit 1
- If AppleScript fails: Print error with details, continue to next file
- If file permissions prevent copy: Print error, skip file, continue
- If temp directory creation fails: Print error, exit 1
- Always clean up temp directories, even on failure

**Status:** Draft