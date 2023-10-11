import requests
import json
import logging
from typing import Optional, Any

from aiohttp import ClientSession

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

        self.set_default_url(self.get_default_url() + "resource/light")

    def get_lights(self, identification: Optional[str] = None) \
            -> list[Light]:
        logging.debug("Started 'get_light'")

        url: str = self.get_default_url()

        if identification is not None:
            logging.debug(f"Light identification: {identification}")
            url = url + f"/{identification}"

        response = requests.request("GET", url=url, headers=self.get_headers(),
                                    verify=False)

        if response.status_code == StatusCode.OK.value:
            data: list[dict[str, Any]] = response.json()["data"]

            logging.debug(f"Response json: {data}")

            lights: list[Light] = []
            for light in data:
                lights.append(Light(light))

            return lights

        else:
            raise ApiException.response_status(response)

    async def put_light(self, light: Light, session: ClientSession):
        """Update method for the light"""
        logging.debug(f"Started 'put_light' identification: {light.id}")

        url: str = self.get_default_url() + f"/{light.id}"
        headers = self.get_headers()
        payload = light.to_dict()

        logging.debug(f"Request method['put_light'] = {payload}")

        return await session.request("PUT", url=url, headers=headers,
                                     json=payload, ssl=False)
