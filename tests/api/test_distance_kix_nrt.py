"""
Test module for verifying distance calculations between airports.

This module contains tests for verifying distance calculations between
specific airports using the AirportGap API.

Test Case: TC-API-003
Objective: Verify that the distance between KIX and NRT airports is greater than 400 km
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
@allure.feature("Distance Calculation")
@allure.story("KIX to NRT Distance")
@allure.title("Verify distance between KIX and NRT exceeds 400 km")
@allure.description(
    """
This test verifies that the distance between KIX (Kansai International Airport)
and NRT (Narita International Airport) is greater than 400 kilometers.

Steps:
1. Send POST request to /api/airports/distance
2. Include request body with KIX and NRT airport codes
3. Verify HTTP response status is 200
4. Parse the JSON response
5. Extract the distance value in kilometers
6. Verify distance is greater than 400 km
7. Validate distance is reasonable (< 2000 km for Japan domestic)

Expected Result:
- HTTP status code is 200 (OK)
- Response contains distance calculation data
- Distance between KIX and NRT is > 400 kilometers
- Response includes distance in multiple units (km, miles, nautical miles)
"""
)
@allure.testcase("TC-API-003", "KIX-NRT Distance Calculation")
def test_distance_between_kix_and_nrt_exceeds_400km(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that the distance between KIX and NRT airports exceeds 400 km.

    This test validates the distance calculation API by checking the distance
    between two major Japanese airports and ensuring it meets expected thresholds.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context with correlation ID
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If distance is not greater than 400 km
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get distance calculation expectations"):
        api_expectations = get_api_expectations("airportgap_api")
        distance_expectations = api_expectations["distance_calculations"]["kix_to_nrt"]

        from_airport = distance_expectations["from_code"]
        to_airport = distance_expectations["to_code"]
        min_distance = distance_expectations["min_distance_km"]
        max_distance = distance_expectations["max_distance_km"]

        allure_reporter.attach_json(
            {
                "from_airport": from_airport,
                "to_airport": to_airport,
                "min_expected_distance_km": min_distance,
                "max_expected_distance_km": max_distance,
                "test_description": distance_expectations["description"],
            },
            "Distance Test Parameters",
        )

    with allure.step(f"Calculate distance between {from_airport} and {to_airport}"):
        distance_calculation = airports_client.calculate_distance(
            from_airport, to_airport
        )

        allure_reporter.attach_json(
            {
                "from_airport": from_airport,
                "to_airport": to_airport,
                "distance_km": distance_calculation.kilometers,
                "distance_miles": distance_calculation.miles,
                "distance_nautical_miles": distance_calculation.nautical_miles,
                "calculation_valid": distance_calculation.is_valid_distance,
            },
            "Distance Calculation Results",
        )

    with allure.step("Verify distance is greater than minimum threshold"):
        actual_distance = distance_calculation.kilometers

        assertions.assert_greater_than(
            actual=actual_distance,
            threshold=min_distance,
            message=(
                f"Distance between {from_airport} and {to_airport} "
                f"({actual_distance:.2f} km) should be greater than {min_distance} km"
            ),
        )

    with allure.step("Verify distance is reasonable (less than maximum threshold)"):
        assertions.assert_less_than(
            actual=actual_distance,
            threshold=max_distance,
            message=(
                f"Distance between {from_airport} and {to_airport} "
                f"({actual_distance:.2f} km) should be less than {max_distance} km "
                f"(sanity check for domestic Japan distance)"
            ),
        )

    with allure.step("Verify distance calculation has valid data"):
        assertions.assert_equals(
            actual=distance_calculation.is_valid_distance,
            expected=True,
            message="Distance calculation should have valid positive values for all units",
        )

        # Verify all distance units are positive
        if distance_calculation.kilometers <= 0:
            raise AssertionError(
                f"Invalid kilometers value: {distance_calculation.kilometers}"
            )

        if distance_calculation.miles <= 0:
            raise AssertionError(f"Invalid miles value: {distance_calculation.miles}")

        if distance_calculation.nautical_miles <= 0:
            raise AssertionError(
                f"Invalid nautical miles value: {distance_calculation.nautical_miles}"
            )

    with allure.step("Verify distance unit conversions are reasonable"):
        # Basic sanity checks for unit conversions
        km_to_miles_ratio = distance_calculation.miles / distance_calculation.kilometers
        km_to_nm_ratio = (
            distance_calculation.nautical_miles / distance_calculation.kilometers
        )

        # 1 km ≈ 0.621 miles, 1 km ≈ 0.540 nautical miles
        expected_km_to_miles = 0.621371
        expected_km_to_nm = 0.539957

        # Allow 5% tolerance for conversion ratios
        tolerance = 0.05

        if (
            abs(km_to_miles_ratio - expected_km_to_miles)
            > expected_km_to_miles * tolerance
        ):
            raise AssertionError(
                f"Kilometers to miles conversion seems incorrect. "
                f"Expected ratio ≈ {expected_km_to_miles:.3f}, got {km_to_miles_ratio:.3f}"
            )

        if abs(km_to_nm_ratio - expected_km_to_nm) > expected_km_to_nm * tolerance:
            raise AssertionError(
                f"Kilometers to nautical miles conversion seems incorrect. "
                f"Expected ratio ≈ {expected_km_to_nm:.3f}, got {km_to_nm_ratio:.3f}"
            )


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Distance Calculation")
@allure.story("Distance API Performance")
@allure.title("Verify distance calculation API performance")
@allure.description(
    """
