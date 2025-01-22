import logging
from typing import Optional, Dict

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import \
    EntertainmentConfiguration, EntertainmentChannel
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration_api_service import \
    EntertainmentConfigurationApiService
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration_create_request import \
    EntertainmentConfigurationCreateRequest
from src.hue_entertainment_pykit.exception.entertainment_exception import EntertainmentException
from src.hue_entertainment_pykit.http.http_payload import HttpPayload
from src.hue_entertainment_pykit.utils.stream_action_enum import StreamActionEnum


class EntertainmentConfigurationService:
    def __init__(self, bridge: Bridge):
        self._bridge = bridge
        self._entertainment_configuration_api_service = EntertainmentConfigurationApiService(bridge)
        self._entertainment_configuration_dict: Dict[str, EntertainmentConfiguration] = self.get_all()
        self._active_entertainment_configuration: Optional[EntertainmentConfiguration] = None

    def create(self, create_request: EntertainmentConfigurationCreateRequest) -> EntertainmentConfiguration:
        logging.info(f"Creating entertainment configuration with parameters: {create_request}")
        entertainment_configuration: EntertainmentConfiguration = self._entertainment_configuration_api_service.create(
            create_request)
        logging.info(f"Entertainment configuration created {entertainment_configuration}")
        return entertainment_configuration

    def get_all(self) -> Dict[str, EntertainmentConfiguration]:
        logging.info("Fetching entertainment configurations")
        self._entertainment_configuration_dict = self._entertainment_configuration_api_service.fetch_all()
        logging.info("Entertainment configurations fetched successfully")
        return self._entertainment_configuration_dict

    def get_by_name(self, name: str) -> EntertainmentConfiguration:
        logging.info(f"Fetching entertainment configuration with name: {name}")
        entertainment_configuration = self._entertainment_configuration_dict.get(name)
        logging.info(f"Entertainment configuration {name} fetched successfully")
        return entertainment_configuration

    def get_active(self) -> EntertainmentConfiguration:
        return self._active_entertainment_configuration

    def set_active(self, entertainment_configuration_name: str) -> None:
        logging.info(f"Setting Entertainment Configuration {entertainment_configuration_name}")
        entertainment_configuration = self._entertainment_configuration_dict.get(entertainment_configuration_name)

        if not entertainment_configuration:
            raise EntertainmentException(
                f"No '{entertainment_configuration_name}' entertainment configuration found on bridge '{self._bridge.get_name()}'"
            )

        self._active_entertainment_configuration = entertainment_configuration
        logging.info(f"Entertainment Configuration {entertainment_configuration.name} successfully set")

    def get_channels(self) -> list[EntertainmentChannel]:
        if not self._active_entertainment_configuration:
            raise EntertainmentException("No active entertainment configuration")

        logging.info("Fetching channels for entertainment configuration '%s'",
                     self._active_entertainment_configuration.name)

        return self._active_entertainment_configuration.channels

    def setup_for_streaming(self) -> None:
        if not self._active_entertainment_configuration:
            raise EntertainmentException("No active Entertainment Configuration selected")

        logging.info(f"Starting stream on active Entertainment Configuration {self._active_entertainment_configuration.name}")

        payload: HttpPayload = HttpPayload(
            {
                "id": self._active_entertainment_configuration.id,
                "action": StreamActionEnum.START.value
            }
        )
        self._entertainment_configuration_api_service.put(payload)
        logging.info(f"Started stream on Entertainment Configuration {self._active_entertainment_configuration.name}")

    def setup_for_stop_streaming(self) -> None:
        logging.info("Stopping stream on Entertainment Configuration %s",
                     self._active_entertainment_configuration.name)
        if self._active_entertainment_configuration is None:
            raise EntertainmentException("No Entertainment Configuration selected")

        payload: HttpPayload = HttpPayload(
            {
                "id": self._active_entertainment_configuration.id,
                "action": "stop"
            }
        )
        self._entertainment_configuration_api_service.put(payload)
        logging.info("Stopped stream on Entertainment Configuration %s",
                     self._active_entertainment_configuration.name)
