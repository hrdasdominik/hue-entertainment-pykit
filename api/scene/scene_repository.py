"""_summary_"""

import json
import requests

from utils.decorators import get, put, post, delete
from utils.logger import logging
from config.constants import API2_URL_HTTPS, API2_USERNAME


class SceneRepository:
    """_summary_"""

    def __init__(self) -> None:
        self.__headers = {"hue-application-key": API2_USERNAME}

    @get("/resource/scene")
    def get_scenes(self, endpoint: str) -> dict:
        """A method for sending a GET request to all scenes"""
        response = requests.get(
            url=API2_URL_HTTPS + endpoint,
            headers=self.__headers,
            timeout=1,
            verify=False,
        )

        if response.status_code == requests.codes["ok"]:
            data = response.json()
            logging.info(str(response.status_code) + ", " + response.reason)
            return data

        logging.error(
            "status code: "
            + str(response.status_code)
            + "\n"
            + "context: "
            + str(response.content)
        )

    @post("/resource/scene")
    def post_scene(self, endpoint: str) -> None:
        """A method for sending POST request for a specific scene"""
        response = requests.post(
            url=API2_URL_HTTPS + endpoint,
            headers=self.__headers,
            timeout=1,
            verify=False,
        )

        if response.status_code == requests.codes["ok"]:
            logging.info(str(response.status_code) + ", " + response.reason)

        logging.error(
            "status code: "
            + str(response.status_code)
            + "\n"
            + "context: "
            + str(response.content)
        )

    @get("/resource/scene/{identification}")
    def get_scene(self, endpoint: str) -> dict:
        """A method for sending a GET request to a specific scene"""
        response = requests.get(
            url=API2_URL_HTTPS + endpoint,
            headers=self.__headers,
            timeout=1,
            verify=False,
        )

        if response.status_code == requests.codes["ok"]:
            data = response.json()
            logging.info(str(response.status_code) + ", " + response.reason)
            return data

        logging.error(
            "status code: "
            + str(response.status_code)
            + "\n"
            + "context: "
            + str(response.content)
        )

    @put("/resource/scene/{identification}")
    def put_scene(self, endpoint: str, data: dict) -> None:
        """A method for sending a PUT request to a specific scene"""
        url = API2_URL_HTTPS + endpoint
        json_data = json.dumps(data)

        response = requests.put(
            url=url, headers=self.__headers, data=json_data, timeout=2, verify=False
        )

        if response.status_code == requests.codes["ok"]:
            logging.info(str(response.status_code) + ", " + response.reason)
        else:
            logging.error(
                "status code: "
                + str(response.status_code)
                + "\n"
                + "context: "
                + str(response.content)
            )

    @delete("/resource/scene/{identification}")
    def delete_scene(self, endpoint: str, data: dict) -> None:
        """A method for sending DELETE request to a specfic scene"""
        url = API2_URL_HTTPS + endpoint
        json_data = json.dumps(data)

        response = requests.delete(
            url=url, headers=self.__headers, data=json_data, timeout=2, verify=False
        )

        if response.status_code == requests.codes["ok"]:
            logging.info(str(response.status_code) + ", " + response.reason)
        else:
            logging.error(
                "status code: "
                + str(response.status_code)
                + "\n"
                + "context: "
                + str(response.content)
            )
