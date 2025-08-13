"""
Allure reporting utilities and helpers.

This module provides utilities for enhanced Allure reporting including
screenshot attachment, JSON data attachment, step annotations, and
test metadata management.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

import allure
from playwright.sync_api import Page

from src.core.types import TestContext


class AllureReporter:
    """
    Helper class for Allure test reporting functionality.

    This class provides methods for attaching screenshots, logs, JSON data,
    and other artifacts to Allure reports for enhanced test debugging and
    analysis capabilities.
    """

    def __init__(self, context: Optional[TestContext] = None) -> None:
        """
        Initialize the Allure reporter.

        Args:
            context: Optional test execution context
        """
        self.context = context
        self.logger = logging.getLogger(__name__)

    @allure.step("Attach screenshot: {name}")
    def attach_screenshot(
        self, page: Page, name: str = "Screenshot", full_page: bool = True
    ) -> str:
        """
        Take and attach a screenshot to the Allure report.

        Args:
            page: Playwright page instance
            name: Name for the screenshot attachment
            full_page: Whether to capture the full page

        Returns:
            str: Path to the saved screenshot
        """
        try:
            # Generate screenshot filename with correlation ID if available
            correlation_id = self.context.correlation_id if self.context else "unknown"
            timestamp = str(int(__import__("time").time()))
            filename = f"{correlation_id}_{name}_{timestamp}.png"

            # Take screenshot
            screenshot_bytes = page.screenshot(full_page=full_page)

            # Attach to Allure report
            allure.attach(
                screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG
            )

            self.logger.debug(f"Screenshot attached to Allure report: {name}")
            return filename

        except Exception as e:
            self.logger.error(f"Failed to attach screenshot: {str(e)}")
            return ""

    @allure.step("Attach JSON data: {name}")
    def attach_json(
        self, data: Union[Dict[str, Any], str], name: str = "JSON Data"
    ) -> None:
        """
        Attach JSON data to the Allure report.

        Args:
            data: JSON data (dict or string)
            name: Name for the attachment
        """
        try:
            if isinstance(data, dict):
                json_str = json.dumps(data, indent=2)
            else:
                json_str = str(data)

            allure.attach(
                json_str, name=name, attachment_type=allure.attachment_type.JSON
            )

            self.logger.debug(f"JSON data attached to Allure report: {name}")

        except Exception as e:
            self.logger.error(f"Failed to attach JSON data: {str(e)}")

    @allure.step("Attach text: {name}")
    def attach_text(self, text: str, name: str = "Text Data") -> None:
        """
        Attach text content to the Allure report.

        Args:
            text: Text content to attach
            name: Name for the attachment
        """
        try:
            allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)

            self.logger.debug(f"Text attached to Allure report: {name}")

        except Exception as e:
            self.logger.error(f"Failed to attach text: {str(e)}")

    @allure.step("Attach log file: {name}")
    def attach_log_file(
        self, log_file_path: Union[str, Path], name: str = "Log File"
    ) -> None:
        """
        Attach a log file to the Allure report.

        Args:
            log_file_path: Path to the log file
            name: Name for the attachment
        """
        try:
            log_path = Path(log_file_path)

            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()

                allure.attach(
                    log_content, name=name, attachment_type=allure.attachment_type.TEXT
                )

                self.logger.debug(f"Log file attached to Allure report: {name}")
            else:
                self.logger.warning(f"Log file not found: {log_file_path}")

        except Exception as e:
            self.logger.error(f"Failed to attach log file: {str(e)}")

    def attach_browser_console_logs(
        self, page: Page, name: str = "Browser Console Logs"
    ) -> None:
        """
        Attach browser console logs to the Allure report.

        Args:
            page: Playwright page instance
            name: Name for the attachment
        """
        try:
            # This would require setting up console log capture
            # For now, we'll attach a placeholder
            console_logs = "Console log capture not yet implemented"

            self.attach_text(console_logs, name)

        except Exception as e:
            self.logger.error(f"Failed to attach console logs: {str(e)}")

    def set_test_description(self, description: str) -> None:
        """
        Set the test description in Allure.

        Args:
            description: Test description
        """
        try:
            allure.dynamic.description(description)
            self.logger.debug(f"Test description set: {description}")

        except Exception as e:
            self.logger.error(f"Failed to set test description: {str(e)}")

    def add_test_link(self, name: str, url: str, link_type: str = "link") -> None:
        """
        Add a link to the test in Allure.

        Args:
            name: Link name
            url: Link URL
            link_type: Type of link (link, issue, test_case)
        """
        try:
            if link_type == "issue":
                allure.dynamic.issue(name, url)
            elif link_type == "test_case":
                allure.dynamic.testcase(name, url)
            else:
                allure.dynamic.link(url, name=name)

            self.logger.debug(f"Test link added: {name} -> {url}")

        except Exception as e:
            self.logger.error(f"Failed to add test link: {str(e)}")

    def add_test_labels(self, **labels: str) -> None:
        """
        Add custom labels to the test in Allure.

        Args:
            **labels: Key-value pairs for labels
        """
        try:
            for key, value in labels.items():
                allure.dynamic.label(key, value)

            self.logger.debug(f"Test labels added: {labels}")

        except Exception as e:
            self.logger.error(f"Failed to add test labels: {str(e)}")


class AllureSteps:
    """
    Context manager for Allure test steps with enhanced logging.

    This class provides a convenient way to create Allure test steps
    with automatic logging and error handling.
    """

    def __init__(
        self,
        step_name: str,
        logger: Optional[
            Union[logging.Logger, logging.LoggerAdapter[logging.Logger]]
        ] = None,
    ) -> None:
        """
        Initialize the Allure step context manager.

        Args:
            step_name: Name of the test step
            logger: Optional logger instance
        """
        self.step_name = step_name
        self.logger = logger or logging.getLogger(__name__)
        self.step_context = None

    def __enter__(self):
        """Enter the step context."""
        self.step_context = allure.step(self.step_name)
        self.step_context.__enter__()
        self.logger.info(f"Starting step: {self.step_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the step context."""
        if exc_type:
            self.logger.error(f"Step failed: {self.step_name} - {str(exc_val)}")
        else:
            self.logger.info(f"Step completed: {self.step_name}")

        self.step_context.__exit__(exc_type, exc_val, exc_tb)


# Global reporter instance
reporter = AllureReporter()


def get_allure_reporter(context: Optional[TestContext] = None) -> AllureReporter:
    """
    Get an Allure reporter instance with optional context.

    Args:
        context: Optional test execution context

    Returns:
        AllureReporter: Configured Allure reporter
    """
    return AllureReporter(context)


def allure_step(
    step_name: str,
    logger: Optional[
        Union[logging.Logger, logging.LoggerAdapter[logging.Logger]]
    ] = None,
):
    """
    Decorator for creating Allure steps with logging.

    Args:
        step_name: Name of the test step
        logger: Optional logger instance

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with AllureSteps(step_name, logger):
                return func(*args, **kwargs)

        return wrapper

    return decorator
