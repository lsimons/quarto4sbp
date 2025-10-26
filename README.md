# quarto4sbp

Python tool for working with [quarto](https://quarto.org/) in [Schuberg Philis](https://schubergphilis.com/).

## Prerequisites

- **Python 3.13+** with `uv` package manager: try `brew install uv` on mac
- [quarto](https://quarto.org/) CLI installed: try `brew install quarto` on mac
- for PDF export:
  - **Mac OS X**
  - **Microsoft Office**:
    - **Microsoft PowerPoint** - for PDF export of presentations
    - **Microsoft Word** - for PDF export of documents

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
python install.py
```

This creates a `~/.local/bin/q4s` shim that runs the CLI from the project's venv.

After installation, you can use `q4s` directly:

```bash
q4s help
```

Ensure `~/.local/bin` is in your PATH. If not, add this to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

### q4s CLI Tool

The `q4s` CLI provides utilities for working with Quarto presentations and documents.

**Available Commands:**

```bash
# Show help
q4s help

# Create PowerPoint and Word documents (unified)
q4s new <directory>

# Create PowerPoint presentation
q4s new-pptx <directory>

# Create Word document
q4s new-docx <directory>

# Export all Office documents to PDF
q4s pdf

# Export PowerPoint files to PDF
q4s pdf-pptx

# Export Word documents to PDF
q4s pdf-docx
```

### Rendering Documents

Each created project includes a `render.sh` script that:
1. Renders the Quarto file (`.qmd`) to Office format (`.pptx` or `.docx`)
2. Exports the Office file to PDF

```bash
cd my-presentation
./render.sh
```

You can also run `q4s pdf` in any directory to convert files.

### Disable Word automatic link updates

If you get this dialog from Word on PDF conversion:

![word dialog to update links](docs/images/word-link-update-dialog.png)

You can disable automatic link updates in Word preferences:

![word preference to not auto-update links](docs/images/word-disable-automatic-link-update.png)

Step by step instructions:
- Open **Microsoft Word**
- Go to **Word** > **Preferences**
- Select **General**
- Uncheck **Update automatic links at open**

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

### Testing

Unit and integration tests are located in `tests/`. Run them using:

```bash
# Full test suite
uv run pytest

# Specific test file
uv run pytest tests/my_test_file.py

# With verbose output
uv run pytest -v

# With coverage report
uv run pytest --cov=quarto4sbp --cov-report=term-missing

# Check coverage meets minimum threshold (90%)
uv run pytest --cov=quarto4sbp --cov-report=term --cov-fail-under=90

# With integration tests (not for agents!)
RUN_INTEGRATION_TESTS=1 uv run pytest -v
```

### Test Coverage Requirements

- Minimum test coverage: 80%
- Coverage is enforced in CI - builds will fail if coverage drops below threshold
- Run coverage checks before creating PRs

### Type Checking

This project uses strict type checking with pyright. Run type checks using: `uv run pyright`.

All code must pass pyright checks with no errors or warnings before merging.
