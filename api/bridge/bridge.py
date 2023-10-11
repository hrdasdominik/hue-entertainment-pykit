import logging
import os
import requests
import json

from requests import Response

from api.exceptions.bridge_exception import BridgeException
from api.utils.decorators import singleton


@singleton
class Bridge:
    def __init__(self):
        self._id: str = ""
        self._internal_ip_address: str = ""
        self._port: int = 0

    def get_ip_address(self) -> str:
        return self._internal_ip_address

    def get_port(self):
        return self._port

    def get_ip_with_broker(self):
        logging.debug(f"Started {self.__class__.__name__}.get_ip_with_broker")
        if os.path.exists("logs/info.txt"):
            with open("logs/info.txt", "r") as doc:
                info: dict = json.loads(doc.readline().strip())

                self._id = info["id"]
                self._internal_ip_address = info["internalipaddress"]
                self._port = info["port"]

                logging.debug("Successfully loaded broker info")
                return self

        response: Response = requests.get("https://discovery.meethue.com/")

        if response.status_code == 200:
            data = json.loads(response.text)
            self._id = data[0]["id"]
            self._internal_ip_address = data[0]["internalipaddress"]
            self._port = data[0]["port"]

            with open("logs/info.txt", "w") as doc:
                doc.write(json.dumps({
                    "id": self._id,
                    "internalipaddress": self._internal_ip_address,
                    "port": self._port
                }))
        else:
            raise BridgeException.status_respons(response)

        return self
