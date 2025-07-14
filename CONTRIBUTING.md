# Contributing to Universal Airgapper

Thank you for your interest in contributing to the Universal Airgapper!
This document provides guidelines and information on how to contribute to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.
We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally: `git clone https://github.com/YOUR-USERNAME/universal-airgapper.git`
3. Create a branch for your changes: `git checkout -b task/your-feature-name`

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Docker (for testing container functionality)
- Git

### Setting Up Your Environment

1. Create a virtual environment:

``` bash
   python -m venv .venv
   source .venv/bin/activate
```

1. Install development dependencies:

``` bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
```

## Coding Standards

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Write docstrings for all functions, classes, and modules (Google notation)
- Include type hints where possible
- Keep functions focused on a single responsibility

We use pre-commit to test, lint, check,.. the code for compliance - please do so too!

- install pre-commit hooks: `pre-commit install && pre-commit install --hook-type commit-msg`
- run hooks before commit: `pre-commit run --all-files`

- [pre-commit tool](https://pre-commit.com/)
- [our pre-commit config](.pre-commit-config.yaml)

## Submitting Changes

1. Commit your changes with clear, descriptive commit messages
2. Push to your fork
3. Submit a pull request to the main repository
4. In your pull request, clearly describe:
    - What changes you've made
    - Why you've made them
    - Any potential side effects or considerations

### Commit Message Format

We use conventional commits that adhere to the following commit title pattern: `^(feat|fix|try|maintain)!?(\(.*\))?:
.+|^Merge branch.*`

This means commit messages must:

- Start with one of these types:
    - `feat`: A new feature
    - `fix`: A bug fix
    - `try`: Experimental changes
    - `maintain`: Maintenance tasks (refactoring, dependencies, etc.)

- Optionally include a scope in parentheses: `feat(ui):` or `fix(api):`
- Optionally include a breaking change indicator `!`: `feat!:` or `fix(api)!:`
- Include a descriptive message after the colon
- Merge commits are automatically formatted by Git

Examples of valid commit messages:

- `feat: add user authentication`
- `fix(login): resolve incorrect password handling`
- `maintain(deps): update dependencies`
- `feat!: completely redesign the UI`

## Testing

Please write tests for new features or bug fixes. We use `pytest` for testing:

``` bash
pytest
```

Before submitting a pull request, make sure:

- All existing tests pass
- You've added tests for new functionality

## Documentation

Update documentation when adding or modifying features:

- Update relevant README sections
- Update or create documentation in the `docs/` directory
- Include examples for new features
- Document any new CLI arguments

## Issue Reporting

When reporting issues, please use the issue template and include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Logs or error messages if applicable
