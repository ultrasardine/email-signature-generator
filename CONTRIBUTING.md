# Contributing to Email Signature Generator

Thank you for your interest in contributing to the Email Signature Generator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Code Style Requirements](#code-style-requirements)
- [Testing Requirements](#testing-requirements)
- [Communication Channels](#communication-channels)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13 or higher**: Download from [python.org](https://www.python.org/downloads/)
- **Git**: For version control
- **uv** (recommended) or pip: For package management

### Finding Issues to Work On

- Check the [issue tracker](https://github.com/ultrasardine/email-signature-generator/issues) for open issues
- Look for issues labeled `good first issue` or `help wanted` if you're new to the project
- Feel free to ask questions on any issue before starting work

### Reporting Bugs

If you find a bug, please create an issue using the bug report template. Include:

- A clear description of the bug
- Steps to reproduce the behavior
- Expected behavior vs. actual behavior
- Your environment (OS, Python version)
- Screenshots if applicable

### Suggesting Features

We welcome feature suggestions! Please create an issue using the feature request template and include:

- A clear description of the problem you're trying to solve
- Your proposed solution
- Any alternative solutions you've considered
- Use cases and examples

## Development Setup

### Option 1: Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/ultrasardine/email-signature-generator.git
cd email-signature-generator

# Install uv if you haven't already
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies
uv sync

# Activate the virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/ultrasardine/email-signature-generator.git
cd email-signature-generator

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Platform-Specific Setup

#### Linux

Install required system packages:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-tk xvfb fonts-dejavu fonts-liberation

# Fedora/RHEL
sudo dnf install python3-tkinter dejavu-sans-fonts liberation-fonts

# Arch Linux
sudo pacman -S tk ttf-dejavu ttf-liberation
```

#### macOS

Tkinter is included with Python from python.org. If using Homebrew:

```bash
brew install python-tk@3.13
```

#### Windows

Tkinter is included with the standard Python installation. No additional setup required.

### Verify Installation

```bash
# Run tests to verify setup
uv run pytest

# Or with pip
pytest

# Run the application
python gui_main.py
```

## How to Contribute

### Workflow

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following our code style guidelines
5. **Write or update tests** for your changes
6. **Run the test suite** to ensure everything passes
7. **Commit your changes** with clear, descriptive commit messages
8. **Push to your fork**
9. **Create a pull request** to the main repository

### Commit Message Guidelines

Write clear, concise commit messages that explain what and why:

```
Add feature to export signatures as SVG

- Implement SVG export functionality in ImageRenderer
- Add SVG format option to GUI export dialog
- Update documentation with SVG export instructions

Closes #123
```

**Format:**
- Use the imperative mood ("Add feature" not "Added feature")
- First line: brief summary (50 characters or less)
- Blank line
- Detailed description if needed (wrap at 72 characters)
- Reference related issues

### Branch Naming

Use descriptive branch names:

- `feature/add-svg-export` - New features
- `fix/logo-scaling-bug` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/simplify-validation` - Code refactoring
- `test/add-property-tests` - Test additions

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest changes from `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all quality checks**:
   ```bash
   # Format code
   uv run black src tests

   # Run linter
   uv run ruff check src tests

   # Run type checker
   uv run mypy src

   # Run tests
   uv run pytest
   ```

   Or use the Makefile:
   ```bash
   make format
   make check
   make test
   ```

3. **Ensure all tests pass** on your local machine

4. **Update documentation** if you've changed functionality

5. **Add tests** for new features or bug fixes

### Submitting the Pull Request

1. Push your branch to your fork on GitHub
2. Go to the main repository and click "New Pull Request"
3. Fill out the pull request template completely
4. Link related issues using keywords (e.g., "Closes #123", "Fixes #456")
5. Request review from maintainers

### Pull Request Requirements

Your pull request must:

- **Pass all CI checks**: Tests must pass on Windows, macOS, and Linux
- **Maintain or improve code coverage**: Aim for 80%+ coverage
- **Follow code style guidelines**: Black formatting, ruff linting, mypy type checking
- **Include tests**: Unit tests and property-based tests where appropriate
- **Update documentation**: README, docstrings, and comments as needed
- **Have a clear description**: Explain what, why, and how

### Review Process

1. **Automated checks** run on all pull requests (CI/CD pipeline)
2. **Maintainer review**: A project maintainer will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, a maintainer will merge your PR
5. **Merge**: Your contribution becomes part of the project!

### After Your Pull Request is Merged

- Delete your feature branch (both locally and on GitHub)
- Update your local `main` branch:
  ```bash
  git checkout main
  git pull upstream main
  ```
- Celebrate! 🎉 You've contributed to open source!

## Code Style Requirements

We maintain high code quality standards using automated tools.

### Formatting: Black

All Python code must be formatted with [Black](https://github.com/psf/black):

```bash
# Format all code
uv run black src tests

# Check formatting without changes
uv run black --check src tests
```

**Configuration:**
- Line length: 100 characters
- Target version: Python 3.13

### Linting: Ruff

Code must pass [Ruff](https://github.com/astral-sh/ruff) linting:

```bash
# Run linter
uv run ruff check src tests

# Auto-fix issues where possible
uv run ruff check --fix src tests
```

**Rules enforced:**
- E: pycodestyle errors
- F: pyflakes
- I: isort (import sorting)
- N: pep8-naming
- W: pycodestyle warnings
- UP: pyupgrade

### Type Checking: Mypy

All code must include type hints and pass [Mypy](https://mypy-lang.org/) type checking:

```bash
# Run type checker
uv run mypy src
```

**Configuration:**
- Strict mode enabled
- Python version: 3.13
- All functions must have type annotations

**Example:**

```python
def generate_signature(data: SignatureData, config: SignatureConfig) -> Path:
    """Generate email signature image.

    Args:
        data: Signature data containing user information
        config: Configuration for signature generation

    Returns:
        Path to the generated signature image

    Raises:
        ValidationError: If data validation fails
        FileNotFoundError: If logo file not found
    """
    # Implementation
    pass
```

### Documentation

- **Docstrings**: All public functions, classes, and modules must have docstrings
- **Type hints**: All function parameters and return values must be type-annotated
- **Comments**: Use comments to explain complex logic, not obvious code
- **README**: Update README.md if you add features or change usage

### Code Organization

Follow the clean architecture structure:

```
src/email_signature/
├── domain/          # Business logic and models
├── application/     # Use cases and orchestration
├── infrastructure/  # External dependencies (file I/O, image processing)
└── interface/       # User interfaces (CLI, GUI)
```

## Testing Requirements

Comprehensive testing is mandatory for all contributions.

### Test Framework

We use [pytest](https://pytest.org/) for unit tests and [Hypothesis](https://hypothesis.readthedocs.io/) for property-based tests.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src/email_signature --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_validators.py

# Run specific test
uv run pytest tests/unit/test_validators.py::test_email_validation

# Run only unit tests
uv run pytest tests/unit/

# Run only property-based tests
uv run pytest tests/property/
```

Or use the Makefile:

```bash
make test           # All tests with coverage
make test-unit      # Unit tests only
make test-property  # Property-based tests only
make coverage       # Open HTML coverage report
```

### Writing Unit Tests

Unit tests verify specific examples and edge cases:

```python
import pytest
from src.email_signature.domain.validators import EmailValidator

def test_valid_email():
    """Test that valid email addresses are accepted."""
    validator = EmailValidator()
    assert validator.validate("user@example.com") is True

def test_invalid_email_missing_at():
    """Test that email without @ symbol is rejected."""
    validator = EmailValidator()
    with pytest.raises(ValidationError):
        validator.validate("userexample.com")

def test_empty_email():
    """Test that empty email is rejected."""
    validator = EmailValidator()
    with pytest.raises(ValidationError):
        validator.validate("")
```

### Writing Property-Based Tests

Property-based tests verify universal properties across many inputs:

```python
from hypothesis import given, strategies as st
from src.email_signature.domain.models import SignatureData

# Feature: open-source-standards, Property 1: Email validation is consistent
@given(st.emails())
def test_valid_emails_are_accepted(email: str):
    """For any valid email, the validator should accept it."""
    validator = EmailValidator()
    assert validator.validate(email) is True

# Feature: signature-generation, Property 2: Generated images have correct dimensions
@given(st.integers(min_value=100, max_value=1000))
def test_signature_dimensions(width: int):
    """For any valid width, generated signature should match specified dimensions."""
    config = SignatureConfig(width=width)
    signature = generate_signature(sample_data, config)
    image = Image.open(signature)
    assert image.width == width
```

**Property test requirements:**
- Run minimum 100 iterations (configured in pytest.ini)
- Include comment referencing design document property
- Use appropriate Hypothesis strategies
- Test universal properties, not specific examples

### Test Coverage

- **Minimum coverage**: 80% overall
- **New code**: 100% coverage for new features
- **Critical paths**: 100% coverage for validation, data processing, and file operations

View coverage report:

```bash
# Generate HTML coverage report
uv run pytest --cov=src/email_signature --cov-report=html

# Open in browser
make coverage
```

### Platform-Specific Tests

Mark platform-specific tests appropriately:

```python
import pytest
import platform

@pytest.mark.windows
def test_windows_font_loading():
    """Test font loading on Windows."""
    if platform.system() != "Windows":
        pytest.skip("Windows-only test")
    # Test implementation

@pytest.mark.linux
def test_linux_font_loading():
    """Test font loading on Linux."""
    if platform.system() != "Linux":
        pytest.skip("Linux-only test")
    # Test implementation
```

### GUI Tests

GUI tests require special handling:

```python
@pytest.mark.gui
def test_gui_validation():
    """Test GUI input validation."""
    # GUI test implementation
```

Run without GUI tests:

```bash
pytest -m "not gui"
```

## Communication Channels

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions, ideas, and general discussion
- **Pull Request Comments**: For code review and implementation questions

### Asking Questions

Before asking a question:

1. Check existing issues and discussions
2. Read the documentation (README, BUILDING.md, RELEASING.md)
3. Search the codebase for similar implementations

When asking a question:

- Be specific and provide context
- Include relevant code snippets or error messages
- Describe what you've already tried
- Be patient and respectful

### Reporting Security Issues

**Do not report security vulnerabilities through public GitHub issues.**

Please see [SECURITY.md](SECURITY.md) for instructions on responsibly disclosing security vulnerabilities.

## Project Governance

### Maintainers

The project is currently maintained by:

- **ultrasardine** - Project creator and lead maintainer

### Decision-Making Process

- **Pull requests**: Require approval from at least one maintainer
- **Major changes**: Discussed in issues before implementation
- **Breaking changes**: Require consensus and clear migration path

### Becoming a Maintainer

Maintainers are selected based on:

- Consistent, high-quality contributions over time
- Deep understanding of the codebase
- Positive community interactions
- Demonstrated commitment to the project

If you're interested in becoming a maintainer, start by making regular contributions and engaging with the community.

## Recognition

### Contributors

All contributors are recognized in the project. Your contributions, no matter how small, are valued and appreciated!

### Attribution

- Contributors are listed in GitHub's contributor graph
- Significant contributions may be highlighted in release notes
- Major contributors may be acknowledged in the README

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Thank You!

Thank you for contributing to the Email Signature Generator! Your efforts help make this project better for everyone. 🙏

---

**Questions?** Feel free to open an issue or start a discussion. We're here to help!
