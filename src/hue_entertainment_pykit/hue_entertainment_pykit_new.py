import logging

from src.hue_entertainment_pykit.bridge.bridge_repository import BridgeRepository
from src.hue_entertainment_pykit.bridge.entertainment_configuration_repository import EntertainmentConfigurationRepository
from src.hue_entertainment_pykit.models.bridge import Bridge
from src.hue_entertainment_pykit.models.entertainment_configuration import EntertainmentConfiguration
from src.hue_entertainment_pykit.models.light import LightBase
from src.hue_entertainment_pykit.network.dtls import Dtls
from src.hue_entertainment_pykit.network.mdns import Mdns
from src.hue_entertainment_pykit.services.discovery_service import DiscoveryService
from src.hue_entertainment_pykit.services.streaming_service import StreamingService
from src.hue_entertainment_pykit.utils.logger import setup_logging


class HueEntertainmentPyKit:
    def __init__(self):
        setup_logging(
            level=logging.WARNING,
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

        if self._streaming.is_stream_active() is True:
            raise Exception("Stream is already active")

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

    def set_lights_functions(self,
                             light_list: list[LightBase],
                             transition_time: float = 0.0):
        self._streaming.set_input(light_list, transition_time)

    def get_all_bridges(self) -> dict[str, Bridge]:
        if not self._bridges:
            self._bridges = self._discovery_service.discover()
        return self._bridges

    def set_bridge(self, bridge: Bridge):
        self._bridge_repository.set_base_url(bridge.get_ip_address())
        self._bridge_repository.set_headers({"hue-application-key": bridge.get_username()})

        self._entertainment_configuration_repository = EntertainmentConfigurationRepository(bridge)
        self._dtls = Dtls(bridge)

        if not self._entertainment_configurations:
            self._entertainment_configurations = self._entertainment_configuration_repository.fetch_configurations()

    def get_entertainment_configuration(self):
        return self._entertainment_configuration

    def get_entertainment_configurations(self):
        return self._entertainment_configurations

    def set_entertainment_configuration(self, entertainment_configuration: EntertainmentConfiguration):
        self._entertainment_configuration = entertainment_configuration

        self._streaming = StreamingService(
            self._entertainment_configuration,
            self._entertainment_configuration_repository,
            self._dtls
        )

    def get_lights(self):
        return self._bridge_repository.fetch_lights()

    def get_entertainment_lights(self):
        return self._bridge_repository.fetch_entertainment_lights(self._entertainment_configuration)

    def connect_manually_to_bridge(self, ip_address: str):
        ...

    @classmethod
    def modify_log_config(
            cls,
            level: int = logging.DEBUG,
            max_file_size: int = 1024 * 1024 * 5,
            backup_count: int = 3,
    ):
        setup_logging(level, max_file_size, backup_count)
