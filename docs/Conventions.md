# Development Conventions and Standards

## Overview

This document outlines the coding standards, conventions, and best practices for the Playwright UI & API Automation Framework. These guidelines ensure consistency, maintainability, and quality across the entire codebase.

## Code Style and Formatting

### Python Style GuideYou are Cursor, acting as a senior QA automation engineer and repo bootstrapper. Build a complete Python-based automation project that includes:
- UI tests with Playwright
- API tests with Playwright’s APIRequestContext
- Allure reporting
- GitHub Actions CI that runs tests and publishes the Allure report to GitHub Pages
- Strong OOP, SOLID, and POM architecture
- Extensive logging, comments, and docstrings across all modules

Constraints and style:
- Python 3.11+
- Use pytest + pytest-playwright + allure-pytest
- Follow PEP8 and type-hint everything (mypy-clean)
- Use Page Object Model for all UI flows
- Clean separation of concerns: core, pages, tests, data, utils, config
- Add structured logging with logging.config from a YAML file
- Add rich docstrings (Google style) and inline comments explaining decisions
- Include pre-commit hooks for formatting and linting (black, isort, flake8, mypy)
- Keep test data in JSON/YAML fixtures
- Use environment variables and a typed settings module

Source material to analyze:
- Read the PDF placed at: docs/controlup-automation-home-test.pdf
  - The file describes: 2 UI tests against https://www.saucedemo.com and 3 API tests against https://airportgap.com (including the distance check KIX-NRT > 400 km)
  - Derive the SRD and STP from this, including numbered test cases that exactly match the scenarios and acceptance criteria

Deliverables to create in this repo:

1) Repository initialization
- Create .gitignore for Python, Playwright, macOS, Linux, Windows, venv, .pytest_cache, .mypy_cache, .venv, node_modules, allure-results, allure-report
- Create pyproject.toml with black, isort, flake8, mypy configs
- Create requirements.txt with:
  - pytest
  - pytest-playwright
  - playwright
  - allure-pytest
  - pydantic
  - pyyaml
  - requests (optional, but prefer Playwright API)
  - types-requests (if used)
  - mypy, black, isort, flake8, pre-commit
- **Create `.cursor/rules`** containing project-specific coding rules based on all requirements in this prompt, so future generations in Cursor follow the architecture, logging, typing, docstring, and testing standards you define here.
- Add README.md with quickstart, badges placeholders, and links to latest report on GitHub Pages
- Add Makefile with targets:
  - make install
  - make fmt
  - make lint
  - make type
  - make test-ui
  - make test-api
  - make test-all
  - make allure
  - make ci
- Add pytest.ini to configure markers, log formatting, and allure
- Add logging configuration at config/logging.yaml

2) docs/ directory and documentation set
- Place the provided assignment PDF here as docs/controlup-automation-home-test.pdf
- Create docs/SRD.md:
  - System context, scope, stack, constraints
  - Test environments and dependencies
  - Architectural overview of the test framework (modules, layers, interaction)
- Create docs/STP.md:
  - Numbered test cases for all 5 scenarios from the PDF
  - Preconditions, data sets, steps, expected results, and clean-up
  - Tagging scheme for test selection (e.g. smoke, api, ui)
  - Mapping between test cases and automated test files
- Create docs/Conventions.md:
  - POM rules, naming, package layout, logging standards, docstrings style
  - How to add a new page object or API test suite
- Ensure all docs are well cross-linked and contain code snippets

3) Source layout
Create the following structure and populate with working code:
- src/
  - config/
    - settings.py  (Typed Pydantic settings: base URLS, creds via env, timeouts)
    - logging.yaml  (Structured logging with handlers: console, file)
  - core/
    - base_page.py       (Abstract base class: waits, navigation, helpers)
    - base_api_client.py (Wrapper for Playwright APIRequestContext with helpers)
    - assertions.py      (Reusable assertions with rich messages)
    - reporting.py       (Allure helper utilities: attach text, JSON, screenshots)
    - types.py           (Typed aliases and dataclasses as needed)
  - pages/
    - login_page.py
    - inventory_page.py
    - cart_page.py
    - components/        (optional for small widgets)
  - api/
    - airports_client.py (GET /api/airports, POST /api/airports/distance)
    - models.py          (Typed response models if useful)
  - utils/
    - data_loader.py     (YAML/JSON fixtures)
    - env.py             (env helpers)
    - waits.py           (custom waiters if needed)
