"""
Pytest configuration and fixtures for the automation framework.

This module provides shared fixtures for test setup including browser configuration,
page objects, API clients, test data, and Allure reporting integration.
"""

import logging
import logging.config
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Generator

import pytest
import yaml
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page

from src.config.settings import get_settings
from src.core.reporting import get_allure_reporter
from src.core.types import TestContext
from src.utils.data_loader import get_user_credentials


def pytest_configure(config) -> None:
    """Configure pytest with logging and other settings."""
    # Configure logging
    logging_config_path = Path("src/config/logging.yaml")
    if logging_config_path.exists():
        with open(logging_config_path, "r") as f:
            logging_config = yaml.safe_load(f)

        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        logging.config.dictConfig(logging_config)
    else:
        # Fallback to basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        )


@pytest.fixture(scope="session")
def settings():
    """Provide application settings for tests."""
    return get_settings()


@pytest.fixture(scope="function")
def test_context() -> TestContext:
    """
    Provide test execution context with correlation ID.

    Returns:
        TestContext: Test context with unique correlation ID and metadata
    """
    correlation_id = str(uuid.uuid4())[:8]
    test_name = os.environ.get("PYTEST_CURRENT_TEST", "unknown_test")

    context = TestContext(
        correlation_id=correlation_id, test_name=test_name, start_time=time.time()
    )

    return context


@pytest.fixture(scope="function")
def browser_context(
    browser: Browser, settings
) -> Generator[BrowserContext, None, None]:
    """
    Provide a browser context with proper configuration.

    Args:
        browser: Playwright browser instance
        settings: Application settings

    Yields:
        BrowserContext: Configured browser context
    """
    context = browser.new_context(
        viewport={
            "width": settings.browser.viewport_width,
            "height": settings.browser.viewport_height,
        },
        record_video_dir="test-results/videos" if settings.browser.video else None,
    )

    # Set up request interception for better error handling
    context.set_default_timeout(settings.saucedemo.page_timeout)

    yield context

    # Cleanup
    context.close()


@pytest.fixture(scope="function")
def page(
    browser_context: BrowserContext, test_context: TestContext
) -> Generator[Page, None, None]:
    """
    Provide a page instance with enhanced error handling.

    Args:
        browser_context: Browser context
        test_context: Test execution context

    Yields:
        Page: Configured page instance
    """
    page = browser_context.new_page()

    # Set up console logging
    page.on(
        "console",
        lambda msg: logging.getLogger("browser.console").info(
            f"[{msg.type}] {msg.text}"
        ),
    )

    # Set up page error handling
    page.on(
        "pageerror",
        lambda error: logging.getLogger("browser.error").error(f"Page error: {error}"),
    )

    yield page

    # Cleanup and error handling
    try:
        # Take screenshot on test failure
        if (
            hasattr(test_context, "result")
            and test_context.result
            and test_context.result == "FAILED"
        ):
            screenshot_path = (
                f"test-results/screenshots/{test_context.correlation_id}_final.png"
            )
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
    except Exception as e:
        logging.error(f"Failed to take final screenshot: {str(e)}")
    finally:
        page.close()


@pytest.fixture(scope="session")
def api_request_context(playwright) -> Generator[APIRequestContext, None, None]:
    """
    Provide an API request context for HTTP testing.

    Args:
        playwright: Playwright instance

    Yields:
        APIRequestContext: API request context
    """
    settings = get_settings()

    request_context = playwright.request.new_context(
        base_url=settings.airportgap.base_url,
        timeout=settings.airportgap.api_timeout,
        extra_http_headers={"User-Agent": "Playwright-Automation-Framework/1.0"},
    )

    yield request_context

    # Cleanup
    request_context.dispose()


@pytest.fixture(scope="function")
def standard_user_credentials():
    """
    Provide standard user credentials for SauceDemo.

    Returns:
        Dict[str, str]: User credentials with username and password
    """
    return get_user_credentials("standard_user")


@pytest.fixture(scope="function")
def logged_in_user(
    page: Page, test_context: TestContext, standard_user_credentials: Dict[str, str]
) -> None:
    """
    Fixture that logs in a standard user before the test.

    This fixture navigates to the login page, performs login with standard
    user credentials, and ensures the user is on the inventory page.

    Args:
        page: Page instance
        test_context: Test execution context
        standard_user_credentials: User credentials
    """
    from src.pages.login_page import LoginPage

    login_page = LoginPage(page, test_context)
    login_page.navigate_to_login()
    login_page.login(
        username=standard_user_credentials["username"],
        password=standard_user_credentials["password"],
    )


@pytest.fixture(scope="function")
def allure_reporter(test_context: TestContext):
    """
    Provide an Allure reporter instance for test reporting.

    Args:
        test_context: Test execution context

    Returns:
        AllureReporter: Configured Allure reporter
    """
    return get_allure_reporter(test_context)


@pytest.fixture(scope="function", autouse=True)
def setup_test_logging(test_context: TestContext):
    """
    Automatically set up test logging for each test.

    This fixture runs automatically for each test and sets up enhanced
    logging with correlation IDs and test metadata.

    Args:
        test_context: Test execution context
    """
    logger = logging.getLogger("test_execution")
    logger.info(
        f"Starting test: {test_context.test_name}",
        extra={"correlation_id": test_context.correlation_id},
    )

    yield

    # Update end time
    test_context.end_time = time.time()
    duration = test_context.duration or 0

    logger.info(
        f"Test completed: {test_context.test_name} (duration: {duration:.2f}s)",
        extra={"correlation_id": test_context.correlation_id},
    )


def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results for reporting.

    This hook captures test execution results and makes them available
    to fixtures for enhanced error handling and reporting.
    """
    if call.when == "call":
        # Get test context if available
        if hasattr(item, "funcargs") and "test_context" in item.funcargs:
            test_context = item.funcargs["test_context"]

            # Set test result
            if call.excinfo is None:
                test_context.result = "PASSED"
            else:
                test_context.result = "FAILED"
                test_context.error_message = (
                    str(call.excinfo.value) if call.excinfo else None
                )


def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "Playwright UI & API Automation Test Results"
