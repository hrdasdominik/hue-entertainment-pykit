"""_summary_"""

import json
import requests

from utils.logger import logging
from utils.decorators import get, put
from config.constants import API2_URL_HTTPS, API2_USERNAME


class LightRepository:
    """_summary_"""

    def __init__(self) -> None:
        self.__headers = {"hue-application-key": API2_USERNAME}

    @get("/resource/light")
    def get_lights(self, endpoint: str) -> dict:
        """A method for sending a GET request to all lights"""
        response = requests.get(
            url=API2_URL_HTTPS + endpoint,
            headers=self.__headers,
            timeout=1,
            verify=False,
        )

        if response.status_code == requests.codes["ok"]:
            data = response.json()
            logging.info(
                str(response.status_code)
                + ", "
                + response.reason
            )
            return data

        logging.error(
            "status code: "
            + str(response.status_code)
            + "\n"
            + "context: "
            + str(response.content)
        )

    @get("/resource/light/{identification}")
    def get_light(self, endpoint: str) -> dict:
        """A method for sending a GET request to a specific light."""
        response = requests.get(
            url=API2_URL_HTTPS + endpoint,
            headers=self.__headers,
            timeout=1,
            verify=False,
        )

        if response.status_code == requests.codes["ok"]:
            data = response.json()
            logging.info(
                str(response.status_code)
                + ", "
                + response.reason
            )
            return data
        logging.error(
            "status code: "
            + str(response.status_code)
            + "\n"
            + "context: "
            + str(response.content)
        )

    @put("/resource/light/{identification}")
    def put_light(self, endpoint: str, data: dict) -> None:
        """A method for sending a PUT request to a specific light"""
        url = API2_URL_HTTPS + endpoint
        json_data = json.dumps(data)

        response = requests.put(
            url=url, headers=self.__headers, data=json_data, timeout=2, verify=False
        )

        if response.status_code == requests.codes["ok"]:
            logging.info(
                str(response.status_code)
                + ", "
                + response.reason
            )
        else:
            logging.error(
                "status code: "
                + str(response.status_code)
                + "\n"
                + "context: "
                + str(response.content)
            )
