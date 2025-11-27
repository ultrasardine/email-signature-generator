# Makefile for Email Signature Generator
# Provides convenient shortcuts for development and usage tasks

# ============================================================================
# Configuration Variables
# ============================================================================

# Python interpreter
PYTHON := python3

# Virtual environment paths
VENV := .venv
VENV_BIN := $(VENV)/bin

# Platform detection for Windows/Unix differences
ifeq ($(OS),Windows_NT)
    VENV_BIN := $(VENV)/Scripts
    PYTHON := python
    BROWSER := start
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        BROWSER := open
    else
        BROWSER := xdg-open
    endif
endif

# Tool paths (will be in virtual environment)
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
BLACK := $(VENV_BIN)/black
MYPY := $(VENV_BIN)/mypy
RUFF := $(VENV_BIN)/ruff

# Project directories
SRC_DIR := src
TEST_DIR := tests
TEST_UNIT_DIR := $(TEST_DIR)/unit
TEST_PROPERTY_DIR := $(TEST_DIR)/property

# ============================================================================
# Phony Targets Declaration
# ============================================================================

.PHONY: help install clean test test-unit test-property coverage
.PHONY: lint lint-fix format format-check typecheck check
.PHONY: run check-venv

# ============================================================================
# Default Target
# ============================================================================

.DEFAULT_GOAL := help

# ============================================================================
# Help Target
# ============================================================================

help: ## Display this help message
	@echo "Email Signature Generator - Available Make Targets"
	@echo "=================================================="
	@echo ""
	@echo "Development:"
	@echo "  make install        - Set up virtual environment and install dependencies"
	@echo "  make clean          - Remove generated files and caches"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests with coverage"
	@echo "  make test-unit      - Run only unit tests"
	@echo "  make test-property  - Run only property-based tests"
	@echo "  make coverage       - Open HTML coverage report in browser"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run ruff linter on source and tests"
	@echo "  make lint-fix       - Run ruff linter with auto-fix"
	@echo "  make format         - Format code with black"
	@echo "  make format-check   - Check code formatting without changes"
	@echo "  make typecheck      - Run mypy type checker"
	@echo "  make check          - Run all quality checks (format-check, lint, typecheck)"
	@echo ""
	@echo "Application:"
	@echo "  make run            - Run the email signature generator"
	@echo ""
	@echo "Help:"
	@echo "  make help           - Display this help message"
	@echo ""

# ============================================================================
# Utility Targets
# ============================================================================

check-venv: ## Check if virtual environment exists
	@test -d $(VENV) || (echo "Error: Virtual environment not found. Run 'make install' first." && exit 1)

# ============================================================================
# Installation and Cleanup Targets
# ============================================================================

install: ## Set up virtual environment and install dependencies
	@echo "Setting up virtual environment..."
	@if [ ! -d $(VENV) ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "Virtual environment created at $(VENV)"; \
	else \
		echo "Virtual environment already exists at $(VENV)"; \
	fi
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using uv for package installation..."; \
		uv pip install -e ".[dev]" --python $(VENV_BIN)/python; \
	else \
		echo "Using pip for package installation..."; \
		$(PIP) install --upgrade pip; \
		$(PIP) install -e ".[dev]"; \
	fi
	@echo "Installation complete!"

clean: ## Remove generated files and caches
	@echo "Cleaning generated files and caches..."
	@rm -rf __pycache__
	@rm -rf $(SRC_DIR)/**/__pycache__
	@rm -rf $(TEST_DIR)/**/__pycache__
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf .hypothesis
	@rm -rf htmlcov
	@rm -f .coverage
	@rm -f email_signature.png
	@echo "Cleanup complete!"

# ============================================================================
# Testing Targets
# ============================================================================

test: check-venv ## Run all tests with coverage
	@echo "Running all tests with coverage..."
	$(PYTEST) $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"
	@echo "Run 'make coverage' to open the HTML report in your browser"

test-unit: check-venv ## Run only unit tests
	@echo "Running unit tests..."
	$(PYTEST) $(TEST_UNIT_DIR) -v

test-property: check-venv ## Run only property-based tests
	@echo "Running property-based tests..."
	$(PYTEST) $(TEST_PROPERTY_DIR) -v

coverage: ## Open HTML coverage report in browser
	@if [ ! -d htmlcov ]; then \
		echo "Error: Coverage report not found. Run 'make test' first to generate coverage report."; \
		exit 1; \
	fi
	@echo "Opening coverage report in browser..."
	$(BROWSER) htmlcov/index.html

# ============================================================================
# Code Quality Targets
# ============================================================================

lint: check-venv ## Run ruff linter on source and tests
	@echo "Running ruff linter..."
	$(RUFF) check $(SRC_DIR) $(TEST_DIR)

lint-fix: check-venv ## Run ruff linter with auto-fix
	@echo "Running ruff linter with auto-fix..."
	$(RUFF) check --fix $(SRC_DIR) $(TEST_DIR)

format: check-venv ## Format code with black
	@echo "Formatting code with black..."
	$(BLACK) $(SRC_DIR) $(TEST_DIR)

format-check: check-venv ## Check code formatting without changes
	@echo "Checking code formatting..."
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR)

typecheck: check-venv ## Run mypy type checker
	@echo "Running mypy type checker..."
	$(MYPY) $(SRC_DIR)

check: check-venv ## Run all quality checks (format-check, lint, typecheck)
	@echo "Running all code quality checks..."
	@echo ""
	@echo "1/3 Checking code formatting..."
	@$(MAKE) format-check
	@echo ""
	@echo "2/3 Running linter..."
	@$(MAKE) lint
	@echo ""
	@echo "3/3 Running type checker..."
	@$(MAKE) typecheck
	@echo ""
	@echo "All quality checks passed!"

# ============================================================================
# Application Targets
# ============================================================================

run: check-venv ## Run the email signature generator
	@echo "Starting email signature generator..."
	$(VENV_BIN)/python main.py

