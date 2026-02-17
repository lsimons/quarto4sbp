# Agent Instructions for quarto4sbp

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

Python tool for [Quarto](https://quarto.org/) workflows at Schuberg Philis. Creates projects from templates and automates PDF export via AppleScript.

## Quick Reference

- **Setup**: `uv sync --all-groups`
- **Run**: `q4s help`, `q4s new my-project`, `q4s pdf`
- **Test**: `uv run pytest -v`
- **Lint**: `uv run ruff check . && uv run basedpyright`
- **Coverage**: `uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=80`

## Structure

CLI commands in `quarto4sbp/commands/`. Dependency-free core (Python stdlib only).

**Key commands:** `new`, `new-pptx`, `new-docx`, `pdf`, `pdf-pptx`, `pdf-docx`

See [README.md](README.md) for usage and [DESIGN.md](DESIGN.md) for architecture.

## Guidelines

**Code quality:**
- Full type annotations (basedpyright: 0 errors, 0 warnings)
- Minimum 80% test coverage
- Tests mirror code structure

**Specs:** Big features need a spec in `docs/spec/`. Wait for human review before implementing.

**Pyright ignores:** Use specific codes like `# pyright: ignore[reportAny]`

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `revert`, `improvement`, `chore`

**Branches:** `feat/my-feature`, `fix/my-bugfix`, `test/additional-tests`

## Session Completion

Work is NOT complete until `git push` succeeds.

1. **Quality gates** (if code changed):
   ```bash
   uv run ruff check . && uv run basedpyright
   uv run pytest
   ```

2. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

Never stop before pushing. If push fails, resolve and retry.
