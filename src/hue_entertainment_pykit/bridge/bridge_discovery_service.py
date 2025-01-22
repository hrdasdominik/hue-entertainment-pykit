import json
import logging
import re

import requests
from zeroconf import Zeroconf, ServiceBrowser

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.exception.bridge_exception import BridgeException
from src.hue_entertainment_pykit.http.http_client import HttpClient
from src.hue_entertainment_pykit.http.http_method_enum import HttpMethodEnum
from src.hue_entertainment_pykit.http.http_status_code_enum import HttpStatusCodeEnum
from src.hue_entertainment_pykit.network.mdns import Mdns
from src.hue_entertainment_pykit.utils.endpoint_enum import EndpointEnum
from src.hue_entertainment_pykit.utils.file_handler import FileHandler
from src.hue_entertainment_pykit.utils.json_storage_manager import JsonStorageManager


# pylint: disable=too-few-public-methods
class BridgeDiscoveryService:

    def __init__(self, app_name: str):
        if not self._is_valid_format(app_name):
            raise Exception(f"App name ({app_name}) not valid pattern. <string>#<string>")
        self._app_name = app_name
        self._mdns_service = Mdns()
        self._http_client = HttpClient()
        self._cloud_url = "https://discovery.meethue.com/"
        self._mdns_name = "_hue._tcp.local."
        self._min_swversion = 1948086000

    def fetch_bridge_dict(self) -> dict[str, Bridge]:
        ip_address_list: list[str] = self._discover()

        bridge_dict: dict[str, Bridge] = {}
        for address in ip_address_list:
            bridge: Bridge = self._fetch_bridge(address)

            if self._does_support_streaming_data(bridge):
                FileHandler.write_json(FileHandler.BRIDGE_FILE_PATH, bridge.to_dict())
                bridge_dict[bridge.get_name()] = bridge

        return bridge_dict

    def _discover(self) -> list[str]:
        methods = [
            self._discover_via_mdns,
            self._discover_via_cloud,
        ]

        for method in methods:
            try:
                return method()
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(e)
            except BridgeException as e:
                logging.error(e)

        logging.error("No suitable bridges found")
        raise BridgeException("No suitable bridges found")

    def _fetch_bridge(self, address: str) -> Bridge:
        """
        Fetches a comprehensive set of data about the Philips Hue Bridge.

        This http_method aggregates various details about the bridge including identification, RID,
        IP address, software version, username, Hue application ID, client key, and name.

        Parameters:
            address (str): An IP addresses for the Bridge.

        Returns:
            dict: A dictionary containing detailed information about the Bridge.

        Raises:
            ValueError: If no IP address is provided or if the username is empty.
        """

        logging.info(f"Fetching bridge data from address {address}")
        if not address:
            raise ValueError("No IP address provided for bridge data fetching.")

        self._http_client.set_base_url(address)

        # TODO: Implement retry for link button not pressed case
        username, client_key = self._register_app_and_fetch_username_client_key()

        if username == "":
            logging.error("No username provided for bridge data fetching.")
            raise ValueError("Username is empty.")

        if not self._http_client.get_headers().get("hue-application-key"):
            self._http_client.add_headers("hue-application-key", username)

        identification, rid = self._fetch_bridge_id_and_rid()
        name = self._fetch_bridge_name(rid)
        swversion = self._fetch_swversion()
        hue_application_id = self._fetch_hue_application_id()

        bridge = Bridge(
            identification,
            rid,
            address,
            swversion,
            username,
            hue_application_id,
            client_key,
            name
        )

        FileHandler.write_json(FileHandler.BRIDGE_FILE_PATH, bridge.to_dict())

        logging.info("Successfully fetched bridge data.")
        return bridge

    def _register_app_and_fetch_username_client_key(self) -> tuple[str, str]:
        """
        Registers the application with the Hue Bridge and retrieves the username and client key.

        Attempts to load existing authentication data first. If not available, it registers the application
        with the bridge and fetches new credentials.

        Returns:
            tuple[str, str]: A tuple containing the username and client key. If registration fails,
            both values will be empty strings.
        """

        logging.info("Registering app and fetching username & client key")

        try:
            auth_data = JsonStorageManager.load_auth_data()
            if auth_data:
                return auth_data["username"], auth_data["clientkey"]
        except FileNotFoundError as e:
            logging.info("No existing username data at: %s", e)

        response = self._http_client.make_request(
            HttpMethodEnum.POST, EndpointEnum.API, json={"devicetype": self._app_name, "generateclientkey": True}
        )
        data = response.json()[0]

        if "error" in data:
            raise BridgeException(f"Bridge error: {data['error']['description']}")
        username, client_key = data["success"]["username"], data["success"]["clientkey"]
        JsonStorageManager.save_auth_data({"username": username, "clientkey": client_key})
        return username, client_key

    def _fetch_bridge_id_and_rid(self) -> tuple[str, str]:
        """
        Fetches the Bridge ID and resource identifier (RID).

        Returns:
            tuple[str, str]: A tuple containing the Bridge ID and RID.
        """

        logging.info("Fetching Bridge ID and RID")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_BRIDGE)
        data = response.json()["data"][0]
        identification = data["id"]
        rid = data["owner"]["rid"]
        logging.info(f"Bridge ID: {identification} RID: {rid}")
        return identification, rid

    def _fetch_bridge_name(self, rid: str) -> str:
        """
        Fetches the name of the Philips Hue Bridge.

        Parameters:
            rid (str): The resource identifier of the Bridge.

        Returns:
            str: The name of the Bridge.
        """

        logging.info("Fetching Bridge Name")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_DEVICE, rid=rid)
        bridge_name = response.json()["data"][0]["metadata"]["name"]
        logging.info("Bridge Name: %s", bridge_name)
        return bridge_name

    def _fetch_swversion(self) -> int:
        """
        Fetches the software version of the Philips Hue Bridge.

        Returns:
            int: The software version of the Bridge.
        """

        logging.info("Fetching Bridge software version")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.API_CONFIG)
        swversion = int(response.json()["swversion"])
        logging.info("Bridge software version %s", swversion)
        return swversion

    def _fetch_hue_application_id(self) -> str:
        """
        Fetches the Hue Application ID from the Bridge.

        Returns:
            str: The Hue Application ID.
        """

        logging.info("Fetching Hue Application ID")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.AUTH_V1)
        hue_application_id = response.headers.get("hue-application-id")
        logging.info(f"Hue Application ID {hue_application_id}")
        return hue_application_id

    def _discover_via_mdns(self) -> list[str]:
        """
        Discover bridges using mDNS/cloud/manual IP address.

        Returns:
            list[Bridge]: Discovered Bridge instances or an empty list if none found.
        """

        logging.info("Discovering bridge/s via mDNS")
        with Zeroconf() as zconf:
            ServiceBrowser(zconf, self._mdns_name, self._mdns_service)
            has_found_addresses = self._mdns_service.get_service_discovered().wait(timeout=10)
            if not has_found_addresses:
                raise ValueError("No Hue bridges found via mDNS.")

        ip_and_mac_addresses = self._mdns_service.get_addresses()

        ip_addresses = []
        for address in ip_and_mac_addresses:
            if self._is_valid_ip(address):
                ip_addresses.append(address)

        logging.debug("Discovered IPs: %s", ip_addresses)
        return ip_addresses

    def _discover_via_cloud(self) -> list[str]:
        """
        Discover bridges using Philips Hue's cloud discovery service.

        Returns:
            list[Bridge]: A list of discovered Bridge instances via cloud service.

        Raises:
            BridgeException: If the response from the cloud service is not successful.
        """

        logging.info("Discovering bridge/s via Hue Cloud")
        response = requests.get(self._cloud_url, timeout=5)
        if response.status_code != HttpStatusCodeEnum.OK.value:
            raise BridgeException(f"Response status: {response.status_code}, {response.reason}")

        addresses = [config["internalipaddress"] for config in response.json()]
        logging.debug("addresses: %s", addresses)
        return addresses

    def _filter_supported_bridges(self, bridges: list[Bridge]) -> list[Bridge]:
        """
        Filters the given list of bridges to only include those that support streaming.

        Parameters:
            bridges (list[Bridge]): A list of Bridge instances.

        Returns:
            list[Bridge]: A filtered list of Bridge instances supporting streaming.
        """

        return [bridge for bridge in bridges if self._does_support_streaming_data(bridge)]

    def _does_support_streaming_data(self, bridge: Bridge) -> bool:
        """
        Checks if a given bridge supports streaming based on its software version.

        Parameters:
            bridge (Bridge): An instance of the Bridge class.

        Returns:
            bool: True if the bridge supports streaming, False otherwise.
        """

        return bridge.get_swversion() >= self._min_swversion

    @classmethod
    def _load_bridge_data(cls) -> list[Bridge]:
        """
        Loads saved bridge data from a file and returns it as a list of Bridge instances.

        This http_method reads a JSON file specified by FileHandler.BRIDGE_DATA_FILE. It is now adapted to handle
        multiple Bridge instances stored in the file. Each entry in the JSON file should represent a single
        Bridge's data.

        Returns:
            list[Bridge]: A list of Bridge instances created from the saved data. If the file is not found,
            or if the data is invalid, an empty list is returned.

        Raises:
            FileNotFoundError: If the specified file is not found.
            json.JSONDecodeError: If there is an error in decoding the JSON data.
        """

        logging.info("Attempting to load bridge data from a file")
        try:
            data = FileHandler.read_json(FileHandler.BRIDGE_FILE_PATH)
            if isinstance(data, list):
                logging.debug("data read: %s", data)
                return [Bridge.from_dict(bridge_data) for bridge_data in data]
            if isinstance(data, dict):
                logging.debug("data read: %s", data)
                return [Bridge.from_dict(data)]
            raise ValueError("Invalid data format in bridge data file")
        except FileNotFoundError as e:
            raise FileNotFoundError("No existing saved bridge data") from e

    @classmethod
    def _is_valid_ip(cls, ip_address):
        """
        Validates the format of an IP address using a regular expression.

        Parameters:
            ip_address (str): The IP address to be validated.

        Returns:
            bool: True if the IP address is in a valid format, False otherwise.
        """
        pattern = (
            r"^(?!0\d)(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(?!0\d)(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(?!0\d)(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(?!0\d)(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        return re.match(pattern, ip_address) is not None

    @staticmethod
    def _is_valid_format(s: str) -> bool:
        pattern = r'^[^#]+#[^#]+$'
        return bool(re.match(pattern, s))
