import logging

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.bridge.bridge_discovery_service import BridgeDiscoveryService
from src.hue_entertainment_pykit.bridge.bridge_service import BridgeService
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import \
    EntertainmentConfiguration
from src.hue_entertainment_pykit.light.light_abstract import LightAbstract
from src.hue_entertainment_pykit.utils.color_space_enum import ColorSpaceEnum
from src.hue_entertainment_pykit.utils.logger import setup_logging


class HueEntertainmentPyKit:
    def __init__(self, app_name: str):
        setup_logging(
            level=logging.DEBUG,
            max_file_size=1024 * 1024 * 5,
            backup_count=3
        )

        self._bridge_discovery_service = BridgeDiscoveryService(app_name)
        self._bridge_service_dict: dict[str, BridgeService] = {}

        self._init_setup()

    @classmethod
    def modify_log_config(
            cls,
            level: int = logging.DEBUG,
            max_file_size: int = 1024 * 1024 * 5,
            backup_count: int = 3,
            reconfigure: bool = True
    ) -> None:
        setup_logging(level, max_file_size, backup_count, reconfigure)

    def _init_setup(self) -> None:
        bridge_dict: dict[str, Bridge] = self._bridge_discovery_service.fetch_bridge_dict()

        for bridge in bridge_dict.values():
            bridge_service = BridgeService(bridge)
            self._bridge_service_dict[bridge_service.get_bridge().get_name()] = bridge_service

    def get_bridge_name_list(self) -> list[str]:
        return list(self._bridge_service_dict.keys())

    def get_entertainment_configuration_name_list(self, bridge_name: str) -> list[str]:
        bridge_service = self._bridge_service_dict[bridge_name]

        if not bridge_service:
            raise Exception(f"Bridge {bridge_name} not found")

        entertainment_configuration_service = bridge_service.get_entertainment_configuration_service()
        entertainment_configuration_dict: dict[
            str, EntertainmentConfiguration] = entertainment_configuration_service.get_all()

        return [entertainment_configuration.name for entertainment_configuration in
                entertainment_configuration_dict.values()]

    def set_active_entertainment_configuration_on_bridge(self, bridge_name: str,
                                                         entertainment_configuration_name: str) -> None:
        bridge_service = self._bridge_service_dict.get(bridge_name)

        if not bridge_service:
            raise Exception(f"Bridge service {bridge_name} not found")

        entertainment_configuration_service = bridge_service.get_entertainment_configuration_service()
        entertainment_configuration = entertainment_configuration_service.get_by_name(entertainment_configuration_name)

        if not entertainment_configuration:
            raise Exception(
                f"Entertainment configuration {entertainment_configuration_name} not found on bridge {bridge_name}")

        entertainment_configuration_service.set_active(entertainment_configuration.name)

    def get_light_list_from_bridge(self, bridge_name: str) -> list[LightAbstract]:
        bridge_service = self._bridge_service_dict[bridge_name]

        if not bridge_service:
            raise Exception(f"Bridge {bridge_name} not found")

        return bridge_service.fetch_all_lights()

    def start_streaming_on_bridge(self, bridge_name: str) -> None:
        bridge_service = self._bridge_service_dict.get(bridge_name)

        bridge_service.start_streaming()

    def start_streaming_on_all_bridges(self):
        for bridge_service in self._bridge_service_dict.values():
            bridge_service.start_streaming()

    def stop_streaming_on_bridge(self, bridge_name: str) -> None:
        bridge_service = self._bridge_service_dict.get(bridge_name)
        bridge_service.stop_streaming()

    def stop_streaming_on_all_bridges(self):
        for bridge_service in self._bridge_service_dict.values():
            if bridge_service.is_streaming_active():
                bridge_service.stop_streaming()

    def set_color_space(self, color_space: ColorSpaceEnum) -> None:
        for bridge_service in self._bridge_service_dict.values():
            bridge_service.set_color_space(color_space)

    def set_color_and_brightness(self, bridge_name: str, light_list: list[LightAbstract]):
        bridge_service = self._bridge_service_dict.get(bridge_name)
        if not bridge_service:
            raise Exception(f"Bridge {bridge_name} not found")

        if not bridge_service.is_streaming_active():
            raise Exception(f"Bridge {bridge_name} not streaming")

        bridge_service.send_color_and_brightness(light_list)
