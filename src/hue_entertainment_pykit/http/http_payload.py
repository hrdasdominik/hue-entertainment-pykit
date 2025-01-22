"""
This module defines the HttpPayload class, which is used for handling JSON http_request data. It offers functionalities
for initializing the http_request with data, retrieving and setting key-value pairs, and removing keys. This class
is useful in scenarios where JSON data needs to be dynamically manipulated, such as in API request and
response handling.
"""


class HttpPayload:
    """
    Represents a JSON http_request, providing methods to manipulate key-value data.

    The HttpPayload class offers a convenient way to manage JSON data. It can be initialized with existing data,
    and provides methods to add, retrieve, update, or delete key-value pairs within the http_request. It is
    designed for ease of use when dealing with JSON structures, particularly in contexts such as API
    interactions or data processing.

    Attributes:
        _json_obj (dict): The internal dictionary to store the http_request data.
    """

    def __init__(self, initial_data: dict = None):
        """
        Initializes the HttpPayload object with optional initial data.

        Parameters:
            initial_data (dict, optional): Initial data to populate the http_request.
        """

        self._json_obj = initial_data if initial_data is not None else {}

    def get_data(self) -> dict:
        """
        Returns the JSON object representing the http_request.

        Returns:
            dict: The http_request data.
        """

        return self._json_obj

    def set_key_and_or_value(self, key: str, value) -> "HttpPayload":
        """
        Sets a key-value pair in the http_request.

        Parameters:
            key (str): The key to set.
            value: The value to associate with the key.

        Returns:
            HttpPayload: The instance of the Payload for http_method chaining.
        """

        self._json_obj[key] = value
        return self

    def remove_key(self, key: str):
        """
        Removes a key from the http_request.

        Parameters:
            key (str): The key to remove.

        Raises:
            KeyError: If the key is not in the http_request.
        """

        if key in self._json_obj:
            del self._json_obj[key]
        else:
            raise KeyError(f"Key '{key}' not found in http_request.")
