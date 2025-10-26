# 005 - New PowerPoint Command

**Purpose:** Add a `q4s new-pptx` command to scaffold new Quarto PowerPoint presentations from a template

**Requirements:**
- `q4s new-pptx <directory>` command to create a new PowerPoint presentation
- Create directory if it doesn't exist
- Generate `.qmd` file named same as directory inside the directory
- Create symlink to `templates/simple-presentation.pptx` in the new directory
- Template based on `templates/simple-presentation.qmd` (inspired by `examples/caseum/introduction.qmd`)
- Create `render.sh` script in the new directory (unified script that works for both PowerPoint and Word)
- Output path to created `.qmd` file
- Print hint to run `./render.sh` to generate the presentation
- Proper error handling for existing files and invalid paths

**Design Approach:**
- Follow dependency-free core philosophy (stdlib only: os, pathlib, sys)
- Use pathlib for cross-platform path handling
- Template should include standard Quarto YAML frontmatter
- Relative symlink to `../templates/simple-presentation.pptx` from presentation directory
- Clear user feedback on success

**File Structure:**
```
quarto4sbp/
  commands/
    new_pptx.py         # cmd_new_pptx() implementation (renamed from new.py)
templates/
  simple-presentation.qmd   # Template file
  simple-presentation.pptx  # PowerPoint template
  render.sh.template        # Unified render script template (works for both pptx and docx)
tests/
  commands/
    test_new_pptx.py    # Unit tests for new-pptx command (renamed from test_new.py)
```

**Template Design:**
The `templates/simple-presentation.qmd` should include:
- Basic YAML frontmatter (title, subtitle, author placeholders)
- Font configuration (Merriweather, Merriweather Sans, Cascadia Code)
- PPTX format with reference to `simple-presentation.pptx`
- Sample slides showing common patterns (title slide, columns, speaker notes)
- Based on structure from `examples/caseum/introduction.qmd`

**API Design:**
- `cmd_new_pptx(args: list[str]) -> int` - Handle new-pptx subcommand
  - Takes directory name as argument
  - Returns 0 on success, 1 on error

**Behavior:**
1. Validate directory name argument provided
2. Create directory if doesn't exist (error if file exists with same name)
3. Create `<directory>/<directory>.qmd` from template
4. Create symlink `<directory>/simple-presentation.pptx` → `../templates/simple-presentation.pptx`
5. Create `<directory>/render.sh` from template with file name substituted (uses `{{FILE_NAME}}` placeholder)
6. Make `render.sh` executable
7. Print: `Created: <directory>/<directory>.qmd`
8. Print: `Hint: Run 'cd <directory> && ./render.sh' to generate the presentation`

**Testing Strategy:**
- Test successful creation with new directory
- Test successful creation when directory already exists (but qmd doesn't)
- Test error when qmd file already exists
- Test error when no directory argument provided
- Test error when directory name is invalid
- Verify symlink is created correctly
- Verify template content is copied correctly
- Verify render.sh script is created and executable
- Verify render.sh contains correct file name
- Use temporary directories for testing

**Implementation Notes:**
- Use `Path.mkdir(parents=True, exist_ok=True)` for directory creation
- Use `Path.symlink_to()` for symlink creation
- Handle Windows compatibility (symlinks may require admin/developer mode)
- Template file should be readable and documented
- Follow shared patterns from `000-shared-patterns.md`
- render.sh template uses `#!/bin/sh` for portability
- render.sh script is unified - works for both PowerPoint and Word formats
- Template uses `{{FILE_NAME}}` placeholder (more generic than format-specific names)
- render.sh calls unified `q4s pdf` command that handles both PPTX and DOCX files

**Status:** Implemented