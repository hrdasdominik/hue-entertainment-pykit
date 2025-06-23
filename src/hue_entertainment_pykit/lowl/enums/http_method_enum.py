from enum import Enum


class HttpMethodEnum(Enum):
    """Enum class for HTTP/S request method"""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"