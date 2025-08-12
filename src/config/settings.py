"""
Configuration settings for the automation framework.

This module provides typed configuration using Pydantic settings for managing
environment variables, URLs, credentials, and timeouts across the test suite.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class SauceDemoSettings(BaseSettings):
    """Settings for SauceDemo UI testing."""

    base_url: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for SauceDemo application",
    )

    standard_user: str = Field(
        default="standard_user", description="Standard user username for login"
    )

    password: str = Field(
        default="secret_sauce", description="Password for SauceDemo users"
    )

    page_timeout: int = Field(
        default=30000, description="Page load timeout in milliseconds"
    )

    element_timeout: int = Field(
        default=10000, description="Element wait timeout in milliseconds"
    )

    class Config:
        env_prefix = "SAUCEDEMO_"


class AirportGapSettings(BaseSettings):
    """Settings for AirportGap API testing."""

    base_url: str = Field(
        default="https://airportgap.com", description="Base URL for AirportGap API"
    )

    api_timeout: int = Field(
        default=30000, description="API request timeout in milliseconds"
    )

    expected_airports_count: int = Field(
        default=30, description="Expected number of airports in the API response"
    )

    min_distance_kix_nrt: float = Field(
        default=400.0,
        description="Minimum expected distance between KIX and NRT airports in km",
    )

    class Config:
        env_prefix = "AIRPORTGAP_"


class BrowserSettings(BaseSettings):
    """Settings for browser configuration."""

    headless: bool = Field(default=True, description="Run browser in headless mode")

    browser_type: str = Field(
        default="chromium", description="Browser type: chromium, firefox, or webkit"
    )

    viewport_width: int = Field(default=1280, description="Browser viewport width")

    viewport_height: int = Field(default=720, description="Browser viewport height")

    slow_mo: int = Field(
        default=0, description="Slow down operations by specified milliseconds"
    )

    video: bool = Field(default=False, description="Record video of tests")

    screenshot_on_failure: bool = Field(
        default=True, description="Take screenshot on test failure"
    )

    class Config:
        env_prefix = "BROWSER_"


class TestSettings(BaseSettings):
    """General test execution settings."""

    environment: str = Field(
        default="local", description="Test environment: local, dev, staging, prod"
    )

    parallel_workers: int = Field(
        default=1, description="Number of parallel test workers"
    )

    retry_count: int = Field(
        default=0, description="Number of times to retry failed tests"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )

    allure_results_dir: str = Field(
        default="allure-results", description="Directory for Allure test results"
    )

    class Config:
        env_prefix = "TEST_"


class Settings(BaseSettings):
    """Main settings class combining all configuration sections."""

    saucedemo: SauceDemoSettings = Field(default_factory=SauceDemoSettings)
    airportgap: AirportGapSettings = Field(default_factory=AirportGapSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    test: TestSettings = Field(default_factory=TestSettings)

    @property
    def logs_dir(self) -> str:
        """Get the logs directory path, creating it if necessary."""
        logs_path = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_path, exist_ok=True)
        return logs_path


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.

    Returns:
        Settings: The configured settings instance
    """
    return settings


def override_settings(**kwargs) -> Settings:
    """
    Create a new settings instance with overridden values.

    Args:
        **kwargs: Key-value pairs to override in settings

    Returns:
        Settings: New settings instance with overrides
    """
    return Settings(**kwargs)
