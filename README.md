# Playwright UI & API Automation Framework

[![CI/CD Pipeline](https://github.com/StavLobel/playwright-ui-api-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/StavLobel/playwright-ui-api-automation/actions/workflows/ci.yml)
[![Test Reports](https://img.shields.io/badge/📊%20Allure-Reports-blue?style=flat&logo=github)](https://stavlobel.github.io/playwright-ui-api-automation/)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.41+-green.svg?logo=playwright)](https://playwright.dev/)
[![Pytest](https://img.shields.io/badge/pytest-8.0+-yellow.svg?logo=pytest)](https://pytest.org/)
[![Allure](https://img.shields.io/badge/allure-2.15+-purple.svg?logo=allure)](https://docs.qameta.io/allure/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive Python-based automation testing framework combining UI and API testing with Playwright, featuring advanced reporting with Allure and seamless CI/CD integration.

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
make install

# Setup development environment
make setup

# Run all tests
make test-all

# Generate Allure report
make allure
```

### Running Tests
```bash
# UI tests only
make test-ui

# API tests only
make test-api

# Smoke tests
pytest -m smoke

# CI pipeline
make ci
```

## 🧪 Test Coverage

### UI Tests (SauceDemo)
- **TC-UI-001**: Verify inventory displays exactly 6 items after login
- **TC-UI-002**: Verify adding first item to cart updates badge to "1"

### API Tests (AirportGap)
- **TC-API-001**: Verify API returns exactly 30 airports
- **TC-API-002**: Verify specific airports are present (Akureyri, St. Anthony, CFB Bagotville)
- **TC-API-003**: Verify distance between KIX and NRT exceeds 400km

## 🏗️ Architecture

Built with:
- **Page Object Model (POM)** for UI tests
- **SOLID principles** for maintainability
- **Type safety** with MyPy
- **Structured logging** with correlation IDs
- **Allure reporting** with GitHub Pages

## ✨ Key Features

### 🧪 **Comprehensive Testing**
- **UI Testing**: Cross-browser automation (Chromium, Firefox, WebKit)
- **API Testing**: REST API validation with request/response logging
- **Parallel Execution**: Multi-browser test execution for faster feedback
- **Smart Waiting**: Explicit waits with custom timeout strategies

### 📊 **Advanced Reporting**
- **Allure Integration**: Interactive test reports with rich visualizations
- **Screenshot Capture**: Automatic screenshots on test failures
- **Performance Metrics**: Response time tracking and trend analysis
- **Historical Data**: Test execution trends and stability metrics

### 🚀 **CI/CD Excellence**
- **GitHub Actions**: Automated testing on every push and PR
- **Multi-Browser Testing**: Parallel execution across different browsers
- **GitHub Pages**: Automatic report publishing with history retention
- **Quality Gates**: Automated code quality checks and validation

### 🛡️ **Code Quality**
- **Type Safety**: Full MyPy type checking for reliability
- **Code Formatting**: Automated formatting with Black and isort
- **Linting**: Flake8 linting for code quality standards
- **Pre-commit Hooks**: Quality gates before every commit

### 🏗️ **Architecture**
- **SOLID Principles**: Clean, maintainable, and extensible code
- **Page Object Model**: Structured UI automation with reusable components
- **Structured Logging**: Correlation ID tracking and detailed execution logs
- **Environment Flexibility**: Support for local, CI, and staging environments

## 📚 Documentation

- [System Requirements Document (SRD)](docs/SRD.md)
- [System Test Plan (STP)](docs/STP.md)
- [Development Conventions](docs/Conventions.md)

## 🔗 Links

- **📊 Test Reports**: [Allure Reports on GitHub Pages](https://stavlobel.github.io/playwright-ui-api-automation/)
- **🚀 CI/CD Pipeline**: [GitHub Actions](https://github.com/StavLobel/playwright-ui-api-automation/actions)
- **📁 Repository**: [GitHub](https://github.com/StavLobel/playwright-ui-api-automation)

---

**Built with ❤️ using Playwright, Python, and modern DevOps practices**
