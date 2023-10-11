"""_summary_"""
import asyncio

from api.bridge.bridge import Bridge
from api.light.light_repository import LightRepository
from api.light.light_service import LightService
from entertainment_api.configuration.entertainment_configuration_repository import \
    EntertainmentConfigurationRepository
from entertainment_api.configuration.entertainment_configuration_service import \
    EntertainmentConfigurationService


def main():
    typ = ""

    """_summary_"""
    bridge = Bridge()
    bridge.get_ip_with_broker()
    if typ == "api":
        light_repository = LightRepository(bridge)
        light_repository.generate_key()
        light_service = LightService(light_repository)
        asyncio.run(light_service.update_lights())
    else:
        ent_conf_repo = EntertainmentConfigurationRepository(bridge)
        ent_conf_repo.generate_key()
        ent_conf_service = EntertainmentConfigurationService(ent_conf_repo)
        entertainment = ent_conf_service.get_configurations()[
            "2022ffc4-1b73-4a43-b376-4c45369bf207"]

        payload = {"id": entertainment.id}
        ent_conf_service.start_stream(payload)


if __name__ == "__main__":
    main()
