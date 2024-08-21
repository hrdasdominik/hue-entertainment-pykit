import logging
from typing import Optional

from bridge.bridge_repository import BridgeRepository
from bridge.entertainment_configuration_repository import EntertainmentConfigurationRepository
from models.entertainment_configuration import EntertainmentConfiguration
from network.dtls import Dtls
from network.mdns import Mdns
from services.discovery_service import DiscoveryService
from services.streaming_service import StreamingService
from models.bridge import Bridge
from utils.logger import setup_logging


class HueEntertainmentPyKit:
    def __init__(self):
        setup_logging(
            level=logging.DEBUG,
            max_file_size=1024 * 1024 * 5,
            backup_count=3
        )

        self._bridges: dict[str, Bridge] = {}

        self._mdns = Mdns()
        self._bridge_repository = BridgeRepository()
        self._discovery_service = DiscoveryService(self._mdns, self._bridge_repository)

        self._dtls: Dtls | None = None
        self._streaming: StreamingService | None = None
        self._entertainment_configuration: EntertainmentConfiguration | None = None
        self._entertainment_configurations: dict[str, EntertainmentConfiguration] = {}
        self._entertainment_configuration_repository: EntertainmentConfigurationRepository | None = None

    def start_stream(self):
        if self._streaming is None:
            raise Exception("Stream not started due to streaming being None")

        self._streaming.start_stream()

    def stop_stream(self):
        self._streaming.stop_stream()

    def set_color_space(self, color_space: str):
        """Sets the color space for the streaming service.

        Args:
            color_space (str): The color space to be used in streaming. (rgb or xyb)
        """
        if self._streaming is None:
            raise Exception("Color space not set due to streaming being None")

        self._streaming.set_color_space(color_space)

    def set_single_light(self, color_with_id: tuple[float, float, float, int] | tuple[int, int, int, int]):
        self._streaming.set_input([color_with_id])

    def set_group_lights(self, color_id_list: list[tuple[float, float, float, int] | tuple[int, int, int, int]]):
        self._streaming.set_input(color_id_list)

    def get_all_light_ids(self):
        if self._entertainment_configuration is None:
            raise Exception('No entertainment configuration')

        channel_list = []

        channels = self._entertainment_configuration.channels
        for channel in channels:
            channel_list.append((channel.channel_id, channel.position))
        return channel_list

    def get_all_bridges(self) -> dict[str, Bridge]:
        if not self._bridges:
            self._bridges = self._discovery_service.discover()
        return self._bridges

    def set_bridge(self, bridge: Bridge):
        self._entertainment_configuration_repository = EntertainmentConfigurationRepository(bridge)
        self._dtls = Dtls(bridge)

        if not self._entertainment_configurations:
            self._entertainment_configurations = self._entertainment_configuration_repository.fetch_configurations()

    def get_entertainment_configurations(self):
        return self._entertainment_configurations

    def set_entertainment_configuration(self, entertainment_configuration: EntertainmentConfiguration):
        self._entertainment_configuration = entertainment_configuration

        self._streaming = StreamingService(
            self._entertainment_configuration,
            self._entertainment_configuration_repository,
            self._dtls
        )

    def connect_manually_to_bridge(self, ip_address: str):
        ...

    def modify_log_config(
            self,
            level: int = logging.WARNING,
            max_file_size: int = 1024 * 1024 * 5,
            backup_count: int = 3,
    ):
        setup_logging(level, max_file_size, backup_count)
