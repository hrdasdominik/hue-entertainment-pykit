"""
The mdns_service module provides the MdnsServiceListener class, which implements multicast DNS (mDNS)
service listening functionality for discovering Philips Hue Bridge services in a local network. It captures
the IP addresses of advertised Hue Bridge services through mDNS broadcasts.
"""

import logging
from threading import Event

from zeroconf import ServiceListener, Zeroconf


class Mdns(ServiceListener):
    """
    Listens for mDNS (Multicast DNS) broadcasts to discover Philips Hue Bridge services in a local network.

    This class, leveraging Zeroconf, captures the IP addresses of services advertised over mDNS, specifically
    targeting Philips Hue Bridges. It provides mechanisms to handle service addition, removal, and updates,
    and maintains a list of discovered IP addresses.

    Attributes:
        _addresses (list[str]): Discovered IP addresses of Hue Bridge services.
        _service_discovered (Event): Event triggered when a new service is discovered.

    Methods:
        add_service: Handles new service additions.
        remove_service: Responds to service removal.
        update_service: Manages updates to existing services.
        get_addresses: Retrieves the list of discovered IP addresses.
    """

    def __init__(self):
        """
        Initializes the MdnsService with an empty list of addresses and a service discovery event.
        """

        self._addresses: list[str] = []
        self._service_discovered = Event()

    def get_service_discovered(self) -> Event:
        """
        Retrieves the event object that signals the discovery of a new service.

        This method returns an Event instance which is set when a new service (such as a Philips Hue Bridge)
        is discovered in the local network using mDNS. The event can be used to synchronize or trigger
        subsequent actions following the discovery of a service.

        Returns:
            Event: An event object that is set when a new mDNS service is discovered.
        """

        return self._service_discovered

    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        """
        Called when a service is removed.

        Parameters:
            zc (Zeroconf): The Zeroconf instance.
            type_ (str): The type of service.
            name (str): The name of the service.
        """

        logging.info("Service %s removed", name)

    def update_service(self, zc: Zeroconf, type_: str, name: str):
        """
        Responds to updates of an existing service.

        This method is called when an advertised service, such as a Philips Hue Bridge, undergoes changes that
        are broadcast over mDNS. It logs the update for tracking purposes.

        Parameters:
            zc (Zeroconf): The Zeroconf instance used for mDNS operations.
            type_ (str): The type of the service being updated.
            name (str): The name of the updated service.
        """

        logging.info("Service %s updated", name)

    def add_service(self, zc: Zeroconf, type_: str, name: str):
        """
        Called when a new service is added.

        Parameters:
            zc (Zeroconf): The Zeroconf instance.
            type_ (str): The type of service.
            name (str): The name of the service.
        """

        info = zc.get_service_info(type_, name)
        if info:
            self._addresses.extend(info.parsed_addresses())
            self._service_discovered.set()
            logging.info(
                "Service %s added, IP address: %s", name, ", ".join(self._addresses)
            )
        else:
            logging.error("Failed to get service info for %s", name)

    def get_addresses(self) -> list[str]:
        """
        Gets the list of IP addresses for the service.

        Returns:
            list[str]: A list of IP addresses.
        """

        return self._addresses
