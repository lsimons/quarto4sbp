# 004 - Install Script with q4s Shim

**Purpose:** Provide a user-friendly install script that creates a `~/.local/bin/q4s` shim to run the CLI from the project's venv, eliminating the need to type `uv run q4s` every time

**Requirements:**
- Install script creates `~/.local/bin/q4s` executable shim
- Shim automatically activates the project venv and runs `q4s` CLI
- Shim detects the correct project directory (where it was installed from)
- Handle case where `~/.local/bin` doesn't exist (create it)
- Inform user if `~/.local/bin` is not in PATH
- Follow dependency-free core philosophy (bash script + Python stdlib)
- Proper error handling if venv doesn't exist

**Design Approach:**
- Python install script: `install.py` in project root
- Generated shim: bash wrapper that sources venv and runs CLI
- Store project path in shim at install time (not runtime lookup)
- Check for venv existence before generating shim
- Use `~/.local/bin` following XDG Base Directory conventions
- Install script is idempotent (safe to run multiple times)

**Shim Design:**
- Bash script that activates project venv and runs CLI
- Stores absolute project path at install time
- Executable placed in `~/.local/bin/q4s`

**Install Script Behavior:**
- Verify current directory is project root
- Check `.venv` exists (error with helpful message if missing)
- Create `~/.local/bin` if needed
- Write shim with execute permissions
- Check if `~/.local/bin` in PATH and inform user

**Implementation Notes:**
- See `000-shared-patterns.md` for dependency-free philosophy
- Shim stores absolute path to avoid pwd-dependent behavior
- Install script is idempotent (safe to run multiple times)

**Status:** Implemented