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


# def post(endpoint: str):
#     """_summary_"""
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             print(f"POST request to {endpoint}")
#             return func(*args, endpoint, **kwargs)

#         return wrapper

#     return decorator


def put(endpoint: str, identification: int):
    """_summary_"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if identification is None:
                print(f"PUT request to {endpoint}")
            else:
                print(f"PUT request to {endpoint}/{identification}")
            return func(*args, endpoint, identification, **kwargs)

        return wrapper

    return decorator


# def delete(endpoint: str):
#     """_summary_"""
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             print(f"DELETE request to {endpoint}")
#             return func(*args, endpoint, **kwargs)

#         return wrapper

#     return decorator
