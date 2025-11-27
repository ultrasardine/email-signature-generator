# GitHub Actions CI/CD

This directory contains the GitHub Actions workflows for continuous integration and testing.

## Workflows

### test.yml - Cross-Platform Testing

This workflow runs the test suite on all three supported platforms:
- **Ubuntu Latest** (Linux)
- **macOS Latest**
- **Windows Latest**

#### Features

1. **Multi-Platform Matrix**: Tests run in parallel on all three platforms
2. **Python 3.13**: Uses the required Python version
3. **System Dependencies**: Automatically installs platform-specific dependencies
   - Linux: `python3-tk` and `xvfb` for headless GUI testing
   - macOS: tkinter included with Python
   - Windows: tkinter included with Python
4. **Headless GUI Testing**: Uses `xvfb` on Linux to run GUI tests without a display
5. **Code Quality**: Runs linting (ruff) and type checking (mypy)
6. **Coverage Reports**: Generates coverage reports and uploads to Codecov
7. **Test Artifacts**: Archives test results for 30 days

#### Triggers

The workflow runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual trigger via `workflow_dispatch`

#### Test Execution

**Linux (with xvfb for GUI tests):**
```bash
xvfb-run -a pytest --verbose --cov=src/email_signature --cov-report=term-missing --cov-report=xml
```

**macOS and Windows:**
```bash
pytest --verbose --cov=src/email_signature --cov-report=term-missing --cov-report=xml
```

## Running Tests Locally

### Run All Tests
```bash
pytest
```

### Run Tests for Specific Platform
```bash
# Run only Windows-specific tests
pytest -m windows

# Run only macOS-specific tests
pytest -m macos

# Run only Linux-specific tests
pytest -m linux
```

### Run GUI Tests
```bash
# Run all GUI tests
pytest -m gui

# Skip GUI tests
pytest -m "not gui"
```

### Run Tests on Linux Without Display
```bash
# Install xvfb
sudo apt-get install xvfb

# Run tests with xvfb
xvfb-run -a pytest
```

## Test Markers

The following pytest markers are available:

- `@pytest.mark.windows`: Windows-specific tests
- `@pytest.mark.macos`: macOS-specific tests
- `@pytest.mark.linux`: Linux-specific tests
- `@pytest.mark.gui`: Tests that require GUI/display
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.integration`: Integration tests

### Using Markers

```python
import pytest

@pytest.mark.windows
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_windows_feature():
    # Test Windows-specific functionality
    pass

@pytest.mark.gui
def test_gui_feature():
    # Test GUI functionality
    pass
```

## Platform-Specific Test Skipping

Tests automatically skip on incompatible platforms using `pytest.mark.skipif`:

```python
@pytest.mark.windows
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_image_generation_on_windows():
    # This test only runs on Windows
    pass
```

## Troubleshooting

### GUI Tests Fail on Linux

If GUI tests fail on Linux, ensure xvfb is installed and running:
```bash
sudo apt-get install xvfb
xvfb-run -a pytest -m gui
```

### Tests Fail on Specific Platform

Check the GitHub Actions logs for the specific platform to see detailed error messages.

### Coverage Reports Not Uploading

Ensure the `CODECOV_TOKEN` secret is set in the repository settings (if using private repository).

## Adding New Tests

When adding new tests:

1. **Platform-Specific Tests**: Add appropriate markers
   ```python
   @pytest.mark.windows
   def test_windows_feature():
       pass
   ```

2. **GUI Tests**: Add the `@pytest.mark.gui` marker
   ```python
   @pytest.mark.gui
   def test_gui_feature():
       pass
   ```

3. **Cross-Platform Tests**: No marker needed, they run on all platforms

4. **Update Documentation**: Update this README if adding new markers or workflows
