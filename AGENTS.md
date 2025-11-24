# Repository Guidelines

## Project Structure & Module Organization
- Core package in `src/cnairgapper` with CLI entrypoints under `cli/`, resource handlers in `images/`, `charts/`, and `repositories/`, configuration helpers in `config/`, and credential loading in `credentials/`.
- Domain models live in `src/cnairgapper/models` (configs, creds, scanners, resources) and are mostly pydantic-based for validation.
- Tests mirror the package layout under `tests/` (e.g., `tests/cli`, `tests/config`) and include sample fixtures in `tests/data`.
- Example configs and deployment aids sit in `templates/`, `docker/`, `k8s/`, and `docs/` for reference.

## Setup, Build, and Run
- Create a venv and install deps with uv: `uv venv && uv sync --frozen`.
- Run the CLI locally via `uv run airgapper --help` or invoke modules directly (`uv run python -m cnairgapper.main --config config.yaml`).
- Package builds use Hatch via `uv build` (wheel defined in `pyproject.toml`).

## Coding Style & Conventions
- Target Python 3.12+, type-hint everything, and prefer small, single-purpose functions.
- Ruff enforces linting; keep lines ≤100 chars and follow Google-style docstrings. Run `uv run ruff check .` before pushing.
- Mypy is configured in strict mode; ensure new code passes `uv run mypy src` and avoids `Any` unless necessary.
- Use snake_case for modules, functions, and variables; classes are PascalCase. Keep CLI flags descriptive and match existing `--kebab-case` patterns.

## Testing
- Add or update pytest cases alongside the code under test; name files `test_*.py` and use `pytest` markers strictly (see `pyproject.toml`).
- Run the suite with `uv run pytest`; prefer `requests_mock` for HTTP surfaces and use provided fixtures in `tests/data`.
- Cover error paths for registry/chart/git syncs and configuration validation; favor small, deterministic tests over integration-heavy ones.

## Commit & PR Guidelines
- Commit titles use conventional commits style. First line max 72 chars, then one blank line, then the rest as itemized list, 80 chars per line max.
- Keep commits focused and include relevant test updates. Avoid formatting-only commits unless paired with code changes.
- PRs should summarize behavior changes, link issues when applicable, and mention config or docs touched. Include CLI examples or screenshots when UX changes.

## Security & Configuration Tips
- Never commit secrets; use the credentials folder or env vars for registry/chart/git auth, and rely on `.ssh` mounts when running via Docker.
- Validate configs against `config.yaml` schema patterns and log minimally sensitive info (hostnames over tokens).
- Prefer least-privilege registry credentials when writing new sync flows or tests.