- tests/
  - ui/
    - test_inventory_list_count.py   (exactly 6 items after login)
    - test_add_first_item_to_cart.py (cart badge shows 1)
  - api/
    - test_airports_count.py         (exactly 30 airports)
    - test_airports_contains.py      (Akureyri, St. Anthony, CFB Bagotville present)
    - test_distance_kix_nrt.py       (distance > 400 km)
  - conftest.py
    - Fixtures for browser, context, page, api context, config injection
    - Session-level setup and teardown
    - Allure attachments on failure (screenshots, console logs, response bodies)
- testdata/
  - users.yaml  (standard_user credentials for SauceDemo)
  - api_expected.yaml  (expected airport names, counts, thresholds)

4) Implementation requirements
- UI:
  - Use POM with explicit locators, semantic methods (login, add_to_cart, get_inventory_count)
  - Make all waits explicit and resilient
  - Add screenshots on failure and after critical steps to Allure
- API:
  - Use Playwright’s request context
  - Validate schema minimally or strongly type with simple model parsing
  - Attach request and response bodies to Allure
- Logging:
  - Use structured logging with correlation IDs per test run
  - Log before and after each significant action, include timings
- Docstrings:
  - Every public class and method with a detailed Google-style docstring
- Comments:
  - Explain reasoning around tricky waits, selectors, or API assertions
- Typing:
  - Configure mypy in pyproject, aim for strict but pragmatic
- Markers:
  - @pytest.mark.ui and @pytest.mark.api
  - Allow -m "ui" or -m "api" selections

5) Allure integration and publishing to GitHub Pages
- Generate results with: pytest --alluredir=allure-results
- Generate HTML report with: allure generate allure-results -o allure-report --clean
- Create .github/workflows/ci.yml that:
  - Triggers on push and PR to main
  - Uses ubuntu-latest, sets up Python and Node (for Playwright)
  - Installs Python deps, runs: playwright install --with-deps
  - Runs make lint, make type, make test-all
  - Always generates the Allure report even if tests fail
  - Publishes the allure-report to gh-pages branch using peaceiris/actions-gh-pages
  - Preserves history folder to keep Allure trend charts:
    - Before generating, if gh-pages exists, copy previous allure-report/history into allure-results/history or into new report before publish
- Add a GitHub Pages link in README to the latest report

6) .cursor/rules content (must be generated by you for this project)
The `.cursor/rules` file should:
- Encode all architectural and style rules in this prompt
- Instruct Cursor to always:
  - Follow OOP, SOLID, POM
  - Add Google-style docstrings
  - Add structured logging to every method
  - Keep selectors centralized
  - Use type hints and keep mypy clean
  - Use environment variables and testdata files for creds
  - Never hardcode secrets
  - Maintain separation of concerns between core, pages, api, tests
  - Use Allure attachments for artifacts
  - Keep functions small and focused

7) Major and minor tasks list (tracking-ready)
Major 1 - Repo bootstrap
  1.1 Initialize repo, .gitignore, pyproject, requirements, pytest.ini, Makefile
  1.2 Set up pre-commit with black, isort, flake8, mypy and add .pre-commit-config.yaml
  1.3 Create base src/ layout (config, core, pages, api, utils), tests/ layout, testdata/
  1.4 Add logging config and typed settings

Major 2 - Documentation
  2.1 Save the assignment PDF to docs/controlup-automation-home-test.pdf
  2.2 Write docs/SRD.md describing system, architecture, and flow
  2.3 Write docs/STP.md with numbered test cases mapped to files
  2.4 Write docs/Conventions.md with style, POM, logging, typing
  2.5 Update README.md with quickstart and Pages link

Major 3 - UI automation (SauceDemo)
  3.1 Implement LoginPage, InventoryPage, CartPage with POM
  3.2 Implement test_inventory_list_count.py (expect 6 items)
  3.3 Implement test_add_first_item_to_cart.py (cart badge 1)
  3.4 Add screenshots and console logs to Allure on failure
  3.5 Harden waits and selectors

