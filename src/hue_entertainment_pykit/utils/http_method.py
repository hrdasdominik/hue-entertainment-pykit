from enum import Enum


class HttpMethod(Enum):
    """Enum class for a HTTP/S request method"""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"