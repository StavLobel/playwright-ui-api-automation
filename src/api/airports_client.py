"""
AirportGap API client implementation.

This module provides a client for interacting with the AirportGap API,
including methods for retrieving airport information and calculating
distances between airports.
"""

from typing import Dict, List, Optional

import allure
from playwright.sync_api import APIRequestContext

from src.core.assertions import get_assertion_helper
from src.core.base_api_client import BaseAPIClient
from src.core.types import Airport, DistanceCalculation, TestContext


class AirportsClient(BaseAPIClient):
    """
    Client for interacting with the AirportGap API.

    This client provides methods for retrieving airport information and calculating
    distances between airports. It handles authentication, error handling,
    and response parsing with comprehensive logging and validation.

    API Documentation: https://airportgap.com/docs
    """

    def __init__(
        self, request_context: APIRequestContext, context: Optional[TestContext] = None
    ) -> None:
        """
        Initialize the AirportGap API client.

        Args:
            request_context: Playwright API request context
            context: Test execution context with correlation ID
        """
        super().__init__(request_context, context)
        self.assertions = get_assertion_helper(self.logger)

    @allure.step("Get all airports from API")
    def get_all_airports(self) -> List[Airport]:
        """
        Retrieve all airports from the AirportGap API.

        This method fetches the complete list of airports available in the API
        and returns them as typed Airport objects for easier manipulation.

        Returns:
            List[Airport]: List of airport objects with parsed data

        Raises:
            AssertionError: If API response is invalid or missing required data
            Exception: If request fails or times out
        """
        self.logger.info("Fetching all airports from AirportGap API")

        try:
            # Make the API request
            response = self.get("/api/airports")

            # Verify response status
            self.verify_response_status(response, 200)

            # Verify response structure
            if not isinstance(response.body, dict):
                raise AssertionError(
                    f"Expected JSON response, got {type(response.body)}"
                )

            self.verify_response_contains_keys(response, ["data"])

            # Extract airports data
            airports_data = response.body.get("data", [])

            if not isinstance(airports_data, list):
                raise AssertionError(
                    f"Expected 'data' to be a list, got {type(airports_data)}"
                )

            # Convert to Airport objects
            airports = []
            for airport_data in airports_data:
                try:
                    airport = Airport(
                        id=airport_data.get("id", ""),
                        type=airport_data.get("type", ""),
                        attributes=airport_data.get("attributes", {}),
                    )
                    airports.append(airport)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse airport data: {airport_data} - {str(e)}"
                    )

            self.logger.info(f"Successfully retrieved {len(airports)} airports")

            # Attach response data for reporting
            allure.attach(
                str(response.body),
                name="Airports API Response",
                attachment_type=allure.attachment_type.JSON,
            )

            return airports

        except Exception as e:
            self.logger.error(f"Failed to get airports: {str(e)}")
            raise

    @allure.step("Get airports count")
    def get_airports_count(self) -> int:
        """
        Get the total number of airports available in the API.

        Returns:
            int: Total number of airports

        Raises:
            Exception: If request fails or response is invalid
        """
        self.logger.info("Getting airports count")

        try:
            airports = self.get_all_airports()
            count = len(airports)

            self.logger.info(f"Total airports count: {count}")
            return count

        except Exception as e:
            self.logger.error(f"Failed to get airports count: {str(e)}")
            raise

    @allure.step("Get airport names list")
    def get_airport_names(self) -> List[str]:
        """
        Get a list of all airport names from the API.

        Returns:
            List[str]: List of airport names

        Raises:
            Exception: If request fails or response is invalid
        """
        self.logger.info("Getting list of airport names")

        try:
            airports = self.get_all_airports()
            names = [airport.name for airport in airports if airport.name]

            self.logger.debug(f"Retrieved {len(names)} airport names")
            return names

        except Exception as e:
            self.logger.error(f"Failed to get airport names: {str(e)}")
            raise

    @allure.step("Verify specific airports exist: {required_airports}")
    def verify_airports_exist(self, required_airports: List[str]) -> Dict[str, bool]:
        """
        Verify that specific airports exist in the API response.

        Args:
            required_airports: List of airport names to verify

        Returns:
            Dict[str, bool]: Dictionary mapping airport names to existence status

        Raises:
            AssertionError: If any required airport is not found
        """
        self.logger.info(f"Verifying airports exist: {required_airports}")

        try:
            airport_names = self.get_airport_names()
            verification_results = {}
            missing_airports = []

            for required_airport in required_airports:
                exists = required_airport in airport_names
                verification_results[required_airport] = exists

                if not exists:
                    missing_airports.append(required_airport)
                    self.logger.warning(f"Airport not found: {required_airport}")
                else:
                    self.logger.debug(f"Airport found: {required_airport}")

            # Report results
            allure.attach(
                str(
                    {
                        "required_airports": required_airports,
                        "verification_results": verification_results,
                        "missing_airports": missing_airports,
                        "total_available_airports": len(airport_names),
                    }
                ),
                name="Airport Existence Verification",
                attachment_type=allure.attachment_type.JSON,
            )

            # Assert that all required airports exist
            if missing_airports:
                error_msg = (
                    f"Missing required airports: {missing_airports}. "
                    f"Available airports: {airport_names}"
                )
                self.logger.error(error_msg)
                raise AssertionError(error_msg)

            self.logger.info(f"All required airports verified: {required_airports}")
            return verification_results

        except Exception as e:
            self.logger.error(f"Failed to verify airports exist: {str(e)}")
            raise

    @allure.step("Calculate distance between {from_airport} and {to_airport}")
    def calculate_distance(
        self, from_airport: str, to_airport: str
    ) -> DistanceCalculation:
        """
        Calculate distance between two airports using their IATA codes.

        Args:
            from_airport: Origin airport IATA code (e.g., "KIX")
            to_airport: Destination airport IATA code (e.g., "NRT")

        Returns:
            DistanceCalculation: Distance calculation results with multiple units

        Raises:
            AssertionError: If API response is invalid or airports not found
            Exception: If request fails or times out
        """
        self.logger.info(f"Calculating distance from {from_airport} to {to_airport}")

        try:
            # Prepare request payload
            payload = {"from": from_airport, "to": to_airport}

            # Make the API request
            response = self.post("/api/airports/distance", json=payload)

            # Verify response status
            self.verify_response_status(response, 200)

            # Verify response structure
            if not isinstance(response.body, dict):
                raise AssertionError(
                    f"Expected JSON response, got {type(response.body)}"
                )

            self.verify_response_contains_keys(response, ["data"])

            # Extract distance data
            data = response.body.get("data", {})
            attributes = data.get("attributes", {})

            # Verify required distance fields
            required_fields = ["kilometers", "miles", "nautical_miles"]
            missing_fields = [
                field for field in required_fields if field not in attributes
            ]

            if missing_fields:
                raise AssertionError(f"Missing distance fields: {missing_fields}")

            # Extract airport information
            from_airport_data = (
                data.get("relationships", {}).get("from", {}).get("data", {})
            )
            to_airport_data = (
                data.get("relationships", {}).get("to", {}).get("data", {})
            )

            # Create Airport objects (simplified for distance calculation)
            from_airport_obj = Airport(
                id=from_airport_data.get("id", from_airport),
                type=from_airport_data.get("type", "airport"),
                attributes={"iata": from_airport},
            )

            to_airport_obj = Airport(
                id=to_airport_data.get("id", to_airport),
                type=to_airport_data.get("type", "airport"),
                attributes={"iata": to_airport},
            )

            # Create distance calculation object
            distance_calc = DistanceCalculation(
                from_airport=from_airport_obj,
                to_airport=to_airport_obj,
                kilometers=float(attributes["kilometers"]),
                miles=float(attributes["miles"]),
                nautical_miles=float(attributes["nautical_miles"]),
            )

            self.logger.info(
                f"Distance calculation successful: {distance_calc.kilometers:.2f} km "
                f"({distance_calc.miles:.2f} miles, {distance_calc.nautical_miles:.2f} nm)"
            )

            # Attach response data for reporting
            allure.attach(
                str(
                    {
                        "from_airport": from_airport,
                        "to_airport": to_airport,
                        "kilometers": distance_calc.kilometers,
                        "miles": distance_calc.miles,
                        "nautical_miles": distance_calc.nautical_miles,
                        "request_payload": payload,
                        "response_time_ms": response.duration_ms,
                    }
                ),
                name="Distance Calculation Results",
                attachment_type=allure.attachment_type.JSON,
            )

            return distance_calc

        except Exception as e:
            self.logger.error(f"Failed to calculate distance: {str(e)}")

            # Attach error details for debugging
            allure.attach(
                str(
                    {
                        "from_airport": from_airport,
                        "to_airport": to_airport,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                ),
                name="Distance Calculation Error",
                attachment_type=allure.attachment_type.JSON,
            )

            raise

    @allure.step("Verify distance is greater than {min_distance} km")
    def verify_distance_greater_than(
        self, from_airport: str, to_airport: str, min_distance: float
    ) -> float:
        """
        Verify that the distance between two airports is greater than a minimum value.

        Args:
            from_airport: Origin airport IATA code
            to_airport: Destination airport IATA code
            min_distance: Minimum expected distance in kilometers

        Returns:
            float: Actual distance in kilometers

        Raises:
            AssertionError: If distance is not greater than minimum
        """
        self.logger.info(
            f"Verifying distance {from_airport} to {to_airport} > {min_distance} km"
        )

        try:
            # Calculate distance
            distance_calc = self.calculate_distance(from_airport, to_airport)
            actual_distance = distance_calc.kilometers

            # Verify distance is greater than minimum
            self.assertions.assert_greater_than(
                actual=actual_distance,
                threshold=min_distance,
                message=(
                    f"Distance between {from_airport} and {to_airport} "
                    f"({actual_distance:.2f} km) should be greater than {min_distance} km"
                ),
            )

            self.logger.info(
                f"Distance verification successful: {actual_distance:.2f} km > {min_distance} km"
            )

            return actual_distance

        except Exception as e:
            self.logger.error(f"Distance verification failed: {str(e)}")
            raise

    def get_airport_by_iata_code(self, iata_code: str) -> Optional[Airport]:
        """
        Get airport information by IATA code.

        Args:
            iata_code: IATA airport code (e.g., "KIX", "NRT")

        Returns:
            Optional[Airport]: Airport object if found, None otherwise
        """
        self.logger.debug(f"Looking up airport by IATA code: {iata_code}")

        try:
            airports = self.get_all_airports()

            for airport in airports:
                if airport.iata_code.upper() == iata_code.upper():
                    self.logger.debug(f"Found airport: {airport.name} ({iata_code})")
                    return airport

            self.logger.warning(f"Airport not found for IATA code: {iata_code}")
            return None

        except Exception as e:
            self.logger.error(f"Failed to lookup airport by IATA code: {str(e)}")
            return None