This test verifies that the distance calculation API responds within
acceptable time limits for good user experience.
"""
)
def test_distance_calculation_api_performance(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that distance calculation API responds within acceptable time limits.

    This test validates the API's performance for distance calculations
    to ensure good user experience.

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
            "max_distance_calc_time_ms"
        ]
        distance_expectations = api_expectations["distance_calculations"]["kix_to_nrt"]

    with allure.step("Measure distance calculation response time"):
        import time

        start_time = time.time()
        distance_calculation = airports_client.calculate_distance(
            distance_expectations["from_code"], distance_expectations["to_code"]
        )
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        allure_reporter.attach_json(
            {
                "response_time_ms": response_time_ms,
                "max_allowed_ms": max_response_time,
                "distance_calculated_km": distance_calculation.kilometers,
                "performance_acceptable": response_time_ms <= max_response_time,
            },
            "Distance Calculation Performance",
        )

    with allure.step("Verify response time is within acceptable limits"):
        assertions.assert_less_than(
            actual=response_time_ms,
            threshold=max_response_time,
            message=(
                f"Distance calculation response time {response_time_ms:.2f}ms "
                f"exceeds maximum allowed time {max_response_time}ms"
            ),
        )


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Distance Calculation")
@allure.story("Bidirectional Distance")
@allure.title("Verify distance is same in both directions")
@allure.description(
    """
This test verifies that the distance calculation returns the same result
regardless of the direction (KIX to NRT vs NRT to KIX).
"""
)
def test_distance_calculation_is_bidirectional(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that distance calculation returns same result in both directions.

    This test validates that the distance between two airports is the same
    regardless of which airport is specified as origin or destination.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get test airport codes"):
        distance_expectations = get_api_expectations("airportgap_api")[
            "distance_calculations"
        ]["kix_to_nrt"]
        airport_a = distance_expectations["from_code"]
        airport_b = distance_expectations["to_code"]

    with allure.step(f"Calculate distance from {airport_a} to {airport_b}"):
        distance_a_to_b = airports_client.calculate_distance(airport_a, airport_b)

    with allure.step(f"Calculate distance from {airport_b} to {airport_a}"):
        distance_b_to_a = airports_client.calculate_distance(airport_b, airport_a)

    with allure.step("Compare distances in both directions"):
        allure_reporter.attach_json(
            {
                "direction_1": f"{airport_a} to {airport_b}",
                "distance_1_km": distance_a_to_b.kilometers,
                "direction_2": f"{airport_b} to {airport_a}",
                "distance_2_km": distance_b_to_a.kilometers,
                "difference_km": abs(
                    distance_a_to_b.kilometers - distance_b_to_a.kilometers
                ),
                "distances_equal": distance_a_to_b.kilometers
                == distance_b_to_a.kilometers,
            },
            "Bidirectional Distance Comparison",
        )

    with allure.step("Verify distances are equal in both directions"):
        # Allow very small tolerance for floating point precision
        tolerance_km = 0.001  # 1 meter tolerance

        distance_difference = abs(
            distance_a_to_b.kilometers - distance_b_to_a.kilometers
        )

        assertions.assert_less_than(
            actual=distance_difference,
            threshold=tolerance_km,
            message=(
                f"Distance should be the same in both directions. "
                f"{airport_a} to {airport_b}: {distance_a_to_b.kilometers:.3f} km, "
                f"{airport_b} to {airport_a}: {distance_b_to_a.kilometers:.3f} km, "
                f"Difference: {distance_difference:.6f} km"
            ),
        )


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Distance Calculation")
@allure.story("Error Handling")
@allure.title("Verify distance API handles invalid airport codes gracefully")
@allure.description(
    """
This test verifies that the distance calculation API properly handles
invalid airport codes and returns appropriate error responses.
"""
)
def test_distance_api_handles_invalid_airport_codes(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that distance API handles invalid airport codes gracefully.

    This test validates that the API properly handles error scenarios
    when invalid airport codes are provided.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context
        allure_reporter: Allure reporter for enhanced reporting
    """
    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get error scenario expectations"):
        api_expectations = get_api_expectations("airportgap_api")
        error_scenario = api_expectations["error_scenarios"]["invalid_airport_code"]
        invalid_code = error_scenario["code"]
        valid_code = "KIX"  # Known valid airport code

    with allure.step("Test invalid 'from' airport code"):
        try:
            distance_calc = airports_client.calculate_distance(invalid_code, valid_code)
            # If no exception is raised, the API might be too permissive
            allure_reporter.attach_json(
                {
                    "scenario": "invalid_from_airport",
                    "from_code": invalid_code,
                    "to_code": valid_code,
                    "unexpected_success": True,
                    "distance_km": distance_calc.kilometers,
                },
                "Unexpected Success with Invalid Code",
            )
            pytest.fail(
                f"Expected error for invalid airport code '{invalid_code}', "
                f"but got successful response with distance: {distance_calc.kilometers} km"
            )
        except Exception as e:
            allure_reporter.attach_json(
                {
                    "scenario": "invalid_from_airport",
                    "from_code": invalid_code,
                    "to_code": valid_code,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "handled_correctly": True,
                },
                "Invalid Airport Code Error Handling",
            )
