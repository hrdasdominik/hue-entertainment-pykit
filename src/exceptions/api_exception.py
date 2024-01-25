"""
Defines the ApiException class, a custom exception for handling errors in API requests. This class is used
throughout the application for consistent and clear error handling related to API communication issues.
"""


class ApiException(Exception):
    """
    Custom exception class for API-related errors.

    This class extends the base Exception class to provide a more specific exception type for handling errors
    encountered during API interactions, enhancing error reporting and handling.
    """
