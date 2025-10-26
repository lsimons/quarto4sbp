# Design Decisions

This document captures key design decisions for the quarto4sbp project. For detailed feature specifications, see the [specs directory](docs/spec/).

## Core Philosophy
- **Dependency-free core**: Core functionality uses only Python3 standard library (os, sys, datetime, argparse, unittest)
- **Organized structure**: Main code in `quarto4sbp/`, tests in `tests/`, configuration in `etc/`
- **Functional approach**: Avoids OOP, uses simple functions for clarity and maintainability

## Quarto Integration
- **Template-based workflow**: Projects created from templates with reference documents
- **Multi-format support**: Single `.qmd` source can output to multiple formats (PowerPoint, Word)
- **Unified render script**: One `render.sh` template works for all formats, calls `quarto render` then `q4s pdf`
- **Symlinked references**: Template reference docs (`.pptx`, `.docx`) symlinked from central `templates/` directory

## PDF Export
- **AppleScript automation**: Use Microsoft Office apps (PowerPoint, Word) via AppleScript for PDF export (macOS)
- **Staleness detection**: Only export when source is newer than PDF or PDF doesn't exist
- **Double extension naming**: PDFs named `file.pptx.pdf` and `file.docx.pdf` to preserve provenance and prevent conflicts
- **Skip templates**: Exclude symlinks and files in `templates/` directory from export
- **Optional integration tests**: Real Office app tests marked with `@unittest.skipUnless(RUN_INTEGRATION_TESTS)`, skipped in CI

## File Naming & Conventions
- **Command naming**: Format-specific commands use suffixes (`new-pptx`, `pdf-docx`), unified commands omit suffix (`new`, `pdf`)
- **Project structure**: `<directory>/<directory>.qmd` pattern - QMD file named same as containing directory
- **Template files**: `simple-presentation.*` for PowerPoint, `simple-document.*` for Word
- **Double extensions**: Used for derived files to show transformation chain (`.pptx.pdf`, `.docx.pdf`)

## Error Handling & Reliability
- **Graceful degradation**: Continue execution when individual tasks fail, with clear error messages
- **Exit codes**: 0 for success/already-ran, 1 for errors, 2 for test failures
- **User-friendly errors**: Print descriptive messages, avoid stack traces for expected failures
- **File operations**: Create parent directories automatically, handle permissions gracefully
- **Subprocess calls**: Use `check=True` and catch `CalledProcessError` with context

## Testing Strategy
- **Integration-first**: Prefer end-to-end tests over mocking for reliability
- **Test separation**: Unit tests in dedicated `tests/` directory using Python's unittest framework
- **CLI testing**: Test both standalone execution and programmatic usage
- **Temporary directories**: Use temp paths for file system tests to avoid conflicts

## Code Quality
- **Type safety**: Comprehensive type annotations for better IDE support and static analysis
- **Acceptable diagnostics**: Some remaining warnings for argparse/unittest patterns that are inherently dynamic
- **Pyright ignores**: Use specific error codes (`reportAny`, `reportImplicitOverride`) when needed

## Development Process
- **Spec-driven development**: New features documented in `docs/spec/` before implementation
- **Concise specs**: Focus on design decisions, reference `000-shared-patterns.md`, avoid implementation details
- **Shared patterns**: Common code patterns, templates, and boilerplate documented once in `docs/spec/000-shared-patterns.md`
- **Design documentation**: This file updated with architectural decisions made during feature implementation
