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

# Install dependencies
install:
	pip install -r requirements.txt

# Setup development environment
setup: install
	pre-commit install
	playwright install --with-deps

# Format code
fmt:
	black src tests
	isort src tests

# Run linting
lint:
	flake8 src tests

# Run type checking
type:
	mypy src tests

# Run UI tests only
test-ui:
	pytest -m ui --alluredir=allure-results

# Run API tests only
test-api:
	pytest -m api --alluredir=allure-results

# Run all tests
test-all:
	pytest --alluredir=allure-results

# Generate and serve Allure report
allure:
	allure generate allure-results -o allure-report --clean
	@echo "Report generated in allure-report/"
	@echo "To serve report: allure serve allure-results"

# Clean temporary files
clean:
	rm -rf allure-results/ allure-report/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# CI pipeline
ci: lint type test-all allure
