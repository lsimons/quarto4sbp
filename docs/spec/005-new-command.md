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
- Create directory structure from PowerPoint template
- Symlink to reference document in `templates/`
- Generate render script from template
- Uses standard Quarto YAML frontmatter with pptx format

**Template Structure:**
- `simple-presentation.qmd` - QMD template with sample slides
- `simple-presentation.pptx` - PowerPoint reference document
- `render.sh.template` - Unified render script (see `000-shared-patterns.md`)

**Implementation Notes:**
- See `000-shared-patterns.md` for template creation command pattern
- Uses unified render script that works for both PowerPoint and Word formats
- Symlinks may require admin/developer mode on Windows

**Status:** Implemented