from enum import Enum


class HttpMethodEnum(Enum):
    """Enum class for a HTTP/S request http_method"""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"