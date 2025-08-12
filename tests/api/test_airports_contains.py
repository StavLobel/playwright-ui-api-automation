"""
Test module for verifying specific airports in AirportGap API response.

This module contains tests for verifying that specific airports are present
in the AirportGap API response data.

Test Case: TC-API-002
Objective: Verify that specific airports (Akureyri, St. Anthony, CFB Bagotville) are present
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
@allure.story("Specific Airport Verification")
@allure.title("Verify specific airports are present in API response")
@allure.description(
    """
This test verifies that specific airports (Akureyri, St. Anthony, CFB Bagotville)
are present in the AirportGap API response.

Steps:
1. Send GET request to /api/airports
2. Verify HTTP response status is 200
3. Parse the JSON response and extract airport data
4. Create a list of all airport names from the response
5. Verify "Akureyri" airport is present in the list
6. Verify "St. Anthony" airport is present in the list
7. Verify "CFB Bagotville" airport is present in the list

Expected Result:
- All three specified airports are found in the response
- Airport names match exactly (case-sensitive)
- Each airport has complete attribute information
"""
)
@allure.testcase("TC-API-002", "Specific Airports Presence Verification")
def test_api_contains_required_airports(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that specific required airports are present in the API response.

    This test validates that the API contains specific airports that are
    required for the application's functionality.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context with correlation ID
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If any required airport is not found
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get required airports from test data"):
        api_expectations = get_api_expectations("airportgap_api")
        required_airports = api_expectations["airports"]["required_airports"]

        allure_reporter.attach_json(
            {"required_airports": required_airports}, "Required Airports List"
        )

    with allure.step("Fetch all airports from API"):
        airports = airports_client.get_all_airports()
        airport_names = [airport.name for airport in airports]

        allure_reporter.attach_json(
            {
                "total_airports": len(airports),
                "airport_names_sample": airport_names[:10],  # First 10 for brevity
                "total_names_retrieved": len(airport_names),
            },
            "API Response Summary",
        )

    with allure.step("Verify each required airport is present"):
        verification_results = {}
        missing_airports = []
        found_airports = []

        for required_airport in required_airports:
            with allure.step(f"Checking for airport: {required_airport}"):
                if required_airport in airport_names:
                    verification_results[required_airport] = True
                    found_airports.append(required_airport)
                    allure_reporter.attach_json(
                        {"airport_name": required_airport, "status": "found"},
                        f"Airport Found: {required_airport}",
                    )
                else:
                    verification_results[required_airport] = False
                    missing_airports.append(required_airport)
                    allure_reporter.attach_json(
                        {"airport_name": required_airport, "status": "missing"},
                        f"Airport Missing: {required_airport}",
                    )

        # Attach overall verification results
        allure_reporter.attach_json(
            {
                "verification_results": verification_results,
                "found_airports": found_airports,
                "missing_airports": missing_airports,
                "success_rate": f"{len(found_airports)}/{len(required_airports)}",
            },
            "Airport Verification Results",
        )

    with allure.step("Assert all required airports are found"):
        if missing_airports:
            # Create detailed error message with available airports for debugging
            available_similar = []
            for missing in missing_airports:
                # Find similar airport names for debugging
                similar = [
                    name for name in airport_names if missing.lower() in name.lower()
                ]
                if similar:
                    available_similar.extend(similar)

            error_msg = (
                f"Missing required airports: {missing_airports}. "
                f"Found airports: {found_airports}. "
                f"Similar available airports: {available_similar[:5]}"  # First 5 similar
            )

            allure_reporter.attach_json(
                {
                    "error": "Missing required airports",
                    "missing_airports": missing_airports,
                    "similar_available": available_similar,
                    "all_available_airports": airport_names,
                },
                "Missing Airports Debug Info",
            )

            raise AssertionError(error_msg)

        # All airports found successfully
        assertions.assert_equals(
            actual=len(found_airports),
            expected=len(required_airports),
            message=f"Expected all {len(required_airports)} airports to be found",
        )


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Airport Data Retrieval")
@allure.story("Airport Details Validation")
@allure.title("Verify required airports have complete information")
@allure.description(
    """
