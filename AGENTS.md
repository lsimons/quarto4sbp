# Agent Instructions

This document provides instructions for AI code-generation agents to ensure consistent and high-quality contributions to the `quarto4sbp` project.

**⚠️ CRITICAL: Always follow the "Workflow for AI Agents" in the Issue Tracking section below. Create a bd issue BEFORE starting any work.**

## Response Style

- Be concise in responses - avoid over-explaining changes.
- Focus on the specific task requested rather than extensive commentary.

## Project Overview

TODO

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

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

### Workflow for AI Agents

**ALWAYS FOLLOW THIS WORKFLOW:**

1. **Create issue FIRST**: `bd create "Task description" -t feature|bug|task|epic -p 0-4 --json`
2. **Create feature branch**: `git checkout -b feat/descriptive-name` (or `fix/`, `refactor/`, etc.)
3. **Claim your task**: `bd update <id> --status in_progress --json`
4. **Work on it**: Implement, test, document
5. **Discover new work?** Create linked issue:
   - `bd create "Found bug" -p 1 --deps discovered-from:<parent-id> --json`
6. **Run tests**: `uv run pytest -v` (all tests must pass)
7. **Run type checking**: `uv run pyright` (must have 0 errors, 0 warnings)
8. **Run tests with coverage**: `uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=80` (coverage must be ≥80%)
9. **Commit everything**: `git add -A && git commit -m "..."` (includes `.beads/issues.jsonl`)
10. **For epics, create PR**: 
   - Push: `git push -u origin branch-name`
   - Create PR: `gh pr create --title "..." --body "..."`
   - Wait for CI: `gh pr checks --watch`
   - Fix any CI failures and push fixes
11. **Close the issue**: `bd close <id> --reason "Description of what was done" --json`

### Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### MCP Server (Recommended)

If using Claude or MCP-compatible clients, install the beads MCP server:

```bash
pip install beads-mcp
```

Add to MCP config (e.g., `~/.config/claude/config.json`):
```json
{
  "beads": {
    "command": "beads-mcp",
    "args": []
  }
}
```

Then use `mcp__beads__*` functions instead of CLI commands.

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

For more details, see README.md.

## Building and Running

TODO

## Refactoring Workflow

When refactoring code (splitting modules, reorganizing structure, etc.), follow this workflow:

### 1. Plan the Refactoring
- Identify what needs to be split/reorganized
- Determine the target structure (e.g., `package/commands/` for command modules)
- Ensure tests will mirror the code structure

### 2. Create Feature Branch
```bash
git checkout -b refactor/descriptive-name
```

### 3. File bd Issue FIRST
```bash
bd create "Refactor: Brief description of what's being refactored" \
  --description "Detailed description including what files are being split/moved" \
  -t task -p 2 --json
```

### 4. Perform the Refactoring
- **Create new directories/packages** with `__init__.py` files
- **Split modules**: Move functions/classes to separate files
- **Update imports**: Ensure all imports point to new locations
- **Mirror test structure**: Create matching test directories/files
- **Split tests**: Move test classes to match new module structure
- **Run tests frequently**: Verify nothing breaks during refactoring

Example pattern for splitting commands:
- Code: `package/commands/feature.py` (contains `cmd_feature()`)
- Test: `tests/commands/test_feature.py` (contains `TestCmdFeature`)
- Package exports: `package/commands/__init__.py` imports and exports all commands

### 5. Verify Everything Works
```bash
python -m pytest tests/ -v  # All tests pass
# Run any integration tests
# Check diagnostics if applicable
```

### 6. Commit the Work
```bash
git add -A
git commit -m "refactor: Split X into separate modules (issue-id)

- Created package/subpackage/ structure
- Moved function1() to package/subpackage/module1.py
- Moved function2() to package/subpackage/module2.py
- Updated imports in main module
- Split tests into tests/subpackage/test_module1.py and test_module2.py
- Refactored tests/test_main.py to focus on integration
- All N tests passing"
```

### 7. Close bd Issue
```bash
bd close issue-id --reason "Completed refactoring, all tests passing"
```

### 8. Push and Create PR
```bash
git push origin refactor/descriptive-name
gh pr create --title "Refactor: Brief description (issue-id)" \
  --body "Summary of changes, testing status, benefits"
```

### 9. After Merge
```bash
git checkout main
git pull
```

### Refactoring Best Practices
- ✅ Keep the refactoring focused (one structural change at a time)
- ✅ Ensure tests mirror code structure (easier to find and maintain)
- ✅ Run tests after each significant change
- ✅ Commit atomically (one logical refactoring per commit)
- ✅ Document benefits in PR (organization, maintainability, extensibility)
- ❌ Don't mix refactoring with feature additions or bug fixes
- ❌ Don't skip running tests until the end
- ❌ Don't forget to update imports everywhere

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
</text>


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


### Epic Completion Workflow

When completing an epic (large feature), follow this extended workflow:

1. **Implement the feature** following the standard workflow above
2. **Update spec status** to "Implemented" in the spec file
3. **Commit all changes** including spec status update
4. **Push the branch**: `git push -u origin feat/branch-name`
5. **Create Pull Request**:
   ```bash
   gh pr create --title "feat: issue-id - Brief description (spec-xxx)" \
     --body "## Summary
   
   Description of changes
   
   ## Changes
   - ✅ List of changes
   
   ## Testing
   All X tests passing
   
   ## Related
   - Epic: issue-id
   - Spec: spec-xxx"
   ```
6. **Wait for CI checks**: `gh pr checks --watch`
7. **Fix any CI failures**:
   - If tests fail: fix and commit
   - If pyright fails: remove unused imports, add type hints, commit
   - Push fixes: `git push`
   - Wait for checks again: `gh pr checks --watch`
8. **Close the epic** once all checks pass:
   ```bash
   bd close issue-id --reason "Completed. All tests passing (X/X). PR #N ready for review." --json
   ```
9. **Wait for PR review and merge** (human reviews and merges)

**Important Notes:**
- ✅ Always wait for CI checks to pass before considering work complete
- ✅ Fix CI failures immediately with clear commit messages
- ✅ Don't close the epic until all checks are green
- ✅ Include test count and PR number in close reason
- ❌ Don't merge PRs yourself (human review required)

## If Unsure

1. Re-read [AGENTS.md](AGENTS.md)
2. Look at an existing similar spec or action
3. Propose a tiny spec stub if direction unclear
4. Keep the PR small
