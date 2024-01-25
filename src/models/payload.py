"""
This module defines the Payload class, which is used for handling JSON payload data. It offers functionalities
for initializing the payload with data, retrieving and setting key-value pairs, and removing keys. This class
is useful in scenarios where JSON data needs to be dynamically manipulated, such as in API request and
response handling.
"""


class Payload:
    """
    Represents a JSON payload, providing methods to manipulate key-value data.

    The Payload class offers a convenient way to manage JSON data. It can be initialized with existing data,
    and provides methods to add, retrieve, update, or delete key-value pairs within the payload. It is
    designed for ease of use when dealing with JSON structures, particularly in contexts such as API
    interactions or data processing.

    Attributes:
        _json_obj (dict): The internal dictionary to store the payload data.
    """

    def __init__(self, initial_data: dict = None):
        """
        Initializes the Payload object with optional initial data.

        Parameters:
            initial_data (dict, optional): Initial data to populate the payload.
        """

        self._json_obj = initial_data if initial_data is not None else {}

    def get_data(self) -> dict:
        """
        Returns the JSON object representing the payload.

        Returns:
            dict: The payload data.
        """

        return self._json_obj

    def get_id(self) -> str:
        """
        Retrieves the 'id' value from the payload.

        Returns:
            str: The 'id' value.

        Raises:
            KeyError: If 'id' is not in the payload.
        """

        return self._json_obj["id"]

    def set_key_and_or_value(self, key: str, value) -> "Payload":
        """
        Sets a key-value pair in the payload.

        Parameters:
            key (str): The key to set.
            value: The value to associate with the key.

        Returns:
            Payload: The instance of the Payload for method chaining.
        """

        self._json_obj[key] = value
        return self

    def remove_key(self, key: str):
        """
        Removes a key from the payload.

        Parameters:
            key (str): The key to remove.

        Raises:
            KeyError: If the key is not in the payload.
        """

        if key in self._json_obj:
            del self._json_obj[key]
        else:
            raise KeyError(f"Key '{key}' not found in payload.")
