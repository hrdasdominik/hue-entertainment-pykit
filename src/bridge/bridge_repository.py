"""
The bridge_repository module offers a centralized solution for managing interactions with the Philips Hue Bridge.
It includes BridgeRepository, a class that encapsulates methods for fetching and updating bridge
information, handling authentication, and managing application access. It utilizes a singleton
pattern to ensure a single, consistent repository instance within the application context.
"""

import logging
from typing import Any

import requests
from requests import Response

from exceptions.bridge_exception import BridgeException
from utils.file_handler import FileHandler
from utils.status_code import StatusCode


# pylint: disable=too-few-public-methods
class BridgeRepository:
    """
    A repository class for managing Philips Hue Bridge interactions.

    This class handles the communication with the Philips Hue Bridge. It provides methods to fetch and update
    information related to the bridge, such as software version, Hue application ID, bridge name, and more.
    It also facilitates the registration of the application to obtain a username and client key for authentication.

    Attributes:
        _headers (dict[str, str]): Headers to be used for HTTP requests.
        _base_url (str): The base URL for the Philips Hue Bridge API requests.

    Methods:
        _set_base_url: Sets the base URL for API requests.
        _make_request: Sends HTTP requests to the Bridge and handles responses.
        _register_app_and_fetch_username_client_key: Registers the app and retrieves authentication details.
        _fetch_swversion: Fetches the software version of the Bridge.
        _fetch_hue_application_id: Retrieves the Hue Application ID from the Bridge.
        _fetch_bridge_name: Obtains the name of the Philips Hue Bridge.
        _fetch_bridge_id_and_rid: Retrieves the Bridge ID and resource identifier.
        _fetch_bridge_rid: Gets the resource identifier of the Bridge.
        fetch_bridge_data: Fetches various information about the Bridge.
    """

    def __init__(self):
        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "hue-application-key": "",
        }
        self._base_url: str = ""

    def get_headers(self) -> dict[str, str]:
        """
        Retrieves the headers used for HTTP requests to the Philips Hue Bridge.

        Returns:
            dict[str, str]: A dictionary containing the headers for HTTP requests.
        """

        return self._headers

    def set_headers(self, headers: dict[str, str]):
        """
        Sets the headers for HTTP requests to the Philips Hue Bridge.

        Parameters:
            headers (dict[str, str]): A dictionary containing the headers to be set for HTTP requests.
        """

        self._headers = headers

    def get_base_url(self) -> str:
        """
        Retrieves the base URL used for API requests to the Philips Hue Bridge.

        Returns:
            str: The base URL for the Philips Hue Bridge API requests.
        """

        return self._base_url

    def set_base_url(self, ip_address: str):
        """
        Sets the base URL for API requests to the Philips Hue Bridge.

        Parameters:
            ip_address (str): The IP address of the Philips Hue Bridge.
        """

        self._base_url = f"https://{ip_address}"

    def _load_auth_data(self) -> dict[str, Any]:
        """
        Loads authentication data from a predefined file path.

        This method reads a JSON file containing authentication information necessary for interacting
        with the Philips Hue Bridge. The authentication data typically includes credentials like username
        and client key.

        Returns:
            dict: A dictionary containing authentication data such as username and client key. The dictionary
            will be empty if the file does not exist or is empty.

        Note:
            The file path is obtained from the FileHandler.AUTH_FILE_PATH constant.
        """

        return FileHandler.read_json(FileHandler.AUTH_FILE_PATH)

    def _save_auth_data(self, data: dict):
        """
        Saves authentication data to a predefined file path.

        This method writes the provided authentication data, such as username and client key, to a JSON file.
        This data is essential for subsequent interactions with the Philips Hue Bridge.

        Parameters:
            data (dict): A dictionary containing authentication information like username and client key to be saved.

        Note:
            The file path is obtained from the FileHandler.AUTH_FILE_PATH constant. If the file does not exist,
            it will be created.
        """
        logging.debug("saving data: %s", data)
        FileHandler.write_json(FileHandler.AUTH_FILE_PATH, data)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Response:
        """
        Makes an HTTP request to the Philips Hue Bridge.

        Parameters:
            method (str): The HTTP method to use for the request.
            endpoint (str): The API endpoint to target.
            **kwargs: Additional keyword arguments passed to the requests.request method,
            such as payload data or custom headers.

        Returns:
            Response: The response object from the Hue Bridge.

        Raises:
            ValueError: If the base URL is not set.
            BridgeException: If the response status code indicates an error.
        """

        if self._base_url == "https://":
            raise ValueError("Base url is not set.")
        url = f"{self._base_url}{endpoint}"
        logging.debug("headers: %s", self._headers)
        response = requests.request(
            method, url, headers=self._headers, verify=False, timeout=5, **kwargs
        )
        if response.status_code != StatusCode.OK.value:
            raise BridgeException(
                f"Response status: {response.status_code}, {response.reason}"
            )

        logging.debug("response-headers: %s", response.headers)
        logging.debug("response-body: %s", response.json())
        return response

    def _register_app_and_fetch_username_client_key(self) -> tuple[str, str]:
        """
        Registers the application with the Hue Bridge and retrieves the username and client key.

        Attempts to load existing authentication data first. If not available, it registers the application
        with the bridge and fetches new credentials.

        Returns:
            tuple[str, str]: A tuple containing the username and client key. If registration fails,
            both values will be empty strings.
        """

        logging.info("Registering app and fetching username/client key")

        try:
            auth_data = self._load_auth_data()
            if auth_data:
                return auth_data["username"], auth_data["clientkey"]
        except FileNotFoundError as e:
            logging.warning("No existing username data at: %s", e)

        response = self._make_request(
            "POST", "/api", json={"devicetype": "hep#1", "generateclientkey": True}
        )
        data = response.json()[0]

        if not data:
            raise BridgeException("Did not return any username or client key.")

        if "error" in data:
            raise BridgeException(f"Bridge error: {data['error']['description']}")
        username, client_key = data["success"]["username"], data["success"]["clientkey"]
        self._save_auth_data({"username": username, "clientkey": client_key})
        return username, client_key

    def _fetch_swversion(self) -> int:
        """
        Fetches the software version of the Philips Hue Bridge.

        Returns:
            int: The software version of the Bridge.
        """

        logging.info("Fetching Bridge software version")
        response = self._make_request("GET", "/api/config")
        return int(response.json()["swversion"])

    def _fetch_hue_application_id(self) -> str:
        """
        Fetches the Hue Application ID from the Bridge.

        Returns:
            str: The Hue Application ID.
        """

        logging.info("Fetching Hue Application ID")
        response = self._make_request("GET", "/auth/v1")
        return response.headers["hue-application-id"]

    def _fetch_bridge_name(self, rid: str) -> str:
        """
        Fetches the name of the Philips Hue Bridge.

        Parameters:
            rid (str): The resource identifier of the Bridge.

        Returns:
            str: The name of the Bridge.
        """

        logging.info("Fetching Bridge Name")
        response = self._make_request("GET", f"/clip/v2/resource/device/{rid}")
        return response.json()["data"][0]["metadata"]["name"]

    def _fetch_bridge_id_and_rid(self) -> tuple[str, str]:
        """
        Fetches the Bridge ID and resource identifier (RID).

        Returns:
            tuple[str, str]: A tuple containing the Bridge ID and RID.
        """

        logging.info("Fetching Bridge ID and RID")
        response = self._make_request("GET", "/clip/v2/resource/bridge")
        data = response.json()["data"][0]
        return data["id"], data["owner"]["rid"]

    def _fetch_bridge_rid(self) -> str:
        """
        Fetches the resource identifier (RID) of the Philips Hue Bridge.

        Returns:
            str: The RID of the Bridge.
        """

        logging.info("Fetching Bridge RID")
        response = self._make_request("GET", "/clip/v2/resource/bridge")
        return response.json()["data"][0]["owner"]["rid"]

    def fetch_bridge_data(self, address: str) -> dict:
        """
        Fetches a comprehensive set of data about the Philips Hue Bridge.

        This method aggregates various details about the bridge including identification, RID,
        IP address, software version, username, Hue application ID, client key, and name.

        Parameters:
            address (str): An IP addresses for the Bridge.

        Returns:
            dict: A dictionary containing detailed information about the Bridge.

        Raises:
            ValueError: If no IP address is provided or if the username is empty.
        """

        logging.info("Fetching bridge data")
        if not address:
            raise ValueError("No IP address provided for bridge data fetching.")

        self.set_base_url(address)

        username, client_key = self._register_app_and_fetch_username_client_key()
        if username == "":
            raise ValueError("Username is empty.")

        logging.info("username: %s, clientkey: %s", username, client_key)
        if not self._headers["hue-application-key"]:
            self._headers["hue-application-key"] = username

        identification, rid = self._fetch_bridge_id_and_rid()
        logging.info("id: %s, rid: %s", identification, rid)

        name = self._fetch_bridge_name(rid)
        logging.info("name: %s", name)
        swversion = self._fetch_swversion()
        logging.info("swversion: %s", swversion)
        hue_application_id = self._fetch_hue_application_id()
        logging.info("hue-application-id: %s", hue_application_id)

        data = {
            "id": identification,
            "rid": rid,
            "internalipaddress": address,
            "swversion": swversion,
            "username": username,
            "hue-application-id": hue_application_id,
            "clientkey": client_key,
            "name": name,
        }
        return data
