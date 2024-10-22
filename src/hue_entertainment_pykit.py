"""
This module provides classes for discovering and managing bridge devices and their entertainment configurations
in a network, as well as facilitating streaming operations. It includes the following key components:

1. `Discovery`: Handles the discovery of bridge devices using Multicast DNS (MDNS) and a bridge repository.
2. `EntertainmentService`: Manages entertainment configurations for a given bridge, including
fetching and updating configurations.
3. `Streaming`: Facilitates streaming operations for an entertainment configuration, including starting and
stopping streams, setting color spaces, and managing input data.

The module uses several dependencies, including services for MDNS, DTLS (Datagram Transport Layer Security), and
general bridge device management. It is designed to be used in systems where bridge devices and
their entertainment features need to be dynamically discovered, configured, and controlled.
"""
import logging
import re
from typing import Optional, Union

from bridge.bridge_repository import BridgeRepository
from bridge.entertainment_configuration_repository import (
    EntertainmentConfigurationRepository,
)
from models.bridge import Bridge
from models.entertainment_configuration import (
    EntertainmentConfiguration,
)
from network.dtls import Dtls
from network.mdns import Mdns
from services.discovery_service import DiscoveryService
from services.streaming_service import StreamingService
from utils.logger import setup_logging


def setup_logs(
        level: int = logging.DEBUG,
        max_file_size: int = 1024 * 1024 * 5,
        backup_count: int = 3,
):
    """
    User-friendly interface to configure the library's logging system with default settings.

    This wrapper function provides an easy way to set up logging with commonly used defaults. It initializes a rotating
    log file mechanism with default parameters, but allows for customization of the logging level,
    maximum log file size, and the number of backup files to keep.

    The default log level is DEBUG. The log file, named 'philipsLightsLogs.log', is created in a 'logs' directory
    within the current working directory. The default maximum log file size is set to 5 MB, with 3 backup files
    retained.

    Args:
        level (int, optional): Logging level to set. Defaults to logging.DEBUG.
        max_file_size (int, optional): Maximum size of the log file in bytes before rotation. Defaults to 5 MB
        (5 * 1024 * 1024 bytes).
        backup_count (int, optional): Number of backup log files to retain. Defaults to 3.
    """

    setup_logging(level, max_file_size, backup_count)


# pylint: disable=too-many-positional-arguments
def create_bridge(
        identification: str,
        rid: str,
        ip_address: str,
        swversion: int,
        username: str,
        hue_app_id: str,
        clientkey: str,
        name: str,
) -> Bridge:
    """
    Creates a new Bridge object with the specified configuration.
    This method initializes a Bridge instance with the provided parameters.

    Args:
        identification (str): Unique identifier of the Bridge.
        rid (str): Resource identifier of the Bridge.
        ip_address (str): IP address of the Bridge.
        swversion (int): Software version of the Bridge.
        username (str): Username used for authentication with the Bridge.
        hue_app_id (str): Hue application ID.
        clientkey (str): Client key for secure communication with the Bridge.
        name (str): Human-readable name of the Bridge.

    Returns:
        Bridge: An instance of the Bridge class configured with the given parameters.
    """

    if not isinstance(identification, str):
        raise TypeError("Identification must be a string")
    if not isinstance(rid, str):
        raise TypeError("Resource ID must be a string")
    if not isinstance(ip_address, str) or not re.match(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", ip_address
    ):
        raise ValueError("Invalid IP address format")
    if not isinstance(swversion, int):
        raise TypeError("Software version must be an integer")
    if not isinstance(username, str):
        raise TypeError("Username must be a string")
    if not isinstance(hue_app_id, str):
        raise TypeError("Hue application ID must be a string")
    if not isinstance(clientkey, str):  # Add specific format check if needed
        raise TypeError("Client key must be a string")
    if not isinstance(name, str):
        raise TypeError("Name must be a string")

    return Bridge(
        identification,
        rid,
        ip_address,
        swversion,
        username,
        hue_app_id,
        clientkey,
        name,
    )


