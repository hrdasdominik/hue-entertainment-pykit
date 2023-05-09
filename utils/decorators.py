"""_summary_"""

from functools import wraps


def get(endpoint: str):
    """_summary_"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"GET request to {endpoint}")
            return func(*args, endpoint, **kwargs)

        return wrapper

    return decorator


def post(endpoint: str):
    """_summary_"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"POST request to {endpoint}")
            return func(*args, endpoint, **kwargs)

        return wrapper

    return decorator


def put(endpoint: str):
    """_summary_"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"PUT request to {endpoint}")
            return func(*args, endpoint, **kwargs)

        return wrapper

    return decorator


def delete(endpoint: str):
    """_summary_"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"DELETE request to {endpoint}")
            return func(*args, endpoint, **kwargs)

        return wrapper

    return decorator
