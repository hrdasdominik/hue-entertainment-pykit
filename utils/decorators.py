"""_summary_"""

from functools import wraps
from typing import Callable
from utils.logger import logging


def get(endpoint: str) -> Callable:
    """A decorator for GET requests."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, identification: str = None) -> dict:
            if "{identification}" in endpoint:
                if identification is None:
                    raise ValueError("Missing required identification for endpoint.")
                formatted_endpoint = endpoint.format(identification=identification)
            else:
                formatted_endpoint = endpoint

            logging.info(f"GET request to {formatted_endpoint}")
            return func(self, formatted_endpoint)

        return wrapper

    return decorator

def post(endpoint: str):
    """A decorator for POST requests"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, identification: str = None, *args, **kwargs) -> dict:
            if "{identification}" in endpoint:
                if identification is None:
                    raise ValueError("Missing required identification for endpoint.")
                formatted_endpoint = endpoint.format(identification=identification)
            else:
                formatted_endpoint = endpoint

            logging.info(f"POST request to {formatted_endpoint}")
            return func(self, formatted_endpoint, *args, **kwargs)

        return wrapper

    return decorator


def put(endpoint: str):
    """A decorator for PUT requests"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, identification: str = None, *args, **kwargs) -> dict:
            if "{identification}" in endpoint:
                if identification is None:
                    raise ValueError("Missing required identification for endpoint.")
                formatted_endpoint = endpoint.format(identification=identification)
            else:
                formatted_endpoint = endpoint

            logging.info(f"PUT request to {formatted_endpoint}")
            return func(self, formatted_endpoint, *args, **kwargs)

        return wrapper

    return decorator


def delete(endpoint: str):
    """A decorator for DELETE requests"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, identification: str = None, *args, **kwargs) -> dict:
            if "{identification}" in endpoint:
                if identification is None:
                    raise ValueError("Missing required identification for endpoint.")
                formatted_endpoint = endpoint.format(identification=identification)
            else:
                formatted_endpoint = endpoint

            logging.info(f"DELETE request to {formatted_endpoint}")
            return func(self, formatted_endpoint, *args, **kwargs)

        return wrapper

    return decorator