# pylint: disable=too-few-public-methods
class Discovery:
    """Handles the discovery of bridge devices in a network using MDNS and a bridge repository.

    This class can discover bridge devices either broadly in the network or target a specific IP address.
    It utilizes MDNS (Multicast DNS) for the discovery process.

    Attributes:
        _mdns_service (Mdns): An instance of MdnsService for discovering devices using MDNS.
        _bridge_repository (BridgeRepository): Repository for storing and managing bridge devices.
        _discovery_service (DiscoveryService): Service for discovering bridge devices.
    """

    def __init__(self):
        """Initializes the Discovery class with necessary service instances."""

        self._mdns_service = Mdns()
        self._bridge_repository = BridgeRepository()
        self._discovery_service = DiscoveryService(
            self._mdns_service, self._bridge_repository
        )

    def discover_bridges(self, ip_address: Optional[str] = None) -> dict[str, Bridge]:
        """Discovers bridge devices in the network.

        If an IP address is provided, the discovery is limited to that address.

        Args:
            ip_address (Optional[str]): The IP address to limit the discovery to. Default is None.

        Returns:
            dict[str, Bridge]: A dictionary of discovered bridges, keyed by their IP addresses.
        """
        return self._discovery_service.discover(ip_address)


class Entertainment:
    """Manages entertainment configurations for a given bridge.

    This class provides functionality to fetch and manage entertainment configurations
    associated with a bridge device.

    Attributes:
        _bridge (Bridge): The bridge device for which to manage entertainment configurations.
        _ent_conf_repo (EntertainmentConfigurationRepository): Repository for the entertainment configurations.
        _entertainment_configs (list[EntertainmentConfiguration] | None): Cached list of entertainment configurations.
    """

    def __init__(self, bridge: Bridge):
        """Initializes the EntertainmentService with a specific bridge device."""

        self._bridge = bridge
        self._ent_conf_repo = EntertainmentConfigurationRepository(bridge)
        self._entertainment_configs: dict[str, EntertainmentConfiguration] | None = None

    def get_entertainment_configs(self) -> dict[str, EntertainmentConfiguration]:
        """Retrieves the entertainment configurations for the bridge.

        Returns:
            dict[str, EntertainmentConfiguration]: A dictionary of entertainment configurations.
        """

        if self._entertainment_configs is None:
            self._entertainment_configs = self._ent_conf_repo.fetch_configurations()
        return self._entertainment_configs

    def get_config_by_id(self, config_id: str) -> EntertainmentConfiguration | None:
        """Gets a specific entertainment configuration by its ID.

        Args:
            config_id (str): The ID of the configuration to retrieve.

        Returns:
            EntertainmentConfiguration | None: The requested configuration if found, otherwise None.
        """

        for config in self._entertainment_configs.values():
            if config.id == config_id:
                return config
        return None

    def get_ent_conf_repo(self) -> EntertainmentConfigurationRepository:
        """Returns the entertainment configuration repository.

        Returns:
            EntertainmentConfigurationRepository: The repository for entertainment configurations.
        """

        return self._ent_conf_repo


class Streaming:
    """Facilitates streaming operations for an entertainment configuration.

    This class is responsible for starting and stopping streaming, setting the color space, and managing input data.

    Attributes:
        _dtls_service (Dtls): Service for DTLS (Datagram Transport Layer Security) operations.
        _streaming_service (StreamingService): Service for handling streaming operations.
    """

    def __init__(
            self,
            bridge: Bridge,
            entertainment_configuration: EntertainmentConfiguration,
            ent_conf_repo: EntertainmentConfigurationRepository,
    ):
        """Initializes the Streaming class with bridge and entertainment configuration details."""

        self._dtls_service = Dtls(bridge)
        self._streaming_service = StreamingService(
            entertainment_configuration, ent_conf_repo, self._dtls_service
        )

    def start_stream(self):
        """Starts the streaming service."""

        self._streaming_service.start_stream()

    def stop_stream(self):
        """Stops the streaming service."""

        self._streaming_service.stop_stream()

    def set_color_space(self, color_space: str):
        """Sets the color space for the streaming service.

        Args:
            color_space (str): The color space to be used in streaming. (rgb or xyb)
        """
        self._streaming_service.set_color_space(color_space)

    def set_input(
            self,
            input_data: Union[tuple[int, int, int, int], tuple[float, float, float, int]],
    ):
        """Sets the input data for the streaming service.

        The input data can be a tuple of either three integers or three floats followed by an integer.
        The first three values represent color: in RGB format (0-255 range) when integers,
        or in xyb format (CIE color space, 0.0-1.0 range) for floats, where 'b' stands for brightness.
        The last integer in both cases is the ID of the light in the chosen Entertainment Area.

        Args:
            input_data (Union[tuple[int, int, int, int], tuple[float, float, float, int]]):
                The input data to be used in streaming. This can be either a tuple of three integers (RGB format)
                or a tuple of three floats (xyb format in CIE color space) followed by an integer (the light ID).

        """

        self._streaming_service.set_input(input_data)
