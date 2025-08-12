"""
Reusable assertion helpers for enhanced test validation.

This module provides enhanced assertion methods with rich error messages,
logging integration, and Allure reporting support for better test debugging
and failure analysis.
"""

import logging
from typing import Any, List, Optional, Union

import allure


class AssertionHelper:
    """
    Helper class for enhanced test assertions with logging and reporting.

    This class provides assertion methods that include detailed error messages,
    automatic logging, and Allure step integration for better test reporting.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the assertion helper.

        Args:
            logger: Optional logger instance for assertion logging
        """
        self.logger = logger or logging.getLogger(__name__)

    @allure.step("Assert equals: {expected}")
    def assert_equals(
        self, actual: Any, expected: Any, message: Optional[str] = None
    ) -> None:
        """
        Assert that two values are equal with enhanced error reporting.

        Args:
            actual: Actual value
            expected: Expected value
            message: Optional custom error message

        Raises:
            AssertionError: If values are not equal
        """
        if actual != expected:
            error_msg = message or (
                f"Values are not equal.\n"
                f"Expected: {expected} (type: {type(expected).__name__})\n"
                f"Actual: {actual} (type: {type(actual).__name__})"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            allure.attach(
                f"Expected: {expected}\nActual: {actual}",
                name="Assertion Failure Details",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: {actual} == {expected}")

    @allure.step("Assert not equals: {not_expected}")
    def assert_not_equals(
        self, actual: Any, not_expected: Any, message: Optional[str] = None
    ) -> None:
        """
        Assert that two values are not equal.

        Args:
            actual: Actual value
            not_expected: Value that should not match
            message: Optional custom error message

        Raises:
            AssertionError: If values are equal
        """
        if actual == not_expected:
            error_msg = message or (
                f"Values should not be equal.\n"
                f"Both values: {actual} (type: {type(actual).__name__})"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: {actual} != {not_expected}")

    @allure.step("Assert contains: '{substring}' in text")
    def assert_contains(
        self,
        text: str,
        substring: str,
        case_sensitive: bool = True,
        message: Optional[str] = None,
    ) -> None:
        """
        Assert that text contains a substring.

        Args:
            text: Text to search in
            substring: Substring to find
            case_sensitive: Whether search should be case sensitive
            message: Optional custom error message

        Raises:
            AssertionError: If substring is not found
        """
        search_text = text if case_sensitive else text.lower()
        search_substring = substring if case_sensitive else substring.lower()

        if search_substring not in search_text:
            error_msg = message or (
                f"Substring not found.\n"
                f"Searching for: '{substring}'\n"
                f"In text: '{text}'\n"
                f"Case sensitive: {case_sensitive}"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            allure.attach(
                f"Text: {text}\nSubstring: {substring}\nCase sensitive: {case_sensitive}",
                name="Contains Assertion Failure",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: '{substring}' found in text")

    @allure.step("Assert list contains: {item}")
    def assert_list_contains(
        self, items: List[Any], item: Any, message: Optional[str] = None
    ) -> None:
        """
        Assert that a list contains a specific item.

        Args:
            items: List to search in
            item: Item to find
            message: Optional custom error message

        Raises:
            AssertionError: If item is not in list
        """
        if item not in items:
            error_msg = message or (
                f"Item not found in list.\n"
                f"Looking for: {item}\n"
                f"In list: {items}"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            allure.attach(
                f"Item: {item}\nList: {items}",
                name="List Contains Assertion Failure",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: {item} found in list")

    @allure.step("Assert greater than: {threshold}")
    def assert_greater_than(
        self,
        actual: Union[int, float],
        threshold: Union[int, float],
        message: Optional[str] = None,
    ) -> None:
        """
        Assert that a value is greater than a threshold.

        Args:
            actual: Actual numeric value
            threshold: Minimum threshold
            message: Optional custom error message

        Raises:
            AssertionError: If value is not greater than threshold
        """
        if actual <= threshold:
            error_msg = message or (
                f"Value is not greater than threshold.\n"
                f"Actual: {actual}\n"
                f"Threshold: {threshold}\n"
                f"Difference: {actual - threshold}"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            allure.attach(
                f"Actual: {actual}\nThreshold: {threshold}\nDifference: {actual - threshold}",
                name="Greater Than Assertion Failure",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: {actual} > {threshold}")

    @allure.step("Assert less than: {threshold}")
    def assert_less_than(
        self,
        actual: Union[int, float],
        threshold: Union[int, float],
        message: Optional[str] = None,
    ) -> None:
        """
        Assert that a value is less than a threshold.

        Args:
            actual: Actual numeric value
            threshold: Maximum threshold
            message: Optional custom error message

        Raises:
            AssertionError: If value is not less than threshold
        """
        if actual >= threshold:
            error_msg = message or (
                f"Value is not less than threshold.\n"
                f"Actual: {actual}\n"
                f"Threshold: {threshold}\n"
                f"Difference: {actual - threshold}"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: {actual} < {threshold}")

    @allure.step("Assert status code: {expected_status}")
    def assert_status_code(
        self,
        actual_status: int,
        expected_status: int,
        response_body: Optional[str] = None,
    ) -> None:
        """
        Assert HTTP status code with response context.

        Args:
            actual_status: Actual HTTP status code
            expected_status: Expected HTTP status code
            response_body: Optional response body for context

        Raises:
            AssertionError: If status codes don't match
        """
        if actual_status != expected_status:
            error_msg = (
                f"HTTP status code mismatch.\n"
                f"Expected: {expected_status}\n"
                f"Actual: {actual_status}"
            )

            if response_body:
                error_msg += f"\nResponse body: {response_body}"

            self.logger.error(f"Assertion failed: {error_msg}")

            if response_body:
                allure.attach(
                    response_body,
                    name="Response Body",
                    attachment_type=allure.attachment_type.JSON,
                )

            raise AssertionError(error_msg)

        self.logger.debug(f"Assertion passed: status code {actual_status}")

    @allure.step("Assert response time within: {max_time_ms}ms")
    def assert_response_time(
        self, actual_time_ms: float, max_time_ms: float, message: Optional[str] = None
    ) -> None:
        """
        Assert that response time is within acceptable limits.

        Args:
            actual_time_ms: Actual response time in milliseconds
            max_time_ms: Maximum acceptable time in milliseconds
            message: Optional custom error message

        Raises:
            AssertionError: If response time exceeds limit
        """
        if actual_time_ms > max_time_ms:
            error_msg = message or (
                f"Response time exceeded limit.\n"
                f"Actual: {actual_time_ms:.2f}ms\n"
                f"Limit: {max_time_ms:.2f}ms\n"
                f"Exceeded by: {actual_time_ms - max_time_ms:.2f}ms"
            )

            self.logger.error(f"Assertion failed: {error_msg}")
            raise AssertionError(error_msg)

        self.logger.debug(
            f"Assertion passed: response time {actual_time_ms:.2f}ms within limit"
        )


# Global assertion helper instance
assertions = AssertionHelper()


def get_assertion_helper(logger: Optional[logging.Logger] = None) -> AssertionHelper:
    """
    Get an assertion helper instance with optional logger.

    Args:
        logger: Optional logger for assertion logging

    Returns:
        AssertionHelper: Configured assertion helper
    """
    return AssertionHelper(logger)
