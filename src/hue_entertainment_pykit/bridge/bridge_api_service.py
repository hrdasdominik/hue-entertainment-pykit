import logging

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.http.http_client import HttpClient
from src.hue_entertainment_pykit.http.http_method_enum import HttpMethodEnum
from src.hue_entertainment_pykit.light.light import Light
from src.hue_entertainment_pykit.utils.endpoint_enum import EndpointEnum


# pylint: disable=too-few-public-methods
class BridgeApiService:
    def __init__(self):
        self._http_client = HttpClient()

    def add_hue_application_key(self, hue_application_key: str) -> None:
        logging.info("Adding Hue Application Key: {}".format(hue_application_key))
        self._http_client.add_headers("hue-application-key", hue_application_key)
        logging.info("Successfully added Hue Application Key: {}".format(hue_application_key))

    def fetch_lights(self) -> list[Light]:
        logging.info("Fetching lights")
        response_light = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_LIGHT)
        data: list[Light] = response_light.json()["data"]
        logging.info("Fetched lights successfully")
        return data
