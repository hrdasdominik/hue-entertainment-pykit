from typing import Any, Dict

from api.utils.decorators import singleton

from entertainment_api.configuration.entertainment_configuration_repository import \
    EntertainmentConfigurationRepository


@singleton
class EntertainmentConfigurationService:
    def __init__(self,
                 entertainment_configuration_repository: EntertainmentConfigurationRepository):
        self._entertainment_configuration_repository = entertainment_configuration_repository

        self.entertainment_configurations: Dict[
            str, Any] = self._fetch_configurations()

    def get_configurations(self) -> Dict[str, Any]:
        return self.entertainment_configurations

    def _fetch_configurations(self):
        configs = self._entertainment_configuration_repository.get_configuration()

        temp = {}
        for config in configs:
            temp[config.id] = config
        return temp

    def start_stream(self, payload: Dict[str, Any]):
        payload["action"] = "start"
        self._entertainment_configuration_repository.put_configuration(payload)
