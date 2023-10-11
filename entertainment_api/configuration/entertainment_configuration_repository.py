import logging
from typing import List, Optional, Any, Dict

import requests

from api.base_repository import BaseRepository
from api.bridge.bridge import Bridge
from api.exceptions.api_exception import ApiException
from api.utils.decorators import singleton
from api.utils.status_code import StatusCode
from entertainment_api.configuration.entertainment_configuration_model import \
    EntertainmentConfiguration


@singleton
class EntertainmentConfigurationRepository(BaseRepository):
    def __init__(self, bridge: Bridge):
        super().__init__(bridge)

        self.set_default_url(
            self.get_default_url() + "resource/entertainment_configuration")

    def get_configuration(self, identification: Optional[str] = None) -> List[
        EntertainmentConfiguration]:
        """Get method which fetches all entertainment configurations"""
        logging.debug(f"Started {self.__class__.__name__}.get_configuration")

        url = self.get_default_url()

        if identification is not None:
            logging.debug(f"Entertainment identification: {identification}")
            url += f"/{identification}"

        response = requests.request("GET", url=url,
                                    headers=self.get_headers(), verify=False)

        if response.status_code == StatusCode.OK.value:
            data: List = response.json()["data"]

            logging.debug(f"{self.__class__.__name__} response json: {data}")

            entertainments: List[EntertainmentConfiguration] = []
            for item in data:
                entertainment = EntertainmentConfiguration(item)

                entertainments.append(entertainment)
            return entertainments

        elif response.status_code == StatusCode.BAD_REQUEST.value:
            raise ApiException.bad_request(response)
        else:
            raise ApiException.response_status(response)

    def post_configuration(self):
        pass

    def put_configuration(self, payload: Dict[str, Any]):
        logging.debug(f"Started {self.__class__.__name__}.put_configuration")
        logging.debug(f"Entertainment identification: {payload['id']}")

        url = self.get_default_url() + f"/{payload['id']}"
        del payload["id"]

        response = requests.request("PUT", url=url,
                                    headers=self.get_headers(),
                                    json=payload, verify=False)

        if response.status_code == StatusCode.OK.value:
            logging.debug(f"Update successful: {response.json()}")
        else:
            raise ApiException.response_status(response)

    def delete_configuration(self, identification: str):
        pass
