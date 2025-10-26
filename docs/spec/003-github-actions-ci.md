# 003 - GitHub Actions CI Workflows

**Purpose:** Automated CI workflows to ensure code quality on PRs and main branch merges

**Requirements:**
- Run linting and tests on all PRs and pushes to PR branches
- Run linting and tests on all merges to main branch
- Separate workflows for PR CI vs main branch CI for flexibility
- Use Python 3.13 as specified in pyproject.toml
- Support pytest for testing and pyright for type checking/linting

**Design Approach:**
- Two distinct workflow files: `pr-ci.yml` for PR checks, `main-ci.yml` for main branch
- Use uv for fast dependency management (project uses uv.lock)
- Run pyright for type checking (configured in pyproject.toml with strict mode)
- Run pytest for unit tests
- Both workflows use same job definitions but different triggers
- Cache dependencies to speed up runs

**Implementation Notes:**
- Workflows located in `.github/workflows/`
- PR workflow triggers on: `pull_request` (opened, synchronize, reopened)
- Main workflow triggers on: `push` to `main` branch
- Both run on `ubuntu-latest` with Python 3.13
- Install uv, sync dependencies, run pyright, run pytest
- Fail fast: if linting fails, don't run tests (save CI time)

**Status:** Approved