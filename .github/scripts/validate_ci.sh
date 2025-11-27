#!/bin/bash
# Script to validate CI/CD setup locally before pushing

set -e

echo "================================"
echo "CI/CD Validation Script"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must be run from project root"
    exit 1
fi

echo "✓ Running from project root"
echo ""

# Validate YAML syntax
echo "Checking GitHub Actions workflow syntax..."
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
echo "✓ YAML syntax is valid"
echo ""

# Check pytest markers are configured
echo "Checking pytest markers configuration..."
if grep -q "markers =" pyproject.toml; then
    echo "✓ Pytest markers are configured"
else
    echo "❌ Pytest markers not found in pyproject.toml"
    exit 1
fi
echo ""

# List available markers
echo "Available pytest markers:"
python -m pytest --markers | grep -E "^  @pytest.mark.(windows|macos|linux|gui|slow|integration):" || true
echo ""

# Count tests by marker
echo "Test counts by marker:"
echo "  Total tests: $(python -m pytest --co -q 2>&1 | tail -1 | grep -oE '[0-9]+ selected' | grep -oE '[0-9]+')"
echo "  GUI tests: $(python -m pytest -m gui --co -q 2>&1 | tail -1 | grep -oE '[0-9]+ selected' | grep -oE '[0-9]+')"
echo "  Windows tests: $(python -m pytest -m windows --co -q 2>&1 | tail -1 | grep -oE '[0-9]+ selected' | grep -oE '[0-9]+')"
echo "  macOS tests: $(python -m pytest -m macos --co -q 2>&1 | tail -1 | grep -oE '[0-9]+ selected' | grep -oE '[0-9]+')"
echo "  Linux tests: $(python -m pytest -m linux --co -q 2>&1 | tail -1 | grep -oE '[0-9]+ selected' | grep -oE '[0-9]+')"
echo ""

# Run a quick smoke test
echo "Running quick smoke test..."
python -m pytest tests/unit/test_platform_utils.py -v --tb=short -q
echo "✓ Smoke test passed"
echo ""

# Check platform-specific tests
echo "Checking platform-specific tests..."
CURRENT_PLATFORM=$(python -c "import platform; print(platform.system())")
echo "  Current platform: $CURRENT_PLATFORM"

if [ "$CURRENT_PLATFORM" = "Darwin" ]; then
    echo "  Running macOS-specific tests..."
    python -m pytest -m macos -v --tb=short -q
elif [ "$CURRENT_PLATFORM" = "Linux" ]; then
    echo "  Running Linux-specific tests..."
    python -m pytest -m linux -v --tb=short -q
elif [ "$CURRENT_PLATFORM" = "Windows" ]; then
    echo "  Running Windows-specific tests..."
    python -m pytest -m windows -v --tb=short -q
fi
echo ""

echo "================================"
echo "✓ CI/CD validation complete!"
echo "================================"
echo ""
echo "Your CI/CD setup is ready. The following will run on GitHub Actions:"
echo "  - Tests on Ubuntu (Linux)"
echo "  - Tests on macOS"
echo "  - Tests on Windows"
echo "  - Code linting with ruff"
echo "  - Type checking with mypy"
echo "  - Coverage reporting"
echo ""
