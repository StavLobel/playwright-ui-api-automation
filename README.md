# Playwright UI & API Automation Framework

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Playwright](https://img.shields.io/badge/playwright-1.37+-green.svg)
![Pytest](https://img.shields.io/badge/pytest-7.4+-yellow.svg)
![Allure](https://img.shields.io/badge/allure-2.13+-purple.svg)

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

## 📊 Features

- **Dual Testing**: UI browser automation + API testing
- **Rich Reporting**: Allure reports with screenshots, logs, trends
- **CI/CD Ready**: GitHub Actions with automatic report publishing
- **Quality Gates**: Pre-commit hooks (Black, isort, Flake8, MyPy)
- **Environment Support**: Local, CI, staging configurations

## 📚 Documentation

- [System Requirements Document (SRD)](docs/SRD.md)
- [System Test Plan (STP)](docs/STP.md) 
- [Development Conventions](docs/Conventions.md)

## 🔗 Links

- **Test Reports**: [GitHub Pages](https://username.github.io/playwright-ui-api-automation)
- **CI/CD Pipeline**: [GitHub Actions](https://github.com/username/playwright-ui-api-automation/actions)

---

**Built with ❤️ using Playwright, Python, and modern DevOps practices**