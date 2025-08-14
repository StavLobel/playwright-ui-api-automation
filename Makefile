# Playwright UI/API Automation Framework
# Makefile for common development tasks

# Virtual environment activation (POSIX compatible)
VENV_ACTIVATE = if [ -d ".venv" ]; then . .venv/bin/activate; fi

# Default target
.PHONY: help
help:
	@echo "🚀 Playwright UI/API Automation Framework"
	@echo ""
	@echo "Available targets:"
	@echo "  install     - Install dependencies and setup environment"
	@echo "  fmt         - Format code with black and isort"
	@echo "  lint        - Run flake8 linting"
	@echo "  type        - Run mypy type checking"
	@echo "  test-ui     - Run UI tests only"
	@echo "  test-api    - Run API tests only"
	@echo "  test-smoke  - Run smoke tests only"
	@echo "  test-all    - Run all tests"
	@echo "  allure      - Generate and serve Allure report locally"
	@echo "  ci          - Run CI quality checks locally"
	@echo "  debug-ci-quality - Debug CI quality checks step by step"

# Install dependencies and setup environment
.PHONY: install
install:
	@echo "🔧 Installing dependencies..."
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && playwright install --with-deps
	@echo "✅ Installation complete!"

# Format code
.PHONY: fmt
fmt:
	@echo "🎨 Formatting code..."
	$(VENV_ACTIVATE) python -m black src tests
	$(VENV_ACTIVATE) python -m isort src tests
	@echo "✅ Code formatting complete!"

# Run linting
.PHONY: lint
lint:
	@echo "🔍 Running linting..."
	$(VENV_ACTIVATE) python -m flake8 src tests
	@echo "✅ Linting complete!"

# Run type checking
.PHONY: type
type:
	@echo "🔍 Running type checking..."
	$(VENV_ACTIVATE) python -m mypy src tests
	@echo "✅ Type checking complete!"

# Run UI tests only
.PHONY: test-ui
test-ui:
	@echo "🧪 Running UI tests..."
	$(VENV_ACTIVATE) python -m pytest tests/ui/ -m ui -v

# Run API tests only
.PHONY: test-api
test-api:
	@echo "🧪 Running API tests..."
	$(VENV_ACTIVATE) python -m pytest tests/api/ -m api -v

# Run smoke tests only
.PHONY: test-smoke
test-smoke:
	@echo "🧪 Running smoke tests..."
	$(VENV_ACTIVATE) python -m pytest tests/ -m smoke -v

# Run all tests
.PHONY: test-all
test-all:
	@echo "🧪 Running all tests..."
	$(VENV_ACTIVATE) python -m pytest tests/ -v

# Generate and serve Allure report locally
.PHONY: allure
allure:
	@echo "📊 Generating Allure report..."
	$(VENV_ACTIVATE) python -m pytest tests/ --alluredir=allure-results
	@echo "🌐 Starting Allure server..."
	$(VENV_ACTIVATE) allure serve allure-results

# Run CI quality checks locally
.PHONY: ci
ci:
	@echo "🔍 Running CI quality checks..."
	$(VENV_ACTIVATE) python -m black src tests
	$(VENV_ACTIVATE) python -m isort src tests
	$(VENV_ACTIVATE) python -m flake8 src tests
	$(VENV_ACTIVATE) python -m mypy src tests
	@echo "✅ All CI quality checks passed!"

# Debug CI quality checks locally (same as GitHub Actions CI)
.PHONY: debug-ci-quality
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

# Clean up generated files
.PHONY: clean
clean:
	@echo "🧹 Cleaning up generated files..."
	rm -rf allure-results/
	rm -rf allure-report/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Quick validation (format + lint + type)
.PHONY: validate
validate: fmt lint type
	@echo "✅ All validations passed!"

# Test specific markers with different browsers
.PHONY: test-ui-chromium
test-ui-chromium:
	@echo "🧪 Running UI tests with Chromium..."
	$(VENV_ACTIVATE) python -m pytest tests/ui/ -m ui --browser chromium -v

.PHONY: test-ui-firefox
test-ui-firefox:
	@echo "🧪 Running UI tests with Firefox..."
	$(VENV_ACTIVATE) python -m pytest tests/ui/ -m ui --browser firefox -v

.PHONY: test-ui-webkit
test-ui-webkit:
	@echo "🧪 Running UI tests with WebKit..."
	$(VENV_ACTIVATE) python -m pytest tests/ui/ -m ui --browser webkit -v

# Performance testing
.PHONY: test-performance
test-performance:
	@echo "⚡ Running performance tests..."
	$(VENV_ACTIVATE) python -m pytest tests/api/ -m "not slow" -v

# Security testing
.PHONY: test-security
test-security:
	@echo "🔒 Running security tests..."
	$(VENV_ACTIVATE) python -m pytest tests/ -m security -v

# Show test coverage
.PHONY: coverage
coverage:
	@echo "📊 Running tests with coverage..."
	$(VENV_ACTIVATE) python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "🌐 Coverage report generated in htmlcov/"

# Install development dependencies
.PHONY: install-dev
install-dev: install
	@echo "🔧 Installing development dependencies..."
	$(VENV_ACTIVATE) pip install pre-commit
	$(VENV_ACTIVATE) pre-commit install
	@echo "✅ Development setup complete!"

# Update dependencies
.PHONY: update-deps
update-deps:
	@echo "🔄 Updating dependencies..."
	$(VENV_ACTIVATE) pip install --upgrade -r requirements.txt
	@echo "✅ Dependencies updated!"