Major 4 - API automation (AirportGap)
  4.1 Implement Base API client and AirportsClient with request context
  4.2 test_airports_count.py (expect 30)
  4.3 test_airports_contains.py (expect 3 named airports)
  4.4 test_distance_kix_nrt.py (expect > 400 km)
  4.5 Attach requests/responses to Allure

Major 5 - Allure and CI/CD
  5.1 Integrate allure-pytest and commandline generation
  5.2 Configure GitHub Actions for tests and report generation
  5.3 Publish Allure to gh-pages with history retention
  5.4 Add project badges and Pages link to README

Major 6 - Quality gates
  6.1 Add and enforce markers ui and api
  6.2 Configure flake8, mypy strictness and fix warnings
  6.3 Add typing across all modules
  6.4 Add pre-commit and document contributor workflow

9) Nice-to-have (if time permits)
- Add retry for flaky tests via pytest-rerunfailures
- Add HTML summary artifact in CI with key metrics
- Add docker-compose for local run with node deps cached
- Add simple status badge linking to latest Allure report

Execution order:
- Perform Major 1, then 2, then 3 and 4 in parallel branches, then 5, then 6.
- As you implement, commit early and often with conventional commits.
- Validate everything locally with make test-all and make allure before pushing.

Now proceed to:
- Create all files and content above.
- Read docs/controlup-automation-home-test.pdf and generate SRD.md and STP.md with numbered test cases reflecting the PDF scenarios precisely.
- Implement tests and page objects accordingly.
- Generate `.cursor/rules` file based on the requirements above.
- Set up CI and verify Pages publishing to gh-pages.
- Ensure abundant logs, comments, and docstrings throughout.

**Base Standard:** PEP 8 with modifications for consistency and readability

**Line Length:** 88 characters (Black default)

**Indentation:** 4 spaces (no tabs)

**String Quotes:** Double quotes preferred for consistency

### Automated Formatting Tools

```bash
# Format code automatically
make fmt

# Check formatting
black --check src tests
isort --check-only src tests
```

**Configuration:**
- **Black**: Line length 88, Python 3.11 target
- **isort**: Black-compatible profile, multi-line output mode 3
- **Flake8**: Max line length 88, ignore E203, W503, E501

## Naming Conventions

### Files and Directories

```python
# Good: snake_case for all Python files
login_page.py
test_inventory_count.py
api_client_base.py

# Good: lowercase with underscores for directories
src/pages/
tests/ui/
testdata/
```

### Classes

```python
# Good: PascalCase for class names
class LoginPage(BasePage):
    pass

class AirportsClient(BaseAPIClient):
    pass

class TestInventoryCount:
    pass
```

### Functions and Methods

```python
# Good: snake_case for functions and methods
def wait_for_element(self, locator: str) -> None:
    pass

def get_inventory_count(self) -> int:
    pass

def test_airport_count_is_thirty():
    pass
```

### Variables and Constants

```python
# Good: snake_case for variables
user_credentials = get_test_user()
element_timeout = 5000

# Good: UPPER_SNAKE_CASE for constants
DEFAULT_TIMEOUT = 30000
MAX_RETRY_ATTEMPTS = 3
API_BASE_URL = "https://airportgap.com"
```

### Test Names

```python
# Good: Descriptive test names starting with 'test_'
def test_inventory_displays_exactly_six_items():
    pass

def test_adding_first_item_updates_cart_badge():
    pass

def test_airport_api_returns_thirty_airports():
    pass

def test_distance_between_kix_and_nrt_exceeds_400km():
    pass
```

## Type Hints and Documentation

### Type Annotations

**Required:** All public functions, methods, and class attributes must have type hints

```python
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page

# Good: Complete type annotations
def click_element(
    self, 
    locator: str, 
    timeout: Optional[int] = None,
    wait_before: bool = True
) -> None:
    """Click an element with optional waiting and timeout."""
    pass

def get_airports_data(self) -> List[Dict[str, Any]]:
    """Retrieve all airports data from the API."""
    pass

# Good: Typed class attributes
class TestContext:
    correlation_id: str
    test_name: str
    start_time: Optional[float] = None
```

### Docstring Standards

**Style:** Google-style docstrings for all public classes and methods

