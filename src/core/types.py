"""
Type definitions and data classes for the automation framework.

This module provides typed aliases, enums, and dataclasses used throughout
the testing framework to ensure type safety and better code documentation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Type aliases for better readability
JSONData = Dict[str, Any]
TestData = Dict[str, Union[str, int, float, bool, List[Any], Dict[str, Any]]]
Locator = str
URL = str


class TestResult(Enum):
    """Enumeration for test execution results."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BROKEN = "broken"


class LogLevel(Enum):
    """Enumeration for logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BrowserType(Enum):
    """Enumeration for supported browser types."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


@dataclass
class TestContext:
    """
    Data class to hold test execution context information.

    This class encapsulates information about the current test execution
    including correlation ID, test name, browser info, and other metadata.
    """

    __test__ = False  # Tell pytest this is not a test class

    correlation_id: str
    test_name: str
    browser_name: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[TestResult] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Calculate test execution duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class APIResponse:
    """
    Data class for API response information.

    Encapsulates HTTP response data including status, headers, body,
    and timing information for better test assertions and reporting.
    """

    status_code: int
    headers: Dict[str, str]
    body: Union[str, Dict[str, Any]]
    url: str
    method: str
    duration_ms: Optional[float] = None

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status code)."""
        return 200 <= self.status_code < 300

    @property
    def json_body(self) -> Optional[Dict[str, Any]]:
        """Get response body as JSON if it's a dictionary."""
        if isinstance(self.body, dict):
            return self.body
        return None


@dataclass
class Airport:
    """
    Data class representing an airport from the AirportGap API.

    Used for type-safe handling of airport data in API tests.
    """

    id: str
    type: str
    attributes: Dict[str, Any]

    @property
    def name(self) -> str:
        """Get the airport name from attributes."""
        return self.attributes.get("name", "")

    @property
    def city(self) -> str:
        """Get the airport city from attributes."""
        return self.attributes.get("city", "")

    @property
    def country(self) -> str:
        """Get the airport country from attributes."""
        return self.attributes.get("country", "")

    @property
    def iata_code(self) -> str:
        """Get the airport IATA code from attributes."""
        return self.attributes.get("iata", "")


@dataclass
class DistanceCalculation:
    """
    Data class for distance calculation results between two airports.

    Used in AirportGap API distance calculation tests.
    """

    from_airport: Airport
    to_airport: Airport
    kilometers: float
    miles: float
    nautical_miles: float

    @property
    def is_valid_distance(self) -> bool:
        """Check if the calculated distance values are reasonable."""
        return self.kilometers > 0 and self.miles > 0 and self.nautical_miles > 0
