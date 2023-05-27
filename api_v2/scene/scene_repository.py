"""_summary_"""

import requests

from utils.decorators_v2 import get, put
from config.constants import API2_URL_HTTPS, API2_USERNAME
from exceptions.philips_api_exception import PhilipsApiError
from api_v2.scene.scene_model import SceneModel


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
            return data
        raise PhilipsApiError(
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
            return data
        raise PhilipsApiError(
            "status code: "
            + str(response.status_code)
            + "\n"
            + "context: "
            + str(response.content)
        )

    @put("/resource/scene/{identification}")
    def put(self, endpoint: str, identification: str, scene: SceneModel) -> None:
        """A method for sending a PUT request to a specific scene"""
        url = API2_URL_HTTPS + endpoint.format(identification)
        response = requests.put(url=url, headers=self.__headers, data=scene, timeout=2)

        if response.status_code == requests.codes["ok"]:
            data = response.json()
            print(data)
        else:
            raise PhilipsApiError(
                "status code: "
                + str(response.status_code)
                + "\n"
                + "context: "
                + str(response.content)
            )