```python
def wait_for_element(
    self, 
    locator: str, 
    timeout: Optional[int] = None,
    state: str = "visible"
) -> None:
    """
    Wait for an element to reach the specified state.
    
    This method waits for an element identified by the locator to reach
    the specified state within the given timeout period. Supports various
    element states including visible, hidden, attached, and detached.
    
    Args:
        locator: CSS selector or XPath expression to identify the element
        timeout: Maximum wait time in milliseconds. Uses default if None
        state: Target element state (visible, hidden, attached, detached)
        
    Returns:
        None
        
    Raises:
        TimeoutError: If element doesn't reach expected state within timeout
        
    Example:
        >>> page.wait_for_element("#login-button", timeout=5000)
        >>> page.wait_for_element("//h1[@class='title']", state="visible")
    """
    pass
```

### Inline Comments

**Purpose:** Explain complex logic, business rules, or non-obvious decisions

```python
# Wait for network to be idle to ensure dynamic content is loaded
self.page.wait_for_load_state("networkidle")

# Use force click for elements that might be obscured by overlays
element.click(force=True)

# Correlation ID helps track test execution across logs and reports
self.logger = logging.LoggerAdapter(
    self.logger, 
    {"correlation_id": context.correlation_id}
)
```

## Page Object Model (POM) Standards

### Page Class Structure

```python
from abc import ABC, abstractmethod
from playwright.sync_api import Page
from src.core.base_page import BasePage
from src.core.types import TestContext

class InventoryPage(BasePage):
    """
    Page object for SauceDemo inventory/products page.
    
    This page handles all interactions with the main product listing
    including counting items, adding to cart, and navigation.
    """
    
    # Locators - grouped and clearly named
    INVENTORY_ITEMS = ".inventory_item"
    ADD_TO_CART_BUTTON = "[data-test^='add-to-cart']"
    CART_BADGE = ".shopping_cart_badge"
    PRODUCT_NAME = ".inventory_item_name"
    
    def __init__(self, page: Page, context: TestContext) -> None:
        super().__init__(page, context)
    
    @property
    def url_pattern(self) -> str:
        return "/inventory.html"
    
    @property
    def page_title(self) -> str:
        return "Swag Labs"
    
    # Action methods - clear, single responsibility
    def get_inventory_count(self) -> int:
        """Get the total number of inventory items displayed."""
        return self.get_elements_count(self.INVENTORY_ITEMS)
    
    def add_first_item_to_cart(self) -> None:
        """Add the first inventory item to the shopping cart."""
        first_add_button = f"{self.INVENTORY_ITEMS}:first-child {self.ADD_TO_CART_BUTTON}"
        self.click_element(first_add_button)
    
    def get_cart_badge_count(self) -> str:
        """Get the shopping cart badge count as displayed."""
        return self.get_text(self.CART_BADGE)
```

### Locator Management

**Strategy:** Keep locators as class constants, grouped logically

```python
class LoginPage(BasePage):
    # Form elements
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    
    # Error and status elements
    ERROR_MESSAGE = "[data-test='error']"
    ERROR_BUTTON = ".error-button"
    
    # Navigation elements
    MENU_BUTTON = "#react-burger-menu-btn"
    LOGOUT_LINK = "#logout_sidebar_link"
```

## API Client Standards

### Client Structure

```python
from typing import Dict, List, Any, Optional
from playwright.sync_api import APIRequestContext
from src.core.base_api_client import BaseAPIClient
from src.core.types import APIResponse, Airport

class AirportsClient(BaseAPIClient):
    """
    Client for interacting with the AirportGap API.
    
    Provides methods for retrieving airport information and calculating
    distances between airports. Handles authentication, error handling,
    and response parsing.
    """
    
    def __init__(self, request_context: APIRequestContext) -> None:
        super().__init__(request_context)
        self.base_url = self.settings.airportgap.base_url
    
    def get_all_airports(self) -> List[Airport]:
        """
        Retrieve all airports from the API.
        
        Returns:
            List[Airport]: List of airport objects with parsed data
            
        Raises:
            APIError: If request fails or response is invalid
        """
        response = self._make_request("GET", "/api/airports")
        airports_data = response.json_body.get("data", [])
        
        return [
            Airport(
                id=airport["id"],
                type=airport["type"],
                attributes=airport["attributes"]
            )
            for airport in airports_data
        ]
    
    def calculate_distance(
        self, 
        from_airport: str, 
        to_airport: str
    ) -> Dict[str, float]:
        """
        Calculate distance between two airports.
        
        Args:
            from_airport: Origin airport IATA code
            to_airport: Destination airport IATA code
            
        Returns:
            Dict[str, float]: Distance in kilometers, miles, and nautical miles
        """
        payload = {"from": from_airport, "to": to_airport}
        response = self._make_request("POST", "/api/airports/distance", json=payload)
        
        return response.json_body.get("data", {}).get("attributes", {})
```

