"""
Base page class providing common functionality for all page objects.

This module implements the foundation of the Page Object Model (POM) pattern,
providing reusable methods for element interactions, waits, and navigation
that are shared across all page classes.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Literal, Optional, Union

from playwright.sync_api import Page, expect

from src.config.settings import get_settings
from src.core.types import URL, Locator, TestContext


class BasePage(ABC):
    """
    Abstract base class for all page objects.

    This class provides common functionality for page interactions including
    element waits, navigation, screenshots, and logging. All page objects
    should inherit from this class to ensure consistent behavior.

    Attributes:
        page: Playwright page instance
        context: Test execution context
        settings: Application settings
        logger: Logger instance for this page
    """

    def __init__(self, page: Page, context: TestContext) -> None:
        """
        Initialize the base page.

        Args:
            page: Playwright page instance
            context: Test execution context with correlation ID and metadata
        """
        self.page = page
        self.context = context
        self.settings = get_settings()
        base_logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Add correlation ID to logger context
        self.logger: Union[
            logging.Logger, logging.LoggerAdapter
        ] = logging.LoggerAdapter(
            base_logger, {"correlation_id": context.correlation_id}
        )

    @property
    @abstractmethod
    def url_pattern(self) -> str:
        """
        URL pattern that identifies this page.

        Returns:
            str: URL pattern or path that identifies this page
        """
        pass

    @property
    @abstractmethod
    def page_title(self) -> str:
        """
        Expected page title for this page.

        Returns:
            str: Expected page title
        """
        pass

    def navigate_to(self, url: URL, wait_for_load: bool = True) -> None:
        """
        Navigate to the specified URL.

        Args:
            url: Target URL to navigate to
            wait_for_load: Whether to wait for page load completion

        Raises:
            TimeoutError: If page fails to load within timeout
        """
        self.logger.info(f"Navigating to URL: {url}")
        start_time = time.time()

        try:
            self.page.goto(url, timeout=self.settings.saucedemo.page_timeout)

            if wait_for_load:
                # Wait for network to be idle (no requests for 500ms)
                self.page.wait_for_load_state("networkidle")

            duration = time.time() - start_time
            self.logger.info(f"Navigation completed in {duration:.2f}s")

        except Exception as e:
            self.logger.error(f"Navigation failed to {url}: {str(e)}")
            self._take_screenshot("navigation_failed")
            raise

    def wait_for_element(
        self,
        locator: Locator,
        timeout: Optional[int] = None,
        state: Literal["attached", "detached", "hidden", "visible"] = "visible",
    ) -> None:
        """
        Wait for an element to reach the specified state.

        Args:
            locator: Element selector/locator
            timeout: Custom timeout in milliseconds (uses default if None)
            state: Element state to wait for (visible, hidden, attached, detached)

        Raises:
            TimeoutError: If element doesn't reach expected state within timeout
        """
        timeout_ms = timeout or self.settings.saucedemo.element_timeout

        self.logger.debug(
            f"Waiting for element '{locator}' to be {state} (timeout: {timeout_ms}ms)"
        )

        try:
            self.page.wait_for_selector(locator, timeout=timeout_ms, state=state)
            self.logger.debug(f"Element '{locator}' is now {state}")

        except Exception as e:
            self.logger.error(
                f"Element '{locator}' failed to reach state '{state}': {str(e)}"
            )
            self._take_screenshot("element_wait_failed")
            raise

    def click_element(
        self, locator: Locator, wait_before: bool = True, force: bool = False
    ) -> None:
        """
        Click on an element with optional waiting.

        Args:
            locator: Element selector/locator
            wait_before: Whether to wait for element visibility before clicking
            force: Whether to force click even if element is not actionable

        Raises:
            TimeoutError: If element is not found or not clickable
        """
        self.logger.debug(f"Clicking element: {locator}")

        try:
            if wait_before:
                self.wait_for_element(locator, state="visible")

            # Additional check that element is enabled
            element = self.page.locator(locator)
            if not force:
                expect(element).to_be_enabled()

            element.click(force=force)
            self.logger.debug(f"Successfully clicked element: {locator}")

        except Exception as e:
            self.logger.error(f"Failed to click element '{locator}': {str(e)}")
            self._take_screenshot("click_failed")
            raise

    def fill_text(self, locator: Locator, text: str, clear_first: bool = True) -> None:
        """
        Fill text into an input element.

        Args:
            locator: Element selector/locator
            text: Text to input
            clear_first: Whether to clear existing text before filling

        Raises:
            TimeoutError: If element is not found or not editable
        """
        self.logger.debug(f"Filling text '{text}' into element: {locator}")

        try:
            self.wait_for_element(locator, state="visible")
            element = self.page.locator(locator)

            if clear_first:
                element.clear()

            element.fill(text)
            self.logger.debug(f"Successfully filled text into element: {locator}")

        except Exception as e:
            self.logger.error(f"Failed to fill text into element '{locator}': {str(e)}")
            self._take_screenshot("fill_text_failed")
            raise

    def get_text(self, locator: Locator, wait_for_element: bool = True) -> str:
        """
        Get text content from an element.

        Args:
            locator: Element selector/locator
            wait_for_element: Whether to wait for element before getting text

        Returns:
            str: Text content of the element

        Raises:
            TimeoutError: If element is not found
        """
        self.logger.debug(f"Getting text from element: {locator}")

        try:
            if wait_for_element:
                self.wait_for_element(locator, state="visible")

            element = self.page.locator(locator)
            text = element.text_content() or ""

            self.logger.debug(f"Retrieved text '{text}' from element: {locator}")
            return text

        except Exception as e:
            self.logger.error(f"Failed to get text from element '{locator}': {str(e)}")
            self._take_screenshot("get_text_failed")
            raise

    def get_elements_count(self, locator: Locator) -> int:
        """
        Get the count of elements matching the locator.

        Args:
            locator: Element selector/locator

        Returns:
            int: Number of matching elements
        """
        self.logger.debug(f"Counting elements matching: {locator}")

        try:
            elements = self.page.locator(locator)
            count = elements.count()

            self.logger.debug(f"Found {count} elements matching: {locator}")
            return count

        except Exception as e:
            self.logger.error(f"Failed to count elements '{locator}': {str(e)}")
            return 0

    def is_element_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        """
        Check if an element is visible on the page.

        Args:
            locator: Element selector/locator
            timeout: Time to wait for element in milliseconds

        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            self.page.wait_for_selector(locator, timeout=timeout, state="visible")
            return True
        except Exception:
            return False

    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for the page to fully load.

        Args:
            timeout: Custom timeout in milliseconds
        """
        timeout_ms = timeout or self.settings.saucedemo.page_timeout

        self.logger.debug("Waiting for page to load completely")

        try:
            # Wait for DOM content to be loaded
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            # Wait for all network requests to finish
            self.page.wait_for_load_state("networkidle", timeout=timeout_ms)

            self.logger.debug("Page loaded successfully")

        except Exception as e:
            self.logger.error(f"Page load timeout: {str(e)}")
            self._take_screenshot("page_load_timeout")
            raise

    def scroll_to_element(self, locator: Locator) -> None:
        """
        Scroll an element into view.

        Args:
            locator: Element selector/locator
        """
        self.logger.debug(f"Scrolling to element: {locator}")

        try:
            element = self.page.locator(locator)
            element.scroll_into_view_if_needed()

            self.logger.debug(f"Scrolled to element: {locator}")

        except Exception as e:
            self.logger.error(f"Failed to scroll to element '{locator}': {str(e)}")
            raise

    def verify_page_loaded(self) -> None:
        """
        Verify that the current page is loaded correctly.

        This method checks the URL pattern and page title to ensure
        the correct page is loaded.

        Raises:
            AssertionError: If page verification fails
        """
        self.logger.info(f"Verifying page is loaded: {self.__class__.__name__}")

        try:
            # Check URL pattern
            current_url = self.page.url
            if self.url_pattern not in current_url:
                raise AssertionError(
                    f"URL pattern '{self.url_pattern}' not found in current URL: {current_url}"
                )

            # Check page title if specified
            if self.page_title:
                expect(self.page).to_have_title(self.page_title)

            self.logger.info("Page verification successful")

        except Exception as e:
            self.logger.error(f"Page verification failed: {str(e)}")
            self._take_screenshot("page_verification_failed")
            raise

    def _take_screenshot(self, name_suffix: str) -> str:
        """
        Take a screenshot for debugging purposes.

        Args:
            name_suffix: Suffix to add to screenshot filename

        Returns:
            str: Path to the saved screenshot
        """
        timestamp = int(time.time())
        screenshot_name = f"{self.context.correlation_id}_{name_suffix}_{timestamp}.png"
        screenshot_path = f"screenshots/{screenshot_name}"

        try:
            # Ensure screenshots directory exists
            import os

            os.makedirs("screenshots", exist_ok=True)

            self.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.info(f"Screenshot saved: {screenshot_path}")

            # Update context with screenshot path
            self.context.screenshot_path = screenshot_path

            return screenshot_path

        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            return ""
