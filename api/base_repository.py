import json
import logging
import os
from typing import Any

import requests

from api.bridge.bridge import Bridge
from api.exceptions.api_exception import ApiException


class BaseRepository:
    def __init__(self, bridge: Bridge):
        self._bridge: Bridge = bridge

        self._default_url: str = f"https://{self._bridge.get_ip_address()}/clip/v2/"
        self._username: str = ""
        self._client_key: str = ""
        self._headers: dict[str, str] = {
            "hue-application-key": self._username}

    def get_default_url(self):
        return self._default_url

    def get_username(self):
        return self._username

    def get_client_key(self):
        return self._client_key

    def get_headers(self):
        return self._headers

    def generate_key(self):
        logging.debug("Started 'generate_key'")

        if os.path.exists("logs/auth.txt"):
            with open("logs/auth.txt", "r") as doc:
                info: dict = json.loads(doc.readline().strip())

                self._username = info["username"]
                self._client_key = info["clientkey"]
                self._headers["hue-application-key"] = self._username

                logging.debug("Successfully loaded key")
                return self

        url: str = f"https://192.168.100.11/api"

        body: dict[str, Any] = {
            "devicetype": "musical_lights#1",
            "generateclientkey": True
        }
        response = requests.request("POST", url=url, json=body, verify=False)

        if response.status_code == 200:
            data: dict[str, Any] = response.json()[0]

            logging.debug(f"json: {data}")

            if "error" in data.keys():
                raise ApiException.api_return_error(data)
            elif "success" in data.keys():
                self._username = data["success"]["username"]
                self._client_key = data["success"]["clientkey"]
                self._headers["hue-application-key"] = self._username

                with open("logs/auth.txt", "w") as doc:
                    doc.write(json.dumps({
                        "username": self._username,
                        "clientkey": self._client_key
                    }))

                logging.debug("Successfully generated key")
            else:
                raise ApiException.invalid_response(data)
        else:
            raise ApiException.response_status(response)

        return self
