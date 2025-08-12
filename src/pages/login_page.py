"""
Login page object for SauceDemo application.

This module implements the Page Object Model for the SauceDemo login page,
providing methods for user authentication and login-related operations.
"""

import allure
from playwright.sync_api import Page, expect

from src.core.base_page import BasePage
from src.core.reporting import AllureSteps
from src.core.types import TestContext


class LoginPage(BasePage):
    """
    Page object for SauceDemo login functionality.

    This page handles user authentication including login form interactions,
    error handling, and navigation to the inventory page after successful login.
    """

    # Locators for login form elements
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"

    # Error and status elements
    ERROR_MESSAGE = "[data-test='error']"
    ERROR_BUTTON = ".error-button"
    ERROR_CONTAINER = ".error-message-container"

    # Page elements
    LOGIN_LOGO = ".login_logo"
    LOGIN_WRAPPER = ".login_wrapper"

    def __init__(self, page: Page, context: TestContext) -> None:
        """
        Initialize the login page.

        Args:
            page: Playwright page instance
            context: Test execution context
        """
        super().__init__(page, context)

    @property
    def url_pattern(self) -> str:
        """URL pattern that identifies this page."""
        return "/"

    @property
    def page_title(self) -> str:
        """Expected page title for this page."""
        return "Swag Labs"

    @allure.step("Navigate to login page")
    def navigate_to_login(self) -> None:
        """
        Navigate to the SauceDemo login page.

        This method navigates to the base URL and waits for the login form
        to be visible and ready for interaction.
        """
        with AllureSteps("Navigate to SauceDemo login page", self.logger):
            login_url = self.settings.saucedemo.base_url
            self.navigate_to(login_url)

            # Wait for login form to be visible
            self.wait_for_element(self.LOGIN_LOGO, state="visible")
            self.wait_for_element(self.USERNAME_INPUT, state="visible")
            self.wait_for_element(self.PASSWORD_INPUT, state="visible")
            self.wait_for_element(self.LOGIN_BUTTON, state="visible")

            self.logger.info("Login page loaded successfully")

    @allure.step("Enter username: {username}")
    def enter_username(self, username: str) -> None:
        """
        Enter username into the username field.

        Args:
            username: Username to enter
        """
        self.logger.debug(f"Entering username: {username}")
        self.fill_text(self.USERNAME_INPUT, username, clear_first=True)

    @allure.step("Enter password")
    def enter_password(self, password: str) -> None:
        """
        Enter password into the password field.

        Args:
            password: Password to enter (will be masked in logs)
        """
        self.logger.debug("Entering password (masked)")
        self.fill_text(self.PASSWORD_INPUT, password, clear_first=True)

    @allure.step("Click login button")
    def click_login_button(self) -> None:
        """
        Click the login button to submit the login form.

        This method clicks the login button and waits briefly for the
        submission to be processed.
        """
        self.logger.debug("Clicking login button")
        self.click_element(self.LOGIN_BUTTON)

        # Brief wait for form submission
        self.page.wait_for_timeout(1000)

    @allure.step("Login with credentials")
    def login(self, username: str, password: str) -> None:
        """
        Perform complete login process with username and password.

        This method performs the full login sequence: navigate to login page,
        enter credentials, and submit the form. It includes comprehensive
        logging and error handling.

        Args:
            username: Username for login
            password: Password for login

        Raises:
            TimeoutError: If login form elements are not found
            AssertionError: If login fails
        """
        self.logger.info(f"Starting login process for user: {username}")

        try:
            # Navigate to login page if not already there
            if not self.is_element_visible(self.USERNAME_INPUT, timeout=2000):
                self.navigate_to_login()

            # Enter credentials
            self.enter_username(username)
            self.enter_password(password)

            # Submit login form
            self.click_login_button()

            # Wait for either successful redirect or error message
            try:
                # Wait for URL change (successful login)
                self.page.wait_for_url("**/inventory.html", timeout=5000)
                self.logger.info(f"Login successful for user: {username}")

            except Exception:
                # Check for error message
                if self.is_element_visible(self.ERROR_MESSAGE, timeout=2000):
                    error_text = self.get_text(self.ERROR_MESSAGE)
                    self.logger.error(f"Login failed with error: {error_text}")
                    raise AssertionError(f"Login failed: {error_text}")
                else:
                    self.logger.error("Login failed - unknown error")
                    raise AssertionError("Login failed - no error message displayed")

        except Exception as e:
            self.logger.error(f"Login process failed for user {username}: {str(e)}")
            self._take_screenshot("login_failed")
            raise

    @allure.step("Verify login page loaded")
    def verify_login_page_loaded(self) -> None:
        """
        Verify that the login page is properly loaded.

        This method checks that all essential login page elements are visible
        and the page is ready for user interaction.

        Raises:
            AssertionError: If required elements are not found
        """
        self.logger.info("Verifying login page is loaded")

        try:
            # Verify essential elements are visible
            expect(self.page.locator(self.LOGIN_LOGO)).to_be_visible()
            expect(self.page.locator(self.USERNAME_INPUT)).to_be_visible()
            expect(self.page.locator(self.PASSWORD_INPUT)).to_be_visible()
            expect(self.page.locator(self.LOGIN_BUTTON)).to_be_visible()

            # Verify input fields are enabled
            expect(self.page.locator(self.USERNAME_INPUT)).to_be_enabled()
            expect(self.page.locator(self.PASSWORD_INPUT)).to_be_enabled()
            expect(self.page.locator(self.LOGIN_BUTTON)).to_be_enabled()

            # Verify page title
            expect(self.page).to_have_title(self.page_title)

            self.logger.info("Login page verification successful")

        except Exception as e:
            self.logger.error(f"Login page verification failed: {str(e)}")
            self._take_screenshot("login_page_verification_failed")
            raise

    @allure.step("Get error message")
    def get_error_message(self) -> str:
        """
        Get the current error message displayed on the login page.

        Returns:
            str: Error message text, or empty string if no error
        """
        try:
            if self.is_element_visible(self.ERROR_MESSAGE, timeout=2000):
                error_text = self.get_text(self.ERROR_MESSAGE)
                self.logger.debug(f"Error message found: {error_text}")
                return error_text
            else:
                self.logger.debug("No error message visible")
                return ""

        except Exception as e:
            self.logger.warning(f"Failed to get error message: {str(e)}")
            return ""

    @allure.step("Verify error message: {expected_error}")
    def verify_error_message(self, expected_error: str) -> None:
        """
        Verify that a specific error message is displayed.

        Args:
            expected_error: Expected error message text

        Raises:
            AssertionError: If error message doesn't match expected
        """
        self.logger.info(f"Verifying error message: {expected_error}")

        try:
            # Wait for error message to appear
            self.wait_for_element(self.ERROR_MESSAGE, state="visible", timeout=5000)

            actual_error = self.get_text(self.ERROR_MESSAGE)

            if expected_error not in actual_error:
                error_msg = (
                    f"Error message mismatch.\n"
                    f"Expected: {expected_error}\n"
                    f"Actual: {actual_error}"
                )
                self.logger.error(error_msg)
                raise AssertionError(error_msg)

            self.logger.info("Error message verification successful")

        except Exception as e:
            self.logger.error(f"Error message verification failed: {str(e)}")
            self._take_screenshot("error_message_verification_failed")
            raise

    @allure.step("Clear error message")
    def clear_error_message(self) -> None:
        """
        Clear the error message by clicking the error button.

        This method clicks the X button on the error message to dismiss it.
        """
        try:
            if self.is_element_visible(self.ERROR_BUTTON, timeout=2000):
                self.click_element(self.ERROR_BUTTON)

                # Wait for error to disappear
                self.wait_for_element(
                    self.ERROR_CONTAINER, state="hidden", timeout=3000
                )

                self.logger.debug("Error message cleared successfully")
            else:
                self.logger.debug("No error message to clear")

        except Exception as e:
            self.logger.warning(f"Failed to clear error message: {str(e)}")

    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.

        Returns:
            bool: True if user is logged in, False otherwise
        """
        try:
            # Check if we're on the inventory page (successful login)
            current_url = self.page.url
            is_on_inventory = "/inventory.html" in current_url

            self.logger.debug(
                f"Login status check - URL: {current_url}, Logged in: {is_on_inventory}"
            )
            return is_on_inventory

        except Exception as e:
            self.logger.warning(f"Failed to check login status: {str(e)}")
            return False