## Logging Standards

### Logger Configuration

```python
import logging
from src.core.types import TestContext

class BasePage:
    def __init__(self, page: Page, context: TestContext) -> None:
        # Create logger with class context
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        
        # Add correlation ID for traceability
        self.logger = logging.LoggerAdapter(
            self.logger, 
            {"correlation_id": context.correlation_id}
        )
```

### Logging Levels and Messages

```python
# DEBUG: Detailed diagnostic information
self.logger.debug(f"Waiting for element '{locator}' to be {state}")

# INFO: General information about operations
self.logger.info(f"Navigating to URL: {url}")
self.logger.info(f"Login successful for user: {username}")

# WARNING: Something unexpected but recoverable
self.logger.warning(f"Element '{locator}' took {duration}s to load (expected < 2s)")

# ERROR: Error conditions that prevent operation completion
self.logger.error(f"Failed to click element '{locator}': {str(e)}")

# CRITICAL: Serious errors that may abort the test
self.logger.critical(f"Browser crashed during test execution: {str(e)}")
```

### Structured Logging

```python
# Good: Include relevant context in log messages
self.logger.info(
    "API request completed",
    extra={
        "method": "GET",
        "url": "/api/airports",
        "status_code": 200,
        "duration_ms": 245
    }
)

# Good: Log before and after important operations
self.logger.info(f"Starting test: {test_name}")
# ... test execution ...
self.logger.info(f"Test completed: {test_name}, result: {result}")
```

## Test Organization Standards

### Test File Structure

```python
"""
Test module for inventory functionality.

This module contains tests for the SauceDemo inventory page including
item counting, filtering, sorting, and add-to-cart operations.
"""

import pytest
from playwright.sync_api import Page
from src.pages.login_page import LoginPage
from src.pages.inventory_page import InventoryPage
from src.core.types import TestContext

@pytest.mark.ui
@pytest.mark.smoke
class TestInventoryDisplay:
    """Test class for inventory display functionality."""
    
    def test_inventory_displays_exactly_six_items(
        self, 
        page: Page, 
        test_context: TestContext,
        logged_in_user: None
    ) -> None:
        """
        Verify that exactly 6 items are displayed in the inventory.
        
        This test validates the core inventory display functionality
        by counting the number of products shown after login.
        """
        inventory_page = InventoryPage(page, test_context)
        inventory_page.verify_page_loaded()
        
        item_count = inventory_page.get_inventory_count()
        
        assert item_count == 6, f"Expected 6 items, but found {item_count}"
```

### Test Data Management

```python
# Good: Use fixtures for test data
@pytest.fixture
def standard_user_credentials():
    """Provide standard user credentials for testing."""
    return {
        "username": "standard_user",
        "password": "secret_sauce"
    }

# Good: Load test data from external files
@pytest.fixture
def expected_airports():
    """Load expected airport data from configuration."""
    from src.utils.data_loader import load_test_data
    return load_test_data("api_expected.yaml")["airportgap_api"]["airports"]
```

### Assertion Standards

```python
# Good: Clear, descriptive assertion messages
assert response.status_code == 200, (
    f"Expected status code 200, got {response.status_code}. "
    f"Response: {response.body}"
)

assert "Akureyri" in airport_names, (
    f"Airport 'Akureyri' not found in response. "
    f"Available airports: {airport_names}"
)

# Good: Use pytest's enhanced assertions where possible
from playwright.sync_api import expect

expect(page.locator("#cart-badge")).to_have_text("1")
expect(page).to_have_url("**/inventory.html")
```

## Error Handling Standards

### Exception Handling

