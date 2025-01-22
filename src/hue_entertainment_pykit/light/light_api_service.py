import logging

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.entertainment.entertainment import Entertainment
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import \
    EntertainmentConfiguration
from src.hue_entertainment_pykit.http.http_client import HttpClient
from src.hue_entertainment_pykit.http.http_method_enum import HttpMethodEnum
from src.hue_entertainment_pykit.http.http_payload import HttpPayload
from src.hue_entertainment_pykit.light.light import Light
from src.hue_entertainment_pykit.utils.endpoint_enum import EndpointEnum


class LightApiService:
    def __init__(self, bridge: Bridge):
        self._bridge: Bridge = bridge
        self._http_client: HttpClient = HttpClient()
        self._http_client.set_base_url(bridge.get_ip_address())
        self._http_client.add_headers("hue-application-key", bridge.get_username())

    def fetch_by_id(self, identification: str) -> Light:
        """
        Fetches light from the Philips Hue Bridge.

        Returns:
            Light: An instance representing Light fetched from the Hue Bridge.
        """

        logging.info(f"Fetching Light by identification {identification}")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_LIGHT, identification=identification)
        data = response.json()["data"][0]
        light = Light(
            id=data["id"],
            id_v1=data["id_v1"],
            owner=data["owner"],
            metadata=data["metadata"],
            product_data=data["product_data"],
            identify=data["identify"],
            service_id=data["service_id"],
            on=data["on"],
            dimming=data["dimming"],
            color_temperature=data["color_temperature"],
            color=data["color"],
            dynamics=data["dynamics"],
            alert=data["alert"],
            signaling=data["signaling"],
            mode=data["mode"],
            effects=data["effects"],
            effects_v2=data["effects_v2"],
            timed_effects=data["timed_effects"],
            powerup=data["powerup"]
        )
        logging.info(f"Fetched light {light}")
        return light

    def fetch_all(self) -> dict[str, Light]:
        """
        Fetches all entertainment configurations from the Philips Hue Bridge.

        Returns:
            dict[str, EntertainmentConfiguration]: A dictionary of EntertainmentConfiguration instances representing
            each configuration fetched from the Hue Bridge.
        """

        logging.info("Fetching Entertainments")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_LIGHT)
        data = response.json()["data"]
        light_dict = {}
        for item in data:
            light_dict[item["metadata"]["name"]] = Light(
                id=item["id"],
                id_v1=item["id_v1"],
                owner=item["owner"],
                metadata=item["metadata"],
                product_data=item["product_data"],
                identify=item["identify"],
                service_id=item["service_id"],
                on=item["on"],
                dimming=item["dimming"],
                color_temperature=item["color_temperature"],
                color=item["color"],
                dynamics=item["dynamics"],
                alert=item["alert"],
                signaling=item["signaling"],
                mode=item["mode"],
                effects=item["effects"],
                effects_v2=item["effects_v2"],
                timed_effects=item["timed_effects"],
                powerup=item["powerup"]
            )
        logging.info("Fetched Entertainments")
        return light_dict

    def put(self, http_request: HttpPayload):
        """
        Updates an existing light on the Philips Hue Bridge.

        Parameters:
            http_request (HttpPayload): The payload containing the updated light data.
        """
        logging.info("Updating Light")
        json_data = http_request.get_data()
        identification = json_data["id"]
        del json_data["id"]

        self._http_client.make_request(HttpMethodEnum.PUT, EndpointEnum.RESOURCE_LIGHT,
                                       identification=identification, json=json_data)
        logging.info("Light updated successfully.")
