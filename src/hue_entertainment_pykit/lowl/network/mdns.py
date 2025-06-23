"""
The mdns_service module provides the MdnsServiceListener class, which implements multicast DNS (mDNS)
service listening functionality for discovering Philips Hue Bridge services in a local network. It captures
the IP addresses of advertised Hue Bridge services through mDNS broadcasts.
"""

import logging
from ipaddress import ip_address, IPv4Address
from typing import Callable, Sequence
from zeroconf import ServiceListener, Zeroconf


logger = logging.getLogger(__name__)

class Mdns(ServiceListener):
    """
    Stateless listener for mDNS (Multicast DNS) Hue Bridge discovery.
    """

    def __init__(self, on_service_discovered: Callable[[Sequence[IPv4Address]], None]):
        """
        Args:
            on_service_discovered (Callable[[Sequence[str]], None]):
                Function to call when service is discovered.
        """
        self._on_service_discovered = on_service_discovered

    @staticmethod
    def _extract_ipv4_addresses(zc: Zeroconf, type_: str, name: str) -> list[str]:
        info = zc.get_service_info(type_, name)
        if not info:
            return []
        addresses = []
        for addr in info.parsed_addresses():
            try:
                ip = ip_address(addr)
                if isinstance(ip, IPv4Address):
                    addresses.append(addr)
            except ValueError:
                continue
        return addresses

    def add_service(self, zc: Zeroconf, type_: str, name: str):
        addresses = self._extract_ipv4_addresses(zc, type_, name)
        if addresses:
            ip_v4_list = [IPv4Address(address) for address in addresses]
            logger.debug("Discovered service %s with IPv4s: %s", name, ", ".join(addresses))
            self._on_service_discovered(ip_v4_list)
        else:
            logger.error("Failed to resolve service %s or no IPv4 addresses found", name)

    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        logger.info("Service %s removed", name)

    def update_service(self, zc: Zeroconf, type_: str, name: str):
        addresses = self._extract_ipv4_addresses(zc, type_, name)
        if addresses:
            ip_v4_list = [IPv4Address(address) for address in addresses]
            logger.info("Service %s updated with IPv4s: %s", name, ", ".join(addresses))
            self._on_service_discovered(ip_v4_list)
        else:
            logger.info("Service %s updated but no IPv4 addresses found", name)
