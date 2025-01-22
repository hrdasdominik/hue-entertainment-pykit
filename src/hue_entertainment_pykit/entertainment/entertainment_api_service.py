import logging
from typing import Dict

from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.entertainment.entertainment import Entertainment
from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import \
    EntertainmentConfiguration
from src.hue_entertainment_pykit.http.http_client import HttpClient
from src.hue_entertainment_pykit.http.http_method_enum import HttpMethodEnum
from src.hue_entertainment_pykit.http.http_payload import HttpPayload
from src.hue_entertainment_pykit.utils.endpoint_enum import EndpointEnum


class EntertainmentApiService:
    def __init__(self, bridge: Bridge):
        self._bridge: Bridge = bridge
        self._http_client: HttpClient = HttpClient()
        self._http_client.set_base_url(bridge.get_ip_address())
        self._http_client.add_headers("hue-application-key", bridge.get_username())

    def fetch_all(self) -> Dict[str, Entertainment]:
        """
        Fetches all entertainment configurations from the Philips Hue Bridge.

        Returns:
            dict[str, EntertainmentConfiguration]: A dictionary of EntertainmentConfiguration instances representing
            each configuration fetched from the Hue Bridge.
        """

        logging.info("Fetching Entertainments")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_ENTERTAINMENT)
        data = response.json()["data"]
        entertainment_dict = {}
        for item in data:
            entertainment_dict[item["id"]] = Entertainment(
                id=item["id"],
                id_v1=item["id_v1"],
                owner=item["owner"],
                renderer=item["renderer"],
                renderer_reference=item["renderer_reference"],
                proxy=item["proxy"],
                equalizer=item["equalizer"],
                segments=item["segments"]
            )
        logging.info("Fetched Entertainments")
        return entertainment_dict

    def fetch_by_id(self, identification: str) -> Entertainment:
        """
        Fetches entertainment from the Philips Hue Bridge.

        Returns:
            Entertainment: An instance representing Entertainment fetched from the Hue Bridge.
        """

        logging.info(f"Fetching Entertainment by identification {identification}")
        response = self._http_client.make_request(HttpMethodEnum.GET, EndpointEnum.RESOURCE_ENTERTAINMENT, identification=identification)
        data = response.json()["data"][0]
        entertainment = Entertainment(
            id=data["id"],
            id_v1=data["id_v1"],
            owner=data["owner"],
            renderer=data["renderer"],
            renderer_reference=data["renderer_reference"],
            proxy=data["proxy"],
            equalizer=data["equalizer"],
            segments=data["segments"]
        )
        logging.info(f"Fetched Entertainment {entertainment}")
        return entertainment

    def put(self, http_request: HttpPayload):
        """
        Updates an existing entertainment configuration on the Philips Hue Bridge.

        Parameters:
            http_request (HttpPayload): The payload containing the updated entertainment configuration data.
        """
        logging.info("Updating Entertainment")
        json_data = http_request.get_data()
        identification = json_data["id"]
        del json_data["id"]

        self._http_client.make_request(HttpMethodEnum.PUT, EndpointEnum.RESOURCE_ENTERTAINMENT,
                                       identification=identification, json=json_data)
        logging.info("Entertainment updated successfully.")
