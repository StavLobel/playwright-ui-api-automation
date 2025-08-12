"""
Custom logging formatter that handles missing correlation_id gracefully.

This module provides a safe formatter that won't crash when correlation_id
is missing from the log record.
"""

import logging


class SafeFormatter(logging.Formatter):
    """
    A safe formatter that handles missing fields gracefully.

    This formatter extends the standard logging.Formatter to safely handle
    missing fields like correlation_id without causing crashes.
    """

    def format(self, record):
        """
        Format the log record safely.

        Args:
            record: LogRecord instance

        Returns:
            str: Formatted log message
        """
        # Ensure correlation_id exists, default to "unknown" if missing
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "unknown"

        # Ensure other common fields exist
        if not hasattr(record, "filename"):
            record.filename = "unknown"
        if not hasattr(record, "lineno"):
            record.lineno = 0

        return super().format(record)
