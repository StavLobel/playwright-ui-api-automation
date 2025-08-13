.PHONY: help install setup fmt lint type test-ui test-api test-all allure clean ci

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies and setup project"
	@echo "  setup       - Setup pre-commit hooks and install Playwright browsers"
	@echo "  fmt         - Format code with black and isort"
	@echo "  lint        - Run flake8 linting"
	@echo "  type        - Run mypy type checking"
	@echo "  test-ui     - Run UI tests only"
	@echo "  test-api    - Run API tests only"
	@echo "  test-all    - Run all tests"
	@echo "  allure      - Generate and serve Allure report"
	@echo "  clean       - Clean temporary files and reports"
	@echo "  ci          - Run full CI pipeline (lint, type, test)"

# Detect if we're in a virtual environment or if .venv exists
VENV_ACTIVATE = $(shell if [ -f .venv/bin/activate ]; then echo ". .venv/bin/activate &&"; else echo ""; fi)

# Install dependencies
install:
	$(VENV_ACTIVATE) pip install -r requirements.txt

# Setup development environment
setup: install
	$(VENV_ACTIVATE) pre-commit install
	$(VENV_ACTIVATE) playwright install --with-deps

# Format code
fmt:
	$(VENV_ACTIVATE) python -m black src tests
	$(VENV_ACTIVATE) python -m isort src tests

# Run linting
lint:
	$(VENV_ACTIVATE) python -m flake8 src tests

# Run type checking
type:
	$(VENV_ACTIVATE) python -m mypy src tests

# Run UI tests only
test-ui:
	$(VENV_ACTIVATE) python -m pytest tests/ui/ --alluredir=allure-results

# Run API tests only
test-api:
	$(VENV_ACTIVATE) python -m pytest tests/api/ --alluredir=allure-results

# Run all tests
test-all:
	$(VENV_ACTIVATE) python -m pytest tests/ --alluredir=allure-results

# Generate Allure report
allure:
	export PATH="/opt/homebrew/opt/openjdk@11/bin:$$PATH" && allure generate allure-results -o allure-report --clean
	@echo "Report generated in allure-report/"
	@echo "To serve report: make serve or ./scripts/serve-allure.sh"

# Serve Allure report locally
serve:
	./scripts/serve-allure.sh

# Debug CI quality checks locally (same as GitHub Actions)
debug-ci-quality:
	@echo "🔍 Running the same quality checks as GitHub Actions CI..."
	@echo "📋 Step 1: Code formatting"
	$(VENV_ACTIVATE) python -m black src tests
	$(VENV_ACTIVATE) python -m isort src tests
	@echo "📋 Step 2: Linting"
	$(VENV_ACTIVATE) python -m flake8 src tests
	@echo "📋 Step 3: Type checking"
	$(VENV_ACTIVATE) python -m mypy src tests
	@echo "✅ All quality checks passed locally!"

# Clean temporary files
clean:
	rm -rf allure-results/ allure-report/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# CI pipeline
ci: lint type test-all allure
