# 002 - q4s CLI Tool

**Status:** Deprecated - Echo command removed in favor of real functionality

**Purpose:** Create a simple CLI tool called `q4s` (quarto4sbp) with basic help subcommand as a foundation for future functionality

**Requirements:**
- Executable CLI tool named `q4s`
- `q4s help` subcommand to display usage information
- Follow dependency-free core philosophy (stdlib only: argparse, sys)
- Proper exit codes (0 for success, 1 for errors)
- Type hints for all functions
- Unit tests for subcommands

**Design Approach:**
- Main entry point: `quarto4sbp/cli.py` with `main()` function
- Use argparse with subparsers for extensibility
- `help` command shows available subcommands and usage
- Install as console script via pyproject.toml

**API Design:**
- `main(args: list[str] | None = None) -> int` - Entry point, returns exit code
- `cmd_help() -> int` - Handle help subcommand

**Implementation Notes:**
- See `000-shared-patterns.md` for CLI command patterns
- Main entry point uses argparse with subparsers for extensibility
- The echo command was removed once real functionality (new-pptx, new-docx, pdf-pptx, pdf-docx, new, pdf) was implemented

**History:**
- Initial implementation included an `echo` command as a placeholder
- Echo command removed after real functionality was added (new, new-pptx, new-docx, pdf, pdf-pptx, pdf-docx)