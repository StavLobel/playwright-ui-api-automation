"""
Test module for AirportGap API airport count verification.

This module contains tests for verifying that the AirportGap API returns
the expected number of airports in the response.

Test Case: TC-API-001
Objective: Verify that the AirportGap API returns exactly 30 airports
"""

import allure
import pytest
from playwright.sync_api import APIRequestContext

from src.api.airports_client import AirportsClient
from src.core.assertions import get_assertion_helper
from src.core.types import TestContext
from src.utils.data_loader import get_api_expectations


@pytest.mark.api
@pytest.mark.smoke
@allure.epic("API Testing")
@allure.feature("Airport Data Retrieval")
@allure.story("Airport Count Validation")
@allure.title("Verify AirportGap API returns exactly 30 airports")
@allure.description(
    """
This test verifies that the AirportGap API returns exactly 30 airports
in the response when querying the /api/airports endpoint.

Steps:
1. Send GET request to /api/airports
2. Verify HTTP response status is 200
3. Parse the JSON response body
4. Extract the airports data array
5. Count the number of airport objects
6. Verify exactly 30 airports are returned

Expected Result:
- HTTP status code is 200 (OK)
- Response contains valid JSON structure
- "data" array contains exactly 30 airport objects
- Each airport object has required fields (id, type, attributes)
"""
)
@allure.testcase("TC-API-001", "Airport Count Verification")
def test_airports_api_returns_exactly_thirty_airports(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that the AirportGap API returns exactly 30 airports.

    This test validates the API's data consistency by ensuring the airport
    count matches the expected value, which is critical for data integrity.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context with correlation ID
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If airport count is not exactly 30
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get expected airport count from test data"):
        api_expectations = get_api_expectations("airportgap_api")
        expected_count = api_expectations["airports"]["total_count"]

        allure_reporter.attach_json(
            {"expected_airport_count": expected_count}, "Test Expectations"
        )

    with allure.step("Fetch all airports from API"):
        airports = airports_client.get_all_airports()
        actual_count = len(airports)

        allure_reporter.attach_json(
            {
                "actual_count": actual_count,
                "expected_count": expected_count,
                "airports_sample": [
                    {
                        "id": airport.id,
                        "name": airport.name,
                        "city": airport.city,
                        "country": airport.country,
                        "iata_code": airport.iata_code,
                    }
                    for airport in airports[:5]  # First 5 airports as sample
                ],
            },
            "Airports API Response Summary",
        )

    with allure.step("Verify exactly 30 airports are returned"):
        assertions.assert_equals(
            actual=actual_count,
            expected=expected_count,
            message=(
                f"Expected exactly {expected_count} airports from API, "
                f"but received {actual_count} airports"
            ),
        )

    with allure.step("Validate airport data structure"):
        # Verify that airports have required attributes
        airports_with_missing_data = []

        for i, airport in enumerate(airports):
            missing_fields = []

            if not airport.id:
                missing_fields.append("id")
            if not airport.type:
                missing_fields.append("type")
            if not airport.name:
                missing_fields.append("name")
            if not airport.attributes:
                missing_fields.append("attributes")

            if missing_fields:
                airports_with_missing_data.append(
                    {
                        "index": i,
                        "airport_id": airport.id,
                        "missing_fields": missing_fields,
                    }
                )

        # Attach validation results
        allure_reporter.attach_json(
            {
                "total_airports_validated": len(airports),
                "airports_with_missing_data": len(airports_with_missing_data),
                "missing_data_details": airports_with_missing_data[
                    :10
                ],  # First 10 for brevity
            },
            "Airport Data Validation Results",
        )

        # Assert that all airports have complete data
        if airports_with_missing_data:
            error_msg = (
                f"Found {len(airports_with_missing_data)} airports with missing required data. "
                f"First few examples: {airports_with_missing_data[:5]}"
            )
            raise AssertionError(error_msg)


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Airport Data Retrieval")
@allure.story("Data Consistency")
@allure.title("Verify airport count consistency across multiple requests")
@allure.description(
    """
This test verifies that the airport count remains consistent across
multiple API requests, ensuring data stability and reliability.
"""
)
def test_airport_count_consistency_across_requests(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that airport count is consistent across multiple API requests.

    This test validates the API's data consistency by making multiple
    requests and ensuring the airport count remains stable.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Make multiple API requests to verify consistency"):
        request_results = []
        num_requests = 3

        for i in range(num_requests):
            with allure.step(f"Request {i + 1} of {num_requests}"):
                count = airports_client.get_airports_count()
                request_results.append(
                    {"request_number": i + 1, "airport_count": count}
                )

        allure_reporter.attach_json(
            {"number_of_requests": num_requests, "request_results": request_results},
            "Multiple Request Results",
        )

    with allure.step("Verify count consistency across all requests"):
        counts = [result["airport_count"] for result in request_results]
        unique_counts = set(counts)

        if len(unique_counts) > 1:
            error_msg = (
                f"Airport count is inconsistent across requests. "
                f"Got different counts: {sorted(unique_counts)}. "
                f"Request details: {request_results}"
            )
            raise AssertionError(error_msg)

        # Verify the consistent count matches expected value
        consistent_count = counts[0]
        expected_count = get_api_expectations("airportgap_api")["airports"][
            "total_count"
        ]

        assertions.assert_equals(
            actual=consistent_count,
            expected=expected_count,
            message=(
                f"Consistent count {consistent_count} does not match "
                f"expected count {expected_count}"
            ),
        )


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Airport Data Retrieval")
@allure.story("Performance Validation")
@allure.title("Verify airport API response time performance")
@allure.description(
    """
This test verifies that the airport API responds within acceptable
time limits to ensure good user experience.
"""
)
def test_airports_api_response_time_performance(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that the airports API responds within acceptable time limits.

    This test validates the API's performance by measuring response times
    and ensuring they meet performance expectations.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get performance expectations"):
        api_expectations = get_api_expectations("airportgap_api")
        max_response_time = api_expectations["performance_expectations"][
            "max_list_response_time_ms"
        ]

    with allure.step("Make API request and measure response time"):
        import time

        start_time = time.time()

        airports = airports_client.get_all_airports()

        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000

        allure_reporter.attach_json(
            {
                "response_time_ms": response_time_ms,
                "max_allowed_ms": max_response_time,
                "airports_count": len(airports),
                "performance_acceptable": response_time_ms <= max_response_time,
            },
            "Performance Test Results",
        )

    with allure.step("Verify response time is within acceptable limits"):
        assertions.assert_less_than(
            actual=response_time_ms,
            threshold=max_response_time,
            message=(
                f"API response time {response_time_ms:.2f}ms exceeds "
                f"maximum allowed time {max_response_time}ms"
            ),
        )
