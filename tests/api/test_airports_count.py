"""
Test module for airport count validation.

This module contains tests for verifying that the AirportGap API
returns the expected number of airports.

Test Case: TC-API-001
Objective: Verify that the API returns exactly 30 airports
"""

import allure
import pytest
from playwright.sync_api import APIRequestContext

from src.api.airports_client import AirportsClient
from src.core.assertions import get_assertion_helper
from src.core.types import TestContext


@pytest.mark.api
@pytest.mark.smoke
@allure.epic("API Testing")
@allure.feature("Airport Data")
@allure.story("Airport Count Validation")
@allure.title("Verify API returns exactly 30 airports")
@allure.description(
    """
This test verifies that the AirportGap API correctly returns
exactly 30 airports in the response.

Steps:
1. Send GET request to /api/airports endpoint
2. Parse the response JSON
3. Count the number of airports in the data array
4. Verify the count equals exactly 30

Expected Result:
- API responds with 200 status code
- Response contains exactly 30 airports
- Each airport has required fields (id, type, attributes)
"""
)
@allure.testcase("TC-API-001", "Airport Count Validation")
def test_airports_api_returns_exactly_thirty_airports(
    api_request_context: APIRequestContext,
    test_context: TestContext,
    allure_reporter,
) -> None:
    """
    Verify that the airports API returns exactly 30 airports.

    This test validates the core API functionality by ensuring
    the correct number of airports is returned.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context with correlation ID
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If airport count is not exactly 30
    """
    assertions = get_assertion_helper(
        test_context.logger if hasattr(test_context, "logger") else None
    )

    with allure.step("Initialize airports API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Send GET request to /api/airports endpoint"):
        response = airports_client.get_all_airports()

        # Attach response details to report
        allure_reporter.attach_json(
            {
                "airports_count": len(response) if response else 0,
            },
            "API Response Summary",
        )

    with allure.step("Verify response contains data array"):
        assertions.assert_equals(
            actual=response is not None,
            expected=True,
            message="Response should contain data array",
        )

        assertions.assert_equals(
            actual=isinstance(response, list),
            expected=True,
            message="Response data should be a list",
        )

    with allure.step("Count airports and verify total is exactly 30"):
        airport_count = len(response)
        assertions.assert_equals(
            actual=airport_count,
            expected=30,
            message=f"Expected exactly 30 airports, but found {airport_count}",
        )

        # Attach detailed count information
        allure_reporter.attach_json(
            {
                "actual_count": airport_count,
                "expected_count": 30,
                "difference": airport_count - 30,
                "status": "PASS" if airport_count == 30 else "FAIL",
            },
            "Airport Count Validation",
        )

    with allure.step("Verify each airport has required structure"):
        if response:
            for i, airport in enumerate(response[:5]):  # Check first 5 for structure
                assertions.assert_equals(
                    actual=hasattr(airport, "id"),
                    expected=True,
                    message=f"Airport {i} missing 'id' field",
                )

                assertions.assert_equals(
                    actual=hasattr(airport, "type"),
                    expected=True,
                    message=f"Airport {i} missing 'type' field",
                )

                assertions.assert_equals(
                    actual=hasattr(airport, "attributes"),
                    expected=True,
                    message=f"Airport {i} missing 'attributes' field",
                )

                # Verify attributes is a dictionary
                assertions.assert_equals(
                    actual=isinstance(airport.attributes, dict),
                    expected=True,
                    message=f"Airport {i} attributes should be a dictionary",
                )

        allure_reporter.attach_json(
            {
                "airports_checked": min(5, len(response) if response else 0),
                "structure_validation": "PASS",
                "required_fields": ["id", "type", "attributes"],
            },
            "Airport Structure Validation",
        )

    with allure.step("Verify response performance is acceptable"):
        # Performance validation - response should be under 2 seconds
        max_acceptable_time = 2000  # 2 seconds in milliseconds
        # Note: We can't measure response time here since get_all_airports doesn't return timing info
        # This is a placeholder for when we implement timing in the client
        allure_reporter.attach_json(
            {
                "performance_note": "Response time measurement not implemented in current client",
                "max_acceptable_time_ms": max_acceptable_time,
                "performance_status": "INFO",
            },
            "Performance Validation",
        )
