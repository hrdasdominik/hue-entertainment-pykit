import logging

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.bridge.bridge_streaming_service import BridgeStreamingService
from src.hue_entertainment_pykit.entertainment.entertainment_service import EntertainmentService
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration_service import \
    EntertainmentConfigurationService
from src.hue_entertainment_pykit.exception.bridge_exception import BridgeException
from src.hue_entertainment_pykit.exception.entertainment_exception import EntertainmentException
from src.hue_entertainment_pykit.light.light_abstract import LightAbstract
from src.hue_entertainment_pykit.light.light_service import LightService
from src.hue_entertainment_pykit.light.light_xyb import LightXYB
from src.hue_entertainment_pykit.utils.color_space_enum import ColorSpaceEnum


class BridgeService:
    def __init__(self, bridge: Bridge):
        self._bridge = bridge
        self._light_service = LightService(self._bridge)
        self._entertainment_service = EntertainmentService(self._bridge)
        self._entertainment_configuration_service = EntertainmentConfigurationService(self._bridge)
        self._bridge_streaming_service: BridgeStreamingService = BridgeStreamingService(self._bridge,
                                                                                        self._entertainment_configuration_service)

    def get_bridge(self):
        return self._bridge

    def get_entertainment_configuration_service(self):
        return self._entertainment_configuration_service

    def fetch_all_lights(self) -> list[LightAbstract]:
        """Fetch all lights by using active entertainment channels and return a list of LightAbstract."""

        light_list = self._light_service.get_all()
        if not light_list:
            raise BridgeException(
                f"There are no lights available on the bridge {self._bridge.get_name()}"
            )

        channels = self._entertainment_configuration_service.get_active().channels

        abstract_light_list = []
        for channel in channels:
            for member in channel.members:
                entertainment = self._entertainment_service.get_entertainment_by_id(
                    member.service.rid
                )
                if not entertainment:
                    raise EntertainmentException(
                        f"Entertainment not found with id {member.service.rid}"
                    )

                light = self._light_service.get_by_id(entertainment.renderer_reference.get("rid"))
                abstract_light_list.append(
                    LightXYB.transform_hue_light_to_light_model(channel, light)
                )
                break

        return abstract_light_list

    def is_streaming_active(self) -> bool:
        return self._bridge_streaming_service.is_stream_active()

    def start_streaming(self):
        logging.info("Starting streaming service")
        if not self._entertainment_configuration_service.get_active():
            err_msg = "Entertainment Configuration not set"
            logging.error(err_msg)
            raise EntertainmentException(err_msg)

        if self._bridge_streaming_service.is_stream_active():
            err_msg = "Stream already active on bridge " + self._bridge.get_name()
            logging.error(err_msg)
            raise EntertainmentException(err_msg)

        self._bridge_streaming_service.start_stream()
        logging.info("Streaming started")

    def stop_streaming(self):
        logging.info("Stopping streaming")
        if not self._bridge_streaming_service:
            err_msg = "Stream Service not started"
            logging.error(err_msg)
            raise BridgeException(err_msg)

        if not self._bridge_streaming_service.is_stream_active():
            err_msg = "Stream not active"
            logging.error(err_msg)
            raise BridgeException(err_msg)

        self._bridge_streaming_service.stop_stream()
        logging.info("Bridge Stream Service stopped")

    def set_color_space(self, color_space: ColorSpaceEnum):
        logging.info(f"Setting color space {color_space.value}")
        if not self._bridge_streaming_service:
            err_msg = "Bridge Stream Service not started"
            logging.error(err_msg)
            raise Exception(err_msg)

        self._bridge_streaming_service.set_color_space(color_space)

    def send_color_and_brightness(self, light_list: list[LightAbstract]):
        self._bridge_streaming_service.set_input(light_list)
