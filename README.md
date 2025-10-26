# quarto4sbp

A lightweight tool for working with quarto in Schuberg Philis Context.

## Prerequisites

- **Python 3.13+** with `uv` package manager: try `brew install uv` on mac
- [quarto](https://quarto.org/) CLI installed: try `brew install quarto` on mac

## Installation

### Option 1: Install Shim (Recommended)

For convenient usage without typing `uv run` every time:

```bash
# Set up virtual environment
uv venv

# Install the package
uv pip install -e .

# Run the install script
python install.py
```

This creates a `~/.local/bin/q4s` shim that runs the CLI from the project's venv.

After installation, you can use `q4s` directly:

```bash
q4s help
q4s echo hello world
```

**Note:** Ensure `~/.local/bin` is in your PATH. If not, add this to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Option 2: Use with uv run

If you prefer not to install the shim:

```bash
# Set up virtual environment
uv venv

# Install the package
uv pip install -e .

# Run commands with uv
uv run q4s help
```

## Usage

### q4s CLI Tool

The `q4s` CLI provides simple utilities for working with quarto in Schuberg Philis context.

**Available Commands:**

```bash
# Show help
q4s help

# Echo back arguments (useful for testing)
q4s echo hello world
```

**Examples:**

```bash
# Display help message
$ q4s help
q4s - quarto4sbp CLI tool

Usage: q4s <command> [arguments]

Available commands:
  help       Show this help message
  echo       Echo back the command-line arguments

# Echo command
$ q4s echo hello world
hello world
```

**Note:** If you haven't installed the shim, use `uv run q4s` instead of `q4s`.

## Development

### Spec-Based Development

This project follows a spec-based development approach documented in [`docs/spec/`](docs/spec/).

### Beads issue tracking

This project uses [beads (bd)](https://github.com/steveyegge/beads) for issue tracking.

To install try `brew tap steveyegge/beads && brew install bd` on mac.

### Development Guidelines
- See [CLAUDE.md](CLAUDE.md) for Claude Code-specific guidance
- See [AGENTS.md](AGENTS.md) for development guidelines and agent instructions
- See [DESIGN.md](DESIGN.md) for architectural decisions and design rationale
- Reference spec numbers in commit messages during feature implementation
- Run tests after changes: `uv run pytest`

### Commits

### Git

Follow [Conventional Commits](https://conventionalcommits.org/) with types:

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

## Testing

Unit and integration tests are located in `tests/`. Run them using:

```bash
# Full test suite (recommended)
uv run pytest

# Specific test file
uv run pytest tests/my_test_file.py

# With verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=quarto4sbp --cov-report=term-missing

# Check coverage meets minimum threshold (80%)
uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=80
```

**Coverage Requirements:**
- Minimum test coverage: 80%
- Coverage is enforced in CI - builds will fail if coverage drops below threshold
- Run coverage checks before creating PRs

### Type Checking

This project uses strict type checking with pyright. Run type checks using:

```bash
# Run pyright type checking
uv run pyright

# Type checking is also enforced in CI
```

All code must pass pyright checks with no errors or warnings before merging.
