"""
This module defines an enumeration for standard HTTP status codes. It includes status codes for successful responses,
client errors, and server errors, providing an easy and readable way to use these values throughout the code.
"""

from enum import Enum


class StatusCode(Enum):
    """Enum class for response status code"""

    OK = 200
    CREATED = 201
    MULTI_STATUS = 207
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
