# Agent Instructions

This document provides instructions for AI code-generation agents.

Always follow the "Workflow for AI Agents" in the Issue Tracking section below. Create a bd issue BEFORE starting any work.

## Response Style

- Be concise in responses - avoid over-explaining changes.
- Focus on the specific task requested rather than extensive commentary.

## Project Overview

Python tool for working with [quarto](https://quarto.org/) in [Schuberg Philis](https://schubergphilis.com/).

**What it does:**
- Creates Quarto projects from templates (PowerPoint presentations, Word documents, or both)
- Automates PDF export from Office documents via AppleScript (macOS)
- Provides unified workflows for multi-format document creation
- Tracks staleness to avoid unnecessary re-exports

**Key commands:**
- `q4s new` - Create both PowerPoint and Word outputs from single source
- `q4s new-pptx` / `q4s new-docx` - Create format-specific projects
- `q4s pdf` - Export all Office documents to PDF
- `q4s pdf-pptx` / `q4s pdf-docx` - Export specific formats

**Architecture:**
- Dependency-free core (Python stdlib only)
- Template-based project creation with symlinked reference documents
- Double-extension PDF naming (`.pptx.pdf`, `.docx.pdf`) to preserve provenance
- AppleScript automation for Microsoft Office (requires PowerPoint/Word on macOS)

See [README.md](README.md) for usage examples and [DESIGN.md](DESIGN.md) for architectural decisions.

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Quick Start

**Check for ready work:**
```bash
bd ready --json
```

**Create new issues:**
```bash
bd create "Issue title" -t bug|feature|task -p 0-4 --json
bd create "Issue title" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**
```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**
```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Development Workflow

**ALWAYS FOLLOW THIS WORKFLOW FOR ALL TASKS:**

#### 1. Setup
- **Create issue FIRST**: `bd create "Task description" -t feature|bug|task|epic|chore -p 0-4 --json`
- **Create branch**: `git checkout -b <type>/descriptive-name`
  - Branch types: `feat/`, `fix/`, `refactor/`, `test/`, `docs/`, `chore/`
- **Claim task**: `bd update <id> --status in_progress --json`

#### 2. Implementation
- **Work on it**: Implement, test, document
- **For features/epics**:
  - there should usually be bd issues to make specs
  - even if the issue doesn't say so, big features and epics need a spec
  - after writing a spec, wait for human review before continuing
- **For refactoring**:
  - Create new directories/packages with `__init__.py` files
  - Split modules: Move functions/classes to separate files
  - Update imports: Ensure all imports point to new locations
  - Mirror test structure: Create matching test directories/files
  - Split tests: Move test classes to match new module structure
  - Run tests frequently to verify nothing breaks
- **Discover new work?** Create linked issue:
  - `bd create "Found bug" -p 1 --deps discovered-from:<parent-id> --json`

#### 3. Verification
- **Run tests**: `uv run pytest -v` (all tests must pass)
- **Run type checking**: `uv run pyright` (must have 0 errors, 0 warnings)
- **Run coverage**: `uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=80` (coverage must be ≥80%)

#### 4. Commit
- **For simple tasks/fixes**:
  ```bash
  git add -A
  git commit -m "<type>: issue-id - Brief description

  - Detailed change 1
  - Detailed change 2
  - All N tests passing"
  bd close <id> --reason "Completed. All tests passing (N/N)." --json
  ```

- **For refactoring**:
  ```bash
  git add -A
  git commit -m "refactor: issue-id - Brief description

  - Created package/subpackage/ structure
  - Moved function1() to package/subpackage/module1.py
  - Updated imports in main module
  - Split tests into matching structure
  - All N tests passing"
  ```

- **For epics/features** (continue to step 5 before closing)

#### 5. Pull Request (for epics, features, and refactoring)
- **Update spec status** (if applicable): Set to "Implemented" in spec file
- **Commit spec changes**: `git add -A && git commit -m "docs: Update spec-xxx status to Implemented"`
- **Push branch**: `git push -u origin <type>/descriptive-name`
- **Create PR**:
  ```bash
  gh pr create --title "<type>: issue-id - Brief description (spec-xxx)" \
    --body "## Summary

  Description of changes

  ## Changes
  - ✅ List of changes

  ## Testing
  All X tests passing

  ## Related
  - Issue: issue-id
  - Spec: spec-xxx (if applicable)"
  ```
- **Wait for CI**: `sleep 5 && gh pr checks --watch`
- **Fix any CI failures**:
  - If tests fail: fix and commit
  - If pyright fails: remove unused imports, add type hints, commit
  - Push fixes: `git push`
  - Wait for checks again: `sleep 5 && gh pr checks --watch`
- **Close the issue** once all checks pass:
  ```bash
  bd close issue-id --reason "Completed. All tests passing (X/X). PR #N ready for review." --json
  ```
- **Wait for PR review and merge** (human reviews and merges)

#### 6. After Merge
```bash
git checkout main
git pull
```

### Workflow Notes

**Task-Specific Guidance:**
- **Bugs/Small fixes**: Steps 1-4 (commit and close directly)
- **Refactoring**: Steps 1-6 (always use PR for structural changes)
- **Features**: Steps 1-6 (always use PR, update spec if applicable)
- **Epics**: Steps 1-6 (always use PR, update spec status, include test counts)

**Best Practices:**
- ✅ Keep work focused (one logical change at a time)
- ✅ Ensure tests mirror code structure (easier to find and maintain)
- ✅ Run tests after each significant change
- ✅ Commit atomically (one logical change per commit)
- ✅ Always wait for CI checks to pass before closing issues
- ✅ Fix CI failures immediately with clear commit messages
- ✅ Include test count and PR number in close reason for PRs
- ❌ Don't mix refactoring with feature additions or bug fixes
- ❌ Don't skip running tests until the end
- ❌ Don't close issues until all checks are green (for PRs)
- ❌ Don't merge PRs yourself (human review required)

### Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ **Create bd issue BEFORE starting work** (not after)
- ✅ **Update bd status BEFORE committing** (not after)
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems
- ❌ Do NOT start work without creating a bd issue first

## Building and Running

### Setup
```bash
# Create virtual environment
uv venv

# Install package in editable mode
uv pip install -e .

# Install q4s shim (optional but recommended)
python install.py
```

### Running
```bash
# With shim installed
q4s help
q4s new my-project

# Without shim
uv run q4s help
uv run q4s new my-project
```

### Testing
```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=80

# Type checking
uv run pyright
```

See [README.md](README.md) for detailed installation and usage instructions.



## Development Conventions

### Code Style

- **Typing**: The project uses strict type checking with `pyright`. All new code must be fully type-hinted.
- **Formatting**: Follow standard Python formatting guidelines (PEP 8).
- **Modularity**: Actions should be self-contained and independent.

### Commits

- Reference the relevant spec number in commit messages (e.g., `feat(actions): q4s-12 - implement organize-desktop action (spec-004)`).

- Reference the relevant beads issue number in commit messages (e.g., `feat(actions): q4s-12 - implement organize-desktop action (spec-004)`).

- Follow Conventional Commits, with types:
  - build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
  - ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
  - docs: Documentation only changes
  - feat: A new feature
  - fix: A bug fix
  - perf: A code change that improves performance
  - refactor: A code change that neither fixes a bug nor adds a feature
  - revert: undoing (an)other commit(s)
  - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
  - test: Adding missing tests or correcting existing tests
  - improvement: Improves code in some other way (that is not a feat or fix)
  - chore: Changes that take care of some other kind of chore that doesn't impact the main code

- Work with branches. Branches should be named based after the convention commit types, for example `feat/q4s-1-my-new-feature`, `fix/q4s-4-my-bugfix`, and `test/q4s-23-additional-tests-for-my-bugfix`.

### Specification Writing

- Focus on design decisions and rationale, not implementation details.
- Keep specs under 100 lines when possible - longer specs likely need splitting.
- Reference shared patterns (action scripts, testing, installation) rather than repeating.
- Include code only for critical design interfaces, not full implementations.
- Use bullet points for lists rather than verbose paragraphs.
- Eliminate sections that would be identical across multiple specs.

### Testing and Type Checking

**All code must pass testing and type checking before merging:**

```bash
# Run full test suite
uv run pytest -v

# Run type checking (must show 0 errors, 0 warnings)
uv run pyright
```

**Testing Requirements:**
- Write tests for all new functionality
- Ensure all tests pass locally before pushing
- Integration tests are preferred over mocking when practical
- Test files should mirror code structure (e.g., `tests/commands/test_feature.py` for `quarto4sbp/commands/feature.py`)
- Maintain minimum 80% test coverage - run `uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=80` before creating PRs

**Type Checking Requirements:**
- All code must have complete type annotations
- Pyright must pass with 0 errors and 0 warnings
- Use specific ignore comments only when necessary (see Diagnostic Handling below)
- CI enforces type checking - failing checks will block merging

### Diagnostic Handling

For diagnostic warnings, use specific Pyright ignore comments with error codes:
- `# pyright: ignore[reportAny]` for "Type is Any" warnings
- `# pyright: ignore[reportImplicitOverride]` for unittest method override warnings
- Use `_ = function_call()` assignment for unused return value warnings
- Always remove unused imports to avoid `reportUnusedImport` errors


## If Unsure

1. Re-read [AGENTS.md](AGENTS.md)
2. Look at an existing similar spec or action
3. Propose a tiny spec stub if direction unclear
4. Keep the PR small
