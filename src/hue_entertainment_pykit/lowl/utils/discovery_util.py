"""
Contains the DiscoveryService class for locating Philips Hue bridges on the network. The DiscoveryService
class offers methods for discovering bridges through local network scanning (mDNS), Philips Hue's cloud
discovery API, and manual IP address input. It also includes functionality to filter bridges based on
streaming support and to load saved clients data.
"""

import logging
from ipaddress import IPv4Address, ip_address
from threading import Event
from typing import Sequence, Optional

import requests
from zeroconf import Zeroconf, ServiceBrowser

from hue_entertainment_pykit.lowl.enums.status_code_enum import StatusCodeEnum
from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import BridgeDiscoveryError, BridgeApiError, \
    LoadingDataError
from hue_entertainment_pykit.lowl.models.bridge.bridge_combination_hue import BridgeCombinationHue
from hue_entertainment_pykit.lowl.network.mdns import Mdns
from hue_entertainment_pykit.lowl.utils.bridge_builder_util import BridgeBuilderUtil


logger = logging.getLogger(__name__)

class DiscoveryUtil:
    """
    Responsible for discovering Philips Hue bridges in a network, leveraging mDNS and cloud-based discovery methods.

    This service class uses mDNS and cloud services to find bridges, allows manual IP-based discovery, and
    filters bridges based on streaming feature support. It uses the BridgeRepository to store clients data and
    the Mdns service for local network discovery.

    Attributes:
        __CLOUD_URL (str): Cloud service URL for discovering bridges.
        __MDNS_NAME (str): mDNS service name for discovering local network bridges.

    Methods:
        discover: Discover bridges using various methods.
        __discover_via_mdns: Discover bridges using mDNS.
        __discover_via_cloud: Discover bridges using a cloud service.
        __discover_manually: Discover a clients using a given IP address.
        __filter_supported_bridges: Filter bridges that support streaming.
        __does_support_streaming_data: Check if a clients supports streaming.
        __load_bridge_data: Load saved clients data from a file.
    """

    __CLOUD_URL = "https://discovery.meethue.com/"
    __MDNS_NAME = "_hue._tcp.local."

    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def get_cloud_url() -> str:
        return DiscoveryUtil.__CLOUD_URL

    @staticmethod
    def get_mdns_name() -> str:
        return DiscoveryUtil.__MDNS_NAME

    @staticmethod
    def discover(application_name: str,
                 ip_addresses: Sequence[IPv4Address] | None,
                 preload_auth: bool = False) -> list[BridgeCombinationHue]:
        """
        Discover bridges using a combination of saved data, mDNS, cloud, and manual IP input methods.

        Parameters:
            If provided, adds manual discovery to the list of methods.
            application_name (Optional[str]): Optional application name to use.
            ip_addresses (Optional[list[IPv4Address]]): Optional IP addresses to use.
            preload_auth (Optional[bool]): Optional preload auth data.

        Returns:
            list[BridgeHue]: A list of discovered Bridge instances.
            Key: string clients name
            Value: Bridge instance

        Raises:
            BridgeDiscoveryError: If no suitable bridges are found.
        """

        if not ip_addresses:
            ip_addresses: list[IPv4Address] = DiscoveryUtil.discover_ip_addresses()

        bridge_list: list[BridgeCombinationHue] = []
        for address in ip_addresses:
            if preload_auth:
                try:
                    bridge: BridgeCombinationHue = BridgeBuilderUtil.build_without_app_registration(address)
                    if bridge.does_support_streaming:
                        bridge_list.append(bridge)
                    continue
                except LoadingDataError as e:
                    logger.error("Failed to load bridge data from file: %s", e)
                except BridgeApiError as e:
                    logger.error("Failed to fetch data from bridge API: %s", e)
            else:
                try:
                    bridge: BridgeCombinationHue = BridgeBuilderUtil.build_with_app_registration(address,
                                                                                                 application_name)
                    if bridge.does_support_streaming:
                        bridge_list.append(bridge)
                except BridgeDiscoveryError as e:
                    logger.error("Bridge build with app name registration failed: %s", e)
                    pass

        if bridge_list:
            logger.info("Bridge discovery results: %s", bridge_list)
            return bridge_list

        raise BridgeDiscoveryError('No bridges discovered in network.')

    @staticmethod
    def discover_ip_addresses() -> list[IPv4Address]:
        methods = [
            DiscoveryUtil.discover_ip_addresses_via_mdns,
            DiscoveryUtil.discover_ip_addresses_via_cloud,
        ]

        for method in methods:
            try:
                return method()
            except Exception as e:
                logger.warning(e)

        raise BridgeDiscoveryError('No bridges found in network')

    @staticmethod
    def discover_ip_addresses_via_mdns() -> list[IPv4Address]:
        """
        Discover bridges using mDNS/cloud/manual IP address.

        Returns:
            list[BridgeHue]: Discovered Bridge instances or an empty list if none found.
        """

        logger.info("Discovering clients/s via mDNS")

        found_addresses: list[IPv4Address] = []
        discovery_event = Event()

        def __on_service_discovered(addresses: Sequence[IPv4Address]) -> None:
            found_addresses.extend(addresses)
            discovery_event.set()

        with Zeroconf() as z_conf:
            ServiceBrowser(z_conf, DiscoveryUtil.__MDNS_NAME, Mdns(__on_service_discovered))
            discovery_event.wait(timeout=10)

        if not found_addresses:
            raise BridgeDiscoveryError("No Hue bridges found via mDNS.")

        ip_addresses = [
            ip_address(addr) for addr in found_addresses
            if isinstance(ip_address(addr), IPv4Address)
        ]

        logger.info("Discovered IPs via mDNS: %s", ip_addresses)
        return ip_addresses

    @staticmethod
    def discover_ip_addresses_via_cloud() -> list[IPv4Address]:
        """
        Discover bridges using Philips Hue's cloud discovery service.

        Returns:
            list[BridgeHue]: A list of discovered Bridge instances via cloud service.

        Raises:
            BridgeDiscoveryError: If the response from the cloud service is not successful.
        """

        logger.info("Discovering clients/s via Hue Cloud")
        response = requests.get(DiscoveryUtil.__CLOUD_URL, timeout=10)
        if response.status_code != StatusCodeEnum.OK.value:
            raise BridgeDiscoveryError(f"Cloud response status: {response.status_code}, reason: {response.reason}")

        addresses = [config["internalipaddress"] for config in response.json()]
        logger.info("Discovered IPs via cloud: %s", addresses)
        return addresses
