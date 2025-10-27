# 012 - Tone of Voice Rewriting

**Purpose:** Rewrite .qmd file content to match company tone of voice guidelines using LLM, ensuring consistent brand voice across all documents and presentations

**Requirements:**
- Process existing .qmd files and rewrite content to match tone of voice guidelines
- Preserve YAML frontmatter, code blocks, and document structure
- Maintain all technical accuracy and factual information
- Support company-specific tone of voice configuration
- Update files in-place with backup option
- Provide dry-run mode to preview changes
- Handle both presentation and document formats

**Design Approach:**
- **LLM-powered rewriting**: Use LLM to intelligently rewrite content while preserving meaning
- **Structure preservation**: Parse .qmd to separate YAML, code, and prose for selective rewriting
- **Guidelines in prompt**: Load tone of voice guidelines from prompt/ dir
- **Safe updates**: Create backup before modifying files
- **Transparent process**: Show before/after diffs in dry-run mode

**Architecture Components:**

### 1. Command Interface (`q4s tov <file.qmd>`)
```
q4s tov <file.qmd>              # Rewrite file to match tone of voice
q4s tov <file.qmd> --dry-run    # Preview changes without modifying
q4s tov <file.qmd> --no-backup  # Skip backup creation
q4s tov <directory>             # Process all .qmd files in directory
```

### 2. Tone of Voice Configuration
Use prompts/tov/system.txt.

### 3. QMD Parser (`quarto4sbp/tov/parser.py`)
Parse .qmd files into structured sections:
- YAML frontmatter (preserve as-is)
- Markdown content (rewrite)
- Code blocks (preserve as-is)
- Inline code (preserve as-is)

Use a good markdown parser. Note QMD files are quarto markdown files, which are a superset of standard markdown.

### 4. Content Rewriter (`quarto4sbp/tov/rewriter.py`)
- Split content into logical units (slides/sections)
- Send each unit to LLM with tone guidelines
- Use existing prompts in `prompts/tov/`
- Reassemble rewritten content

### 5. File Updater (`quarto4sbp/tov/updater.py`)
- Create `.bak` backup (unless `--no-backup`)
- Write updated content preserving line endings
- Report changes (lines modified, backup location)

**Command Flow:**
1. Parse command arguments (file path, flags)
2. Read and parse .qmd file
3. Extract markdown content (skip YAML and code blocks)
4. Split into sections (by headers or slides)
5. For each section:
   - Send to LLM with prompt(s)
   - Receive rewritten content
6. Reassemble file with rewritten content
7. In dry-run: show diff, exit
8. Otherwise: create backup, write file, report

**Implementation Notes:**
- Use existing `LLMClient` from `quarto4sbp.llm.client`
- Load prompts from `prompts/tov/` directory
- Preserve exact whitespace in code blocks and YAML
- Handle multi-line YAML values correctly
- Progress indicator for multiple files or long content
- Validate rewritten content has same structural elements (headings count, etc.)

**Error Handling:**
- LLM API failures: retry logic from LLMClient, fallback to original content
- Malformed .qmd: report specific parsing error
- File write errors: preserve backup, report issue

**Testing Strategy:**
- Use existing LLM testing support/approach from [llm-testing-guide.md](../llm-testing-guide.md)
- Test YAML preservation (frontmatter unchanged)
- Test code block preservation (no changes to code)
- Test structure preservation (heading levels maintained)
- Test backup creation and restoration
- Test dry-run mode (no file modifications)
- Integration test with real LLM (gated by RUN_INTEGRATION_TESTS)

**Example Usage:**

```bash
# Rewrite single file
q4s tov my-presentation/my-presentation.qmd

# Preview changes without modifying
q4s tov my-presentation/my-presentation.qmd --dry-run

# Process all files in directory
q4s tov my-presentations/

# Use custom guidelines
q4s tov document.qmd --guidelines company-style.md
```

**Status:** Draft
