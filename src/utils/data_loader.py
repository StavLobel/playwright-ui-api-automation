"""
Test data loading utilities.

This module provides functions for loading and managing test data from
external files (YAML, JSON) with proper error handling and validation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.core.types import TestData


class DataLoader:
    """
    Utility class for loading test data from external files.

    This class provides methods for loading YAML and JSON test data files
    with proper error handling, caching, and validation.
    """

    def __init__(self, base_path: Optional[str] = None) -> None:
        """
        Initialize the data loader.

        Args:
            base_path: Base directory path for data files (defaults to testdata/)
        """
        self.base_path = Path(base_path or "testdata")
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, TestData] = {}

    def load_yaml(self, filename: str, use_cache: bool = True) -> TestData:
        """
        Load data from a YAML file.

        Args:
            filename: YAML filename (with or without .yaml extension)
            use_cache: Whether to use cached data if available

        Returns:
            TestData: Loaded data dictionary

        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is invalid
        """
        # Ensure .yaml extension
        if not filename.endswith(".yaml") and not filename.endswith(".yml"):
            filename += ".yaml"

        # Check cache first
        if use_cache and filename in self._cache:
            self.logger.debug(f"Loading cached YAML data: {filename}")
            return self._cache[filename]

        file_path = self.base_path / filename

        try:
            self.logger.debug(f"Loading YAML file: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Cache the loaded data
            if use_cache:
                self._cache[filename] = data

            self.logger.info(f"Successfully loaded YAML data: {filename}")
            return data

        except FileNotFoundError:
            self.logger.error(f"YAML file not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in file {filename}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error loading YAML file {filename}: {str(e)}"
            )
            raise

    def load_json(self, filename: str, use_cache: bool = True) -> TestData:
        """
        Load data from a JSON file.

        Args:
            filename: JSON filename (with or without .json extension)
            use_cache: Whether to use cached data if available

        Returns:
            TestData: Loaded data dictionary

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the JSON is invalid
        """
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        # Check cache first
        if use_cache and filename in self._cache:
            self.logger.debug(f"Loading cached JSON data: {filename}")
            return self._cache[filename]

        file_path = self.base_path / filename

        try:
            self.logger.debug(f"Loading JSON file: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Cache the loaded data
            if use_cache:
                self._cache[filename] = data

            self.logger.info(f"Successfully loaded JSON data: {filename}")
            return data

        except FileNotFoundError:
            self.logger.error(f"JSON file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {filename}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error loading JSON file {filename}: {str(e)}"
            )
            raise

    def get_user_credentials(self, user_type: str = "standard_user") -> Dict[str, str]:
        """
        Get user credentials from the users data file.

        Args:
            user_type: Type of user to get credentials for

        Returns:
            Dict[str, str]: User credentials with username and password

        Raises:
            KeyError: If user type is not found
        """
        users_data = self.load_yaml("users")

        try:
            user_data = users_data["saucedemo_users"][user_type]
            return {
                "username": user_data["username"],
                "password": user_data["password"],
            }
        except KeyError:
            available_users = list(users_data.get("saucedemo_users", {}).keys())
            self.logger.error(
                f"User type '{user_type}' not found. Available users: {available_users}"
            )
            raise

    def get_api_expectations(self, api_name: str) -> Dict[str, Any]:
        """
        Get API test expectations from the API expected data file.

        Args:
            api_name: Name of the API to get expectations for

        Returns:
            Dict[str, Any]: API test expectations

        Raises:
            KeyError: If API name is not found
        """
        api_data = self.load_yaml("api_expected")

        try:
            return api_data[api_name]
        except KeyError:
            available_apis = list(api_data.keys())
            self.logger.error(
                f"API '{api_name}' not found. Available APIs: {available_apis}"
            )
            raise

    def get_expected_airports(self) -> Dict[str, Any]:
        """
        Get expected airports data for API testing.

        Returns:
            Dict[str, Any]: Expected airports data including count and required airports
        """
        return self.get_api_expectations("airportgap_api")["airports"]

    def get_expected_distance_data(self, route: str = "kix_to_nrt") -> Dict[str, Any]:
        """
        Get expected distance calculation data.

        Args:
            route: Distance calculation route identifier

        Returns:
            Dict[str, Any]: Expected distance data
        """
        return self.get_api_expectations("airportgap_api")["distance_calculations"][
            route
        ]

    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()
        self.logger.debug("Data cache cleared")

    def list_available_files(self, extension: Optional[str] = None) -> list[str]:
        """
        List available data files in the base directory.

        Args:
            extension: Optional file extension filter (e.g., '.yaml', '.json')

        Returns:
            list[str]: List of available filenames
        """
        try:
            if extension:
                files = list(self.base_path.glob(f"*{extension}"))
            else:
                files = [f for f in self.base_path.iterdir() if f.is_file()]

            return [f.name for f in files]

        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            return []


# Global data loader instance
data_loader = DataLoader()


def load_test_data(filename: str, file_type: str = "yaml") -> TestData:
    """
    Load test data from a file.

    Args:
        filename: Data filename
        file_type: File type ('yaml' or 'json')

    Returns:
        TestData: Loaded data dictionary
    """
    if file_type.lower() == "json":
        return data_loader.load_json(filename)
    else:
        return data_loader.load_yaml(filename)


def get_user_credentials(user_type: str = "standard_user") -> Dict[str, str]:
    """
    Get user credentials for testing.

    Args:
        user_type: Type of user credentials to retrieve

    Returns:
        Dict[str, str]: User credentials
    """
    return data_loader.get_user_credentials(user_type)


def get_api_expectations(api_name: str) -> Dict[str, Any]:
    """
    Get API test expectations.

    Args:
        api_name: Name of the API

    Returns:
        Dict[str, Any]: API expectations
    """
    return data_loader.get_api_expectations(api_name)
