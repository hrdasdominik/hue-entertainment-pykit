"""
This module defines the Bridge class, which represents a Philips Hue Bridge. A Bridge is the central hub
of the Philips Hue system and manages the communication between the Hue lights and controllers. This
class encapsulates the properties and behaviors of a Hue Bridge, such as handling identification,
configuration, and state information.
"""


class Bridge:
    """
    Represents a Philips Hue Bridge, the central hub of the Philips Hue system.

    This class encapsulates the properties of a Hue Bridge, such as identification,
    resource identifier (rid), IP address, software version, username, Hue application ID,
    client key, and name. It provides methods to access these properties and convert
    bridge information to and from dictionary format.

    Attributes:
        _identification (str): Unique identifier of the Bridge.
        _rid (str): Resource identifier of the Bridge.
        _ip_address (str): IP address of the Bridge.
        _swversion (int): Software version of the Bridge.
        _username (str): Username used for authentication with the Bridge.
        _hue_app_id (str): Hue application ID.
        _client_key (str): Client key for secure communication with the Bridge.
        _name (str): Human-readable name of the Bridge.

    Parameters:
        identification (str): Unique identifier of the Bridge. Defaults to an empty string.
        rid (str): Resource identifier of the Bridge. Defaults to an empty string.
        ip_address (str): IP address of the Bridge. Defaults to an empty string.
        swversion (int): Software version of the Bridge. Defaults to 0.
        username (str): Username used for authentication with the Bridge. Defaults to an empty string.
        hue_app_id (str): Hue application ID. Defaults to an empty string.
        client_key (str): Client key for secure communication with the Bridge. Defaults to an empty string.
        name (str): Human-readable name of the Bridge. Defaults to an empty string.
    """

    # pylint: disable=too-many-positional-arguments

    def __init__(
        self,
        identification: str = "",
        rid: str = "",
        ip_address: str = "",
        swversion: int = 0,
        username: str = "",
        hue_app_id: str = "",
        client_key: str = "",
        name: str = "",
    ):
        # pylint: disable=too-many-arguments
        self._identification = identification
        self._rid = rid
        self._ip_address = ip_address
        self._swversion = swversion
        self._username = username
        self._hue_app_id = hue_app_id
        self._client_key = client_key
        self._name = name

    def get_identification(self) -> str:
        """
        Retrieves the unique identification of the Bridge.

        Returns:
            str: The identification of the Bridge.
        """

        return self._identification

    def get_rid(self) -> str:
        """
        Retrieves the resource identifier (rid) of the Bridge.

        Returns:
            str: The resource identifier of the Bridge.
        """

        return self._rid

    def get_ip_address(self) -> str:
        """
        Retrieves the IP address of the Bridge.

        Returns:
            str: The IP address of the Bridge.
        """

        return self._ip_address

    def get_swversion(self) -> int:
        """
        Retrieves the software version of the Bridge.

        Returns:
            int: The software version of the Bridge.
        """

        return self._swversion

    def get_username(self) -> str:
        """
        Retrieves the username used for authentication with the Bridge.

        Returns:
            str: The username for the Bridge.
        """

        return self._username

    def get_hue_application_id(self) -> str:
        """
        Retrieves the Hue application ID associated with the Bridge.

        Returns:
            str: The Hue application ID.
        """

        return self._hue_app_id

    def get_client_key(self) -> str:
        """
        Retrieves the client key used for secure communication with the Bridge.

        Returns:
            str: The client key for the Bridge.
        """

        return self._client_key

    def get_name(self) -> str:
        """
        Retrieves the human-readable name of the Bridge.

        Returns:
            str: The name of the Bridge.
        """

        return self._name

    def to_dict(self):
        """
        Converts the Bridge's attributes to a dictionary.

        Returns:
            dict: A dictionary representing the Bridge's attributes.
        """

        return {
            "id": self._identification,
            "rid": self._rid,
            "internalipaddress": self._ip_address,
            "swversion": self._swversion,
            "username": self._username,
            "hue-application-id": self._hue_app_id,
            "clientkey": self._client_key,
            "name": self._name,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates an instance of Bridge from a dictionary.

        Parameters:
            data (dict): A dictionary containing the attributes of a Bridge.

        Returns:
            Bridge: An instance of Bridge with attributes set according to the data dictionary.
        """
        return cls(
            identification=data.get("id"),
            rid=data.get("rid"),
            ip_address=data.get("internalipaddress"),
            username=data.get("username"),
            client_key=data.get("clientkey"),
            name=data.get("name"),
            swversion=data.get("swversion"),
            hue_app_id=data.get("hue-application-id"),
        )
