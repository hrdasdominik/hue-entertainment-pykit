"""
This module contains the EntertainmentConfigurationRepository class for managing Philips Hue Entertainment
configurations. It facilitates interactions with the Hue API, abstracting complexities of API communication.
The class provides a streamlined interface for operations related to entertainment configurations on the
Philips Hue Bridge.

The repository facilitates communication with the Hue Bridge by constructing and sending HTTP requests,
handling responses, and converting data into appropriate Python objects. It abstracts the complexities
of direct API communication, providing a simple interface for operations related to entertainment
configurations.

Classes:
- EntertainmentConfigurationRepository: A repository class for managing Philips Hue Entertainment
  configurations, offering methods to fetch and update these configurations through HTTP requests
  to the Philips Hue API.
"""

import logging

import requests
from requests import Response

from models.bridge import Bridge
from models.payload import Payload
from models.entertainment_configuration import EntertainmentConfiguration
from exceptions.api_exception import ApiException

from utils.status_code import StatusCode


class EntertainmentConfigurationRepository:
    """
    Manages Philips Hue Entertainment configurations through the Hue API.

    This class interfaces with the Philips Hue Bridge to fetch and update entertainment configurations. It
    handles HTTP request construction, response processing, and converts data to Python objects.

    Attributes:
        _bridge (Bridge): Instance of Bridge class for Philips Hue Bridge communication.
        _base_url (str): Base URL for entertainment configuration API requests.
        _headers (dict[str, str]): HTTP request headers with content type and application key from the Bridge.

    Methods:
        fetch_configurations: Fetches all entertainment configurations from the Hue Bridge.
        put_configuration: Updates an existing entertainment configuration on the Hue Bridge.
    """

    def __init__(self, bridge: Bridge):
        """
        Initializes the EntertainmentConfigurationRepository with a Philips Hue Bridge.

        Parameters:
            bridge (Bridge): An instance of the Bridge class representing the Philips Hue Bridge.
        """

        self._bridge: Bridge = bridge
        self._base_url: str = f"https://{bridge.get_ip_address()}/clip/v2/resource/entertainment_configuration"

        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "hue-application-key": bridge.get_username(),
        }

    def _send_request(self, method: str, url: str, payload: Payload = None) -> Response:
        """
        Sends an HTTP request to the Philips Hue API.

        Parameters:
            method (str): HTTP method ('GET', 'PUT', etc.).
            url (str): Target URL for the request.
            payload (Payload, optional): Payload for the request, if applicable.

        Returns:
            Response: Response object from the Hue Bridge.

        Raises:
            ApiException: If the response status code indicates an error.
        """

        logging.info("Sending %s request to %s", method, url)
        if payload:
            logging.debug("Payload: %s", payload.get_data())
        response = requests.request(
            method,
            url,
            headers=self._headers,
            json=payload.get_data() if payload else None,
            verify=False,
            timeout=5,
        )
        if response.status_code != StatusCode.OK.value:
            raise ApiException(
                f"Response status: {response.status_code}, {response.reason}"
            )
        return response

    def fetch_configurations(self) -> dict[str, EntertainmentConfiguration]:
        """
        Fetches all entertainment configurations from the Philips Hue Bridge.

        Returns:
            dict[str, EntertainmentConfiguration]: A dictionary of EntertainmentConfiguration instances representing
            each configuration fetched from the Hue Bridge.
        """

        logging.info("Fetching entertainment configurations")
        response = self._send_request("GET", self._base_url)
        data = response.json()["data"]
        entertainment_configs = {}
        for item in data:
            entertainment_configs[item["id"]] = EntertainmentConfiguration(item)
        return entertainment_configs

    def put_configuration(self, payload: Payload):
        """
        Updates an existing entertainment configuration on the Philips Hue Bridge.

        Parameters:
            payload (Payload): The payload containing the updated entertainment configuration data.
        """

        url = f"{self._base_url}/{payload.get_id()}"
        payload.remove_key("id")
        self._send_request("PUT", url, payload)
        logging.info("Entertainment configuration updated successfully.")
