# 005 - New Command

**Purpose:** Add a `q4s new` command to scaffold new Quarto presentations from a template

**Requirements:**
- `q4s new <directory>` command to create a new presentation
- Create directory if it doesn't exist
- Generate `.qmd` file named same as directory inside the directory
- Create symlink to `templates/simple-presentation.pptx` in the new directory
- Template based on `templates/simple-presentation.qmd` (inspired by `examples/caseum/introduction.qmd`)
- Output path to created `.qmd` file
- Print hint to run `q4s render` (future command)
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
    new.py              # cmd_new() implementation
templates/
  simple-presentation.qmd   # Template file (new)
  simple-presentation.pptx  # PowerPoint template (exists)
tests/
  commands/
    test_new.py         # Unit tests for new command
```

**Template Design:**
The `templates/simple-presentation.qmd` should include:
- Basic YAML frontmatter (title, subtitle, author placeholders)
- Font configuration (Merriweather, Merriweather Sans, Cascadia Code)
- PPTX format with reference to `simple-presentation.pptx`
- Sample slides showing common patterns (title slide, columns, speaker notes)
- Based on structure from `examples/caseum/introduction.qmd`

**API Design:**
- `cmd_new(args: list[str]) -> int` - Handle new subcommand
  - Takes directory name as argument
  - Returns 0 on success, 1 on error

**Behavior:**
1. Validate directory name argument provided
2. Create directory if doesn't exist (error if file exists with same name)
3. Create `<directory>/<directory>.qmd` from template
4. Create symlink `<directory>/simple-presentation.pptx` → `../templates/simple-presentation.pptx`
5. Print: `Created: <directory>/<directory>.qmd`
6. Print: `Hint: Run 'q4s render <directory>/<directory>.qmd' to generate the presentation`

**Testing Strategy:**
- Test successful creation with new directory
- Test successful creation when directory already exists (but qmd doesn't)
- Test error when qmd file already exists
- Test error when no directory argument provided
- Test error when directory name is invalid
- Verify symlink is created correctly
- Verify template content is copied correctly
- Use temporary directories for testing

**Implementation Notes:**
- Use `Path.mkdir(parents=True, exist_ok=True)` for directory creation
- Use `Path.symlink_to()` for symlink creation
- Handle Windows compatibility (symlinks may require admin/developer mode)
- Template file should be readable and documented
- Follow shared patterns from `000-shared-patterns.md`

**Status:** In Progress