import requests
import logging
from typing import Optional, Any

from api.base_repository import BaseRepository
from api.bridge.bridge import Bridge
from api.exceptions.api_exception import ApiException
from api.light.light_model import Light
from api.utils.decorators import singleton
from api.utils.status_code import StatusCode


@singleton
class LightRepository(BaseRepository):
    def __init__(self, bridge: Bridge):
        super().__init__(bridge)

    def get_lights(self, identification: Optional[str] = None) \
            -> list[Light]:
        logging.debug("Started 'get_light'")

        url: str = self.get_default_url() + "resource/light"

        if identification is not None:
            logging.debug(f"Light identification: {identification}")
            url = url + f"/{identification}"

        response = requests.request("GET", url=url, headers=self.get_headers(),
                                    verify=False)

        if response.status_code == StatusCode.OK.value:
            data: list[dict[str, Any]] = response.json()["data"]

            logging.debug(f"json: {data}")

            lights: list[Light] = []
            for light in data:
                lights.append(Light(light))

            return lights

        else:
            raise ApiException.response_status(response)

    def put_light(self, light: Light):
        """Update method for the light"""
        logging.debug(f"Started 'put_light' identification: {light.id}")

        url: str = self.get_default_url() + f"resource/light/{light.id}"

        headers = self.get_headers()

        payload = light.to_dict()

        response = requests.request("PUT", url=url, headers=headers,
                                    json=payload, verify=False)

        logging.debug(f"Request method['put_light'] = {payload}")
        if response.status_code == (
                StatusCode.OK.value or StatusCode.MULTI_STATUS.value):
            logging.debug(f"Update successful: {response.json()}")
        else:
            raise ApiException.response_status(response)
