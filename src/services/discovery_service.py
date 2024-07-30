"""
Contains the DiscoveryService class for locating Philips Hue bridges on the network. The DiscoveryService
class offers methods for discovering bridges through local network scanning (mDNS), Philips Hue's cloud
discovery API, and manual IP address input. It also includes functionality to filter bridges based on
streaming support and to load saved bridge data.
"""

import json
import logging
import re
from typing import Optional

import requests
from zeroconf import Zeroconf, ServiceBrowser

from bridge.bridge_repository import BridgeRepository
from exceptions.bridge_exception import BridgeException
from models.bridge import Bridge
from network.mdns import Mdns
from utils.file_handler import FileHandler
from utils.status_code import StatusCode


# pylint: disable=too-few-public-methods
class DiscoveryService:
    """
    Responsible for discovering Philips Hue bridges in a network, leveraging mDNS and cloud-based discovery methods.

    This service class uses mDNS and cloud services to find bridges, allows manual IP-based discovery, and
    filters bridges based on streaming feature support. It uses the BridgeRepository to store bridge data and
    the Mdns service for local network discovery.

    Attributes:
        _CLOUD_URL (str): Cloud service URL for discovering bridges.
        _MDNS_NAME (str): mDNS service name for discovering local network bridges.
        _MIN_SWVERSION (int): Minimum software version for streaming feature support.

    Methods:
        discover: Discover bridges using various methods.
        _discover_via_mdns: Discover bridges using mDNS.
        _discover_via_cloud: Discover bridges using a cloud service.
        _discover_manually: Discover a bridge using a given IP address.
        _create_bridges_from_addresses: Create Bridge instances from IP addresses.
        _filter_supported_bridges: Filter bridges that support streaming.
        _does_support_streaming_data: Check if a bridge supports streaming.
        _load_bridge_data: Load saved bridge data from a file.
        _is_valid_ip: Validate an IP address format.
    """

    _CLOUD_URL = "https://discovery.meethue.com/"
    _MDNS_NAME = "_hue._tcp.local."
    _MIN_SWVERSION = 1948086000

    def __init__(self, mdns_service: Mdns, bridge_repository: BridgeRepository):
        """
        Initializes the DiscoveryService with the required mDNS service and bridge repository.

        Parameters:
            mdns_service (Mdns): An instance of the mDNS service for local network discovery.
            bridge_repository (BridgeRepository): A repository for fetching and storing bridge data.
        """

        self._mdns_service = mdns_service
        self._bridge_repository = bridge_repository

    def discover(self, ip_address: Optional[str] = None) -> dict[str, Bridge] | list:
        """
        Discover bridges using a combination of saved data, mDNS, cloud, and manual IP input methods.

        Parameters:
            ip_address (Optional[str]): Optional IP address for manual discovery.
            If provided, adds manual discovery to the list of methods.

        Returns:
            list[Bridge]: A list of discovered Bridge instances.

        Raises:
            BridgeException: If no suitable bridges are found.
        """

        methods = [
            self._load_bridge_data,
            self._discover_via_mdns,
            self._discover_via_cloud,
        ]
        if ip_address:
            methods.insert(0, lambda: self._discover_manually(ip_address))

        supported_bridges = {}
        for method in methods:
            try:
                bridges = self._filter_supported_bridges(method())
                if bridges:
                    for bridge in bridges:
                        supported_bridges[bridge.get_name()] = bridge
                    return supported_bridges
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(e)
            except BridgeException as e:
                logging.error(e)
            except FileNotFoundError as e:
                logging.warning(e)

        logging.error("No suitable bridges found")
        return {}

    def _discover_via_mdns(self) -> list[Bridge]:
        """
        Discover bridges using mDNS/cloud/manual IP address.

        Returns:
            list[Bridge]: Discovered Bridge instances or an empty list if none found.
        """

        logging.info("Discovering bridge/s via mDNS")
        with Zeroconf() as zconf:
            ServiceBrowser(zconf, self._MDNS_NAME, self._mdns_service)
            has_found_addresses = self._mdns_service.get_service_discovered().wait(timeout=10)
            if not has_found_addresses:
                raise ValueError("No Hue bridges found via mDNS.")

        ip_and_mac_addresses = self._mdns_service.get_addresses()

        ip_addresses = []
        for address in ip_and_mac_addresses:
            if self._is_valid_ip(address):
                ip_addresses.append(address)

        logging.info("Discovered IPs: %s", ip_addresses)
        return self._create_bridges_from_addresses(ip_addresses)

    def _discover_via_cloud(self) -> list[Bridge]:
        """
        Discover bridges using Philips Hue's cloud discovery service.

        Returns:
            list[Bridge]: A list of discovered Bridge instances via cloud service.

        Raises:
            BridgeException: If the response from the cloud service is not successful.
        """

        logging.info("Discovering bridge/s via Hue Cloud")
        response = requests.get(self._CLOUD_URL, timeout=5)
        if response.status_code != StatusCode.OK.value:
            raise BridgeException(f"Response status: {response.status_code}, {response.reason}")

        addresses = [config["internalipaddress"] for config in response.json()]
        logging.debug("addresses: %s", addresses)
        return self._create_bridges_from_addresses(addresses)

    def _discover_manually(self, ip_address: str) -> list[Bridge]:
        """
        Discover a bridge manually using a specified IP address.

        Parameters:
            ip_address (str): The IP address of the bridge to be discovered.

        Returns:
            list[Bridge]: A list containing the manually discovered Bridge instance, or an empty list if none found.
        """

        logging.info("Discovering bridge via manual input of IP %s", ip_address)
        return self._create_bridges_from_addresses([ip_address])

    def _create_bridges_from_addresses(self, addresses: list[str]) -> list[Bridge]:
        """
        Create Bridge instances from a list of IP addresses.

        Parameters:
            addresses (list[str]): A list of IP addresses to create Bridge instances from.

        Returns:
            list[Bridge]: A list of Bridge instances created from the given IP addresses.
        """

        bridges = []
        for address in addresses:
            bridge_data = self._bridge_repository.fetch_bridge_data(address)
            bridge = Bridge.from_dict(bridge_data)
            if bridge:
                FileHandler.write_json(FileHandler.BRIDGE_FILE_PATH, bridge.to_dict())
                bridges.append(bridge)
        return bridges

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

        return bridge.get_swversion() >= self._MIN_SWVERSION

    @classmethod
    def _load_bridge_data(cls) -> list[Bridge]:
        """
        Loads saved bridge data from a file and returns it as a list of Bridge instances.

        This method reads a JSON file specified by FileHandler.BRIDGE_DATA_FILE. It is now adapted to handle
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