```python
def click_element(self, locator: str) -> None:
    """Click an element with proper error handling."""
    try:
        self.wait_for_element(locator, state="visible")
        element = self.page.locator(locator)
        element.click()
        
        self.logger.debug(f"Successfully clicked element: {locator}")
        
    except TimeoutError as e:
        self.logger.error(f"Element '{locator}' not found within timeout: {str(e)}")
        self._take_screenshot("element_not_found")
        raise
        
    except Exception as e:
        self.logger.error(f"Unexpected error clicking element '{locator}': {str(e)}")
        self._take_screenshot("click_error")
        raise
```

### Custom Exceptions

```python
class FrameworkError(Exception):
    """Base exception for framework-specific errors."""
    pass

class PageLoadError(FrameworkError):
    """Raised when a page fails to load properly."""
    pass

class APIError(FrameworkError):
    """Raised when API requests fail or return unexpected responses."""
    
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
```

## Performance Guidelines

### Test Execution Optimization

```python
# Good: Use appropriate waits
def wait_for_page_load(self):
    # Wait for specific condition rather than arbitrary delays
    self.page.wait_for_load_state("networkidle")
    
# Avoid: Hard-coded sleep delays
import time
time.sleep(5)  # Bad - unreliable and slow
```

### Resource Management

```python
# Good: Context managers for resource cleanup
@pytest.fixture
def api_client(request_context):
    client = AirportsClient(request_context)
    yield client
    # Cleanup handled automatically by Playwright

# Good: Efficient element location
class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        # Cache frequently used locators
        self._inventory_items = page.locator(".inventory_item")
    
    def get_inventory_count(self) -> int:
        # Reuse cached locator
        return self._inventory_items.count()
```

## Security Considerations

### Credential Management

```python
# Good: Use environment variables for sensitive data
import os
from src.config.settings import get_settings

def get_api_key():
    return os.getenv("API_KEY") or get_settings().api.default_key

# Avoid: Hardcoded credentials in source code
API_KEY = "abc123"  # Bad - security risk
```

### Data Sanitization

```python
# Good: Sanitize data in logs
def log_api_response(self, response):
    sanitized_body = self._sanitize_sensitive_data(response.body)
    self.logger.info(f"API response: {sanitized_body}")

def _sanitize_sensitive_data(self, data):
    # Remove or mask sensitive information
    if isinstance(data, dict):
        return {k: "***" if "password" in k.lower() else v for k, v in data.items()}
    return data
```

## Adding New Components

### New Page Object Checklist

1. **Inherit from BasePage**: Ensure proper foundation
2. **Define locators**: Use class constants for selectors
3. **Implement abstract methods**: url_pattern and page_title
4. **Add logging**: Include debug and info logging
5. **Write docstrings**: Document purpose and usage
6. **Add type hints**: Complete type annotations
7. **Include error handling**: Proper exception handling
8. **Write tests**: Unit tests for page methods

### New API Client Checklist

1. **Inherit from BaseAPIClient**: Use framework foundation
2. **Define endpoints**: Clear method for each API operation
3. **Add response models**: Type-safe response handling
4. **Include error handling**: API-specific error handling
5. **Add logging**: Request/response logging
6. **Write docstrings**: Complete API documentation
7. **Add authentication**: If required by API
8. **Write tests**: Integration tests for client methods

### New Test Suite Checklist

1. **Choose appropriate markers**: @pytest.mark.ui or @pytest.mark.api
2. **Follow naming conventions**: Descriptive test method names
3. **Use fixtures**: Leverage existing fixtures for setup
4. **Add assertions**: Clear, descriptive assertions
5. **Include cleanup**: Proper test teardown
6. **Add documentation**: Test purpose and coverage
7. **Consider test data**: External test data where appropriate
8. **Verify in CI**: Ensure tests pass in continuous integration

## Code Review Guidelines

### Review Checklist

- [ ] **Code Style**: Follows Black/isort formatting
- [ ] **Type Hints**: Complete type annotations
- [ ] **Docstrings**: Google-style documentation
- [ ] **Logging**: Appropriate logging levels and messages
- [ ] **Error Handling**: Proper exception handling
- [ ] **Test Coverage**: Adequate test coverage for new code
- [ ] **Performance**: No unnecessary delays or inefficient operations
- [ ] **Security**: No hardcoded credentials or sensitive data
- [ ] **Documentation**: Updated documentation if needed
