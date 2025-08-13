"""
Base API client providing common functionality for all API interactions.

This module implements the foundation for API testing using Playwright's
APIRequestContext, providing reusable methods for HTTP requests, error handling,
and response processing that are shared across all API client classes.
"""

import json as json_module
import logging
import time
from typing import Any, Dict, List, Optional, Union

from playwright.sync_api import APIRequestContext, APIResponse

from src.config.settings import get_settings
from src.core.types import APIResponse as APIResponseType
from src.core.types import TestContext


class BaseAPIClient:
    """
    Abstract base class for all API clients.

    This class provides common functionality for API interactions including
    HTTP request methods, error handling, retry logic, and response parsing.
    All API clients should inherit from this class to ensure consistent behavior.

    Attributes:
        request_context: Playwright API request context
        context: Test execution context
        settings: Application settings
        logger: Logger instance for this client
    """

    def __init__(
        self, request_context: APIRequestContext, context: Optional[TestContext] = None
    ) -> None:
        """
        Initialize the base API client.

        Args:
            request_context: Playwright API request context
            context: Test execution context with correlation ID and metadata
        """
        self.request_context = request_context
        self.context = context
        self.settings = get_settings()
        base_logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Add correlation ID to logger context if available
        correlation_id = context.correlation_id if context else "unknown"
        self.logger: Union[
            logging.Logger, logging.LoggerAdapter[logging.Logger]
        ] = logging.LoggerAdapter(base_logger, {"correlation_id": correlation_id})

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> APIResponseType:
        """
        Make an HTTP request with comprehensive logging and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL (can be relative or absolute)
            headers: Optional request headers
            data: Optional request body as string or bytes
            json: Optional JSON request body (will be serialized)
            params: Optional query parameters
            timeout: Request timeout in milliseconds

        Returns:
            APIResponseType: Typed response object with status, headers, and body

        Raises:
            APIError: If request fails or response indicates error
        """
        timeout_ms = timeout or self.settings.airportgap.api_timeout

        # Prepare request details for logging
        full_url = self._build_url(url)
        request_headers = self._prepare_headers(headers)
        request_body = self._prepare_body(data, json)

        self.logger.info(
            f"Making {method} request to {full_url}",
            extra={
                "method": method,
                "url": full_url,
                "headers_count": len(request_headers) if request_headers else 0,
                "has_body": bool(request_body),
                "timeout_ms": timeout_ms,
            },
        )

        start_time = time.time()

        try:
            # Make the actual request
            response = self._execute_request(
                method=method,
                url=full_url,
                headers=request_headers,
                data=request_body,
                params=params,
                timeout=timeout_ms,
            )

            duration_ms = (time.time() - start_time) * 1000

            # Parse response body
            parsed_body = self._parse_response_body(response)

            # Create typed response object
            api_response = APIResponseType(
                status_code=response.status,
                headers=dict(response.headers),
                body=parsed_body,
                url=response.url,
                method=method,
                duration_ms=duration_ms,
            )

            self.logger.info(
                f"Request completed: {method} {full_url}",
                extra={
                    "status_code": response.status,
                    "duration_ms": duration_ms,
                    "response_size": len(str(parsed_body)),
                },
            )

            # Log response body at debug level
            if parsed_body:
                self.logger.debug(
                    f"Response body: {json_module.dumps(parsed_body, indent=2)}"
                )
            else:
                self.logger.debug("Response body: None or empty")

            return api_response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Request failed: {method} {full_url}",
                extra={
                    "error": str(e),
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
            )
            raise

    def _build_url(self, url: str) -> str:
        """
        Build the full URL from a potentially relative URL.

        Args:
            url: URL path or full URL

        Returns:
            str: Complete URL
        """
        if url.startswith(("http://", "https://")):
            return url

        base_url = self.settings.airportgap.base_url
        return f"{base_url.rstrip('/')}/{url.lstrip('/')}"

    def _prepare_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Prepare request headers with defaults.

        Args:
            headers: Optional custom headers

        Returns:
            Dict[str, str]: Complete headers dictionary
        """
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Playwright-Automation-Framework/1.0",
        }

        if headers:
            default_headers.update(headers)

        return default_headers

    def _prepare_body(
        self, data: Optional[Union[str, bytes]], json_data: Optional[Dict[str, Any]]
    ) -> Optional[Union[str, bytes]]:
        """
        Prepare request body from data or JSON.

        Args:
            data: Raw request body
            json_data: JSON data to be serialized

        Returns:
            Optional[Union[str, bytes]]: Prepared request body
        """
        if json_data is not None:
            return json_module.dumps(json_data)
        return data

    def _execute_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Optional[Union[str, bytes]],
        params: Optional[Dict[str, str]],
        timeout: int,
    ) -> APIResponse:
        """
        Execute the HTTP request using Playwright's request context.

        Args:
            method: HTTP method
            url: Full URL
            headers: Request headers
            data: Request body
            params: Query parameters
            timeout: Request timeout

        Returns:
            APIResponse: Playwright API response
        """
        # Playwright APIRequestContext expects specific types for kwargs
        request_kwargs: Dict[str, Any] = {"timeout": timeout, "headers": headers}

        if data is not None:
            request_kwargs["data"] = data

        if params is not None:
            request_kwargs["params"] = params

        # Execute request based on method
        if method.upper() == "GET":
            return self.request_context.get(url, **request_kwargs)
        elif method.upper() == "POST":
            return self.request_context.post(url, **request_kwargs)
        elif method.upper() == "PUT":
            return self.request_context.put(url, **request_kwargs)
        elif method.upper() == "DELETE":
            return self.request_context.delete(url, **request_kwargs)
        elif method.upper() == "PATCH":
            return self.request_context.patch(url, **request_kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def _parse_response_body(self, response: APIResponse) -> Union[Dict[str, Any], str]:
        """
        Parse response body as JSON or return as string.

        Args:
            response: Playwright API response

        Returns:
            Union[Dict[str, Any], str]: Parsed JSON or raw string
        """
        try:
            body_text = response.text()
            if not body_text:
                return ""

            # Try to parse as JSON
            return json_module.loads(body_text)  # type: ignore

        except json_module.JSONDecodeError:
            # Return as string if not valid JSON
            return response.text()
        except Exception as e:
            self.logger.warning(f"Failed to parse response body: {str(e)}")
            return ""

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> APIResponseType:
        """
        Make a GET request.

        Args:
            url: Request URL
            headers: Optional request headers
            params: Optional query parameters
            timeout: Request timeout in milliseconds

        Returns:
            APIResponseType: Response object
        """
        return self._make_request(
            "GET", url, headers=headers, params=params, timeout=timeout
        )

    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> APIResponseType:
        """
        Make a POST request.

        Args:
            url: Request URL
            json: Optional JSON request body
            data: Optional raw request body
            headers: Optional request headers
            timeout: Request timeout in milliseconds

        Returns:
            APIResponseType: Response object
        """
        return self._make_request(
            "POST", url, headers=headers, data=data, json=json, timeout=timeout
        )

    def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> APIResponseType:
        """
        Make a PUT request.

        Args:
            url: Request URL
            json: Optional JSON request body
            data: Optional raw request body
            headers: Optional request headers
            timeout: Request timeout in milliseconds

        Returns:
            APIResponseType: Response object
        """
        return self._make_request(
            "PUT", url, headers=headers, data=data, json=json, timeout=timeout
        )

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> APIResponseType:
        """
        Make a DELETE request.

        Args:
            url: Request URL
            headers: Optional request headers
            timeout: Request timeout in milliseconds

        Returns:
            APIResponseType: Response object
        """
        return self._make_request("DELETE", url, headers=headers, timeout=timeout)

    def verify_response_status(
        self, response: APIResponseType, expected_status: int = 200
    ) -> None:
        """
        Verify that the response has the expected status code.

        Args:
            response: API response to verify
            expected_status: Expected HTTP status code

        Raises:
            AssertionError: If status code doesn't match expected
        """
        if response.status_code != expected_status:
            error_msg = (
                f"Expected status code {expected_status}, got {response.status_code}. "
                f"Response: {response.body}"
            )
            self.logger.error(error_msg)
            raise AssertionError(error_msg)

        self.logger.debug(
            f"Response status verification passed: {response.status_code}"
        )

    def verify_response_contains_keys(
        self, response: APIResponseType, required_keys: List[str]
    ) -> None:
        """
        Verify that the response JSON contains all required keys.

        Args:
            response: API response to verify
            required_keys: List of required keys in response

        Raises:
            AssertionError: If any required key is missing
        """
        if not isinstance(response.body, dict):
            raise AssertionError(
                f"Response body is not a JSON object: {type(response.body)}"
            )

        missing_keys = [key for key in required_keys if key not in response.body]

        if missing_keys:
            error_msg = (
                f"Missing required keys in response: {missing_keys}. "
                f"Available keys: {list(response.body.keys())}"
            )
            self.logger.error(error_msg)
            raise AssertionError(error_msg)

        self.logger.debug(f"Response keys verification passed: {required_keys}")