This test verifies that the required airports not only exist but also
have complete and valid information in their attributes.
"""
)
def test_required_airports_have_complete_information(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that required airports have complete attribute information.

    This test validates that the required airports have all necessary
    attributes populated with valid data for proper application functionality.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get required airports and expected fields"):
        api_expectations = get_api_expectations("airportgap_api")
        required_airports = api_expectations["airports"]["required_airports"]
        optional_fields = api_expectations["airports"]["optional_fields"]

    with allure.step("Fetch airports and find required ones"):
        airports = airports_client.get_all_airports()
        required_airport_objects = []

        for airport in airports:
            if airport.name in required_airports:
                required_airport_objects.append(airport)

        # Verify we found all required airports
        found_names = [airport.name for airport in required_airport_objects]
        missing_names = [name for name in required_airports if name not in found_names]

        if missing_names:
            pytest.fail(f"Required airports not found: {missing_names}")

    with allure.step("Validate attribute completeness for each required airport"):
        validation_results = []

        for airport in required_airport_objects:
            airport_validation = {
                "name": airport.name,
                "id": airport.id,
                "has_attributes": bool(airport.attributes),
                "attribute_count": len(airport.attributes) if airport.attributes else 0,
                "missing_fields": [],
                "present_fields": [],
            }

            # Check for basic required fields
            if not airport.name:
                airport_validation["missing_fields"].append("name")
            else:
                airport_validation["present_fields"].append("name")

            if not airport.id:
                airport_validation["missing_fields"].append("id")
            else:
                airport_validation["present_fields"].append("id")

            # Check optional fields that should be present
            if airport.attributes:
                for field in optional_fields:
                    if field in airport.attributes and airport.attributes[field]:
                        airport_validation["present_fields"].append(field)
                    else:
                        airport_validation["missing_fields"].append(field)

            validation_results.append(airport_validation)

        allure_reporter.attach_json(
            {
                "required_airports_count": len(required_airport_objects),
                "validation_results": validation_results,
            },
            "Airport Attribute Validation",
        )

    with allure.step("Assert all required airports have adequate information"):
        airports_with_issues = []

        for result in validation_results:
            # Allow some missing optional fields, but require basic information
            critical_missing = [
                field
                for field in result["missing_fields"]
                if field in ["name", "id", "iata", "city", "country"]
            ]

            if critical_missing:
                airports_with_issues.append(
                    {"airport": result["name"], "critical_missing": critical_missing}
                )

        if airports_with_issues:
            error_msg = f"Required airports missing critical information: {airports_with_issues}"
            raise AssertionError(error_msg)


@pytest.mark.api
@pytest.mark.regression
@allure.epic("API Testing")
@allure.feature("Airport Data Retrieval")
@allure.story("Case Sensitivity")
@allure.title("Verify airport search is case sensitive")
@allure.description(
    """
This test verifies that airport name matching is case-sensitive
and that the exact airport names are returned as expected.
"""
)
def test_airport_names_case_sensitivity(
    api_request_context: APIRequestContext, test_context: TestContext, allure_reporter
) -> None:
    """
    Verify that airport name matching is case-sensitive.

    This test validates that airport names are returned exactly as stored
    and that case-sensitive matching works correctly.

    Args:
        api_request_context: Playwright API request context
        test_context: Test execution context
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize AirportGap API client"):
        airports_client = AirportsClient(api_request_context, test_context)

    with allure.step("Get test airports with different case variations"):
        api_expectations = get_api_expectations("airportgap_api")
        required_airports = api_expectations["airports"]["required_airports"]

        # Create case variations for testing
        case_variations = {}
        for airport in required_airports:
            case_variations[airport] = {
                "original": airport,
                "lowercase": airport.lower(),
                "uppercase": airport.upper(),
                "title_case": airport.title(),
            }

    with allure.step("Fetch airport names from API"):
        airport_names = airports_client.get_airport_names()

    with allure.step("Test case sensitivity for each required airport"):
        case_test_results = []

        for airport in required_airports:
            variations = case_variations[airport]

            test_result = {
                "airport": airport,
                "exact_match": airport in airport_names,
                "lowercase_match": variations["lowercase"] in airport_names,
                "uppercase_match": variations["uppercase"] in airport_names,
                "title_case_match": variations["title_case"] in airport_names,
            }

            case_test_results.append(test_result)

        allure_reporter.attach_json(
            {
                "case_variations_tested": case_variations,
                "case_test_results": case_test_results,
            },
            "Case Sensitivity Test Results",
        )

    with allure.step("Verify exact case matching works correctly"):
        for result in case_test_results:
            airport = result["airport"]

            # The exact case should match
            assertions.assert_equals(
                actual=result["exact_match"],
                expected=True,
                message=f"Airport '{airport}' should be found with exact case matching",
            )

            # Other cases should not match (unless they happen to be the same)
            if airport != airport.lower():
                assertions.assert_equals(
                    actual=result["lowercase_match"],
                    expected=False,
                    message=f"Airport '{airport}' should not match lowercase version",
                )
