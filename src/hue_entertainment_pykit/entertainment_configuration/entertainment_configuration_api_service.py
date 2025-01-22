import logging
from typing import Dict

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import \
    EntertainmentConfiguration, EntertainmentChannel
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration_create_request import \
    EntertainmentConfigurationCreateRequest
from src.hue_entertainment_pykit.http.http_client import HttpClient
from src.hue_entertainment_pykit.http.http_method_enum import HttpMethodEnum
from src.hue_entertainment_pykit.http.http_payload import HttpPayload
from src.hue_entertainment_pykit.light.light_xyb import LightXYB
from src.hue_entertainment_pykit.utils.endpoint_enum import EndpointEnum


class EntertainmentConfigurationApiService:
    def __init__(self, bridge: Bridge):
        self._bridge: Bridge = bridge
        self._http_client: HttpClient = HttpClient()
        self._http_client.set_base_url(bridge.get_ip_address())
        self._http_client.add_headers("hue-application-key", bridge.get_username())

    def create(self, create_request: EntertainmentConfigurationCreateRequest) -> EntertainmentConfiguration:
        """
        Creates Entertainment Configuration in Philips Hue Bridge.

        Returns:
            Response EntertainmentConfiguration object from the Hue Bridge.
        """
        logging.info("Creating Entertainment Configuration")
        response = self._http_client.make_request(HttpMethodEnum.POST, EndpointEnum.RESOURCE_ENTERTAINMENT,
                                                  json=HttpPayload(create_request.to_dict()))

        entertainment_configuration = EntertainmentConfiguration.from_dict(response.json()["data"])
        logging.info("Created Entertainment Configuration %s", entertainment_configuration.name)
        return entertainment_configuration

    def fetch_all(self) -> Dict[str, EntertainmentConfiguration]:
        """
        Fetches all entertainment configurations from the Philips Hue Bridge.

        Returns:
            dict[str, EntertainmentConfiguration]: A dictionary of EntertainmentConfiguration instances representing
            each configuration fetched from the Hue Bridge.
        """

        logging.info("Fetching entertainment configurations")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_ENTERTAINMENT_CONFIGURATION)
        data = response.json()["data"]
        entertainment_configuration_dict = {}
        for item in data:
            entertainment_configuration_dict[item["name"]] = EntertainmentConfiguration(
                item["id"],
                item["type"],
                item["id_v1"],
                item["name"],
                item["status"],
                item["configuration_type"],
                item["metadata"],
                item["stream_proxy"],
                item["channels"],
                item["locations"],
                item["light_services"]
            )
        logging.info("Fetched entertainment configurations")
        return entertainment_configuration_dict

    def put(self, http_request: HttpPayload):
        """
        Updates an existing entertainment configuration on the Philips Hue Bridge.

        Parameters:
            http_request (HttpPayload): The payload containing the updated entertainment configuration data.
        """
        logging.info("Updating Entertainment Configuration")
        json_data = http_request.get_data()
        identification = json_data["id"]
        del json_data["id"]

        self._http_client.make_request(HttpMethodEnum.PUT, EndpointEnum.RESOURCE_ENTERTAINMENT_CONFIGURATION,
                                       identification=identification, json=json_data)
        logging.info("Entertainment Configuration updated successfully.")

    def fetch_all_lights(self,
                         entertainment_configuration: EntertainmentConfiguration) -> list[LightXYB]:

        logging.info("Fetching Entertainment Configuration light list")
        channel_list: list[EntertainmentChannel] = entertainment_configuration.channels
        response_entertainment = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_ENTERTAINMENT)
        response_light = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_LIGHT)

        entertainment_data_list = response_entertainment.json()["data"]
        light_data_list = response_light.json()["data"]

        light_list: list[LightXYB] = []
        for channel in channel_list:
            rid = channel.members[0].service.rid

            for entertainment_data in entertainment_data_list:
                if entertainment_data["id"] == rid:
                    for light in light_data_list:
                        if light["id"] == entertainment_data["renderer_reference"]["rid"]:
                            light_name = light["metadata"]["name"]
                            xy_dict = light["color"]["xy"]
                            x = xy_dict["x"]
                            y = xy_dict["y"]
                            b = light["dimming"]["brightness"] / 100
                            light_list.append(LightXYB(channel.channel_id, light_name, x, y, b))

        logging.info("Fetched Entertainment Configuration light list")
        return light_list
