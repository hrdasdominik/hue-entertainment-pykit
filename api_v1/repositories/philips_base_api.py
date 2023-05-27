"""_summary_"""

import json
from typing import List
import requests

from requests.exceptions import ConnectTimeout

from config.constants import URL_HTTP
from exceptions.philips_api_exception import PhilipsApiError
from models.philips_base_model import PhilipsBaseModel
from utils.logger import logging


class PhilipsBaseApi:
    """_summary_"""

    def __init__(self) -> None:
        self.__base_url = URL_HTTP
        self.__timeout = 4

    def get_data(self, endpoint: str, identification: int = None) -> List[PhilipsBaseModel]:
        """_summary_

        Args:
            endpoint (str): _description_
            identification (int, optional): _description_. Defaults to None.

        Returns:
            List[PhilipsBaseModel]: _description_
        """
        if identification is None:
            try:
                response = requests.get(
                    url=self.__base_url + endpoint, timeout=self.__timeout
                )
            except ConnectTimeout:
                logging.error(ConnectTimeout(f"Timeout on request GET {endpoint}"))

        else:
            response = requests.get(
                url=self.__base_url + endpoint.format(identification), timeout=self.__timeout
            )

        response_json = response.json()

        if response.status_code == requests.codes["ok"]:
            return self.populate_object(response_json)
        else:
            logging.error(
                PhilipsApiError(f"Error {response.status_code}: {response.text}")
            )

    def send_data(self, endpoint: str, model: PhilipsBaseModel) -> None:
        """_summary_

        Args:
            endpoint (str): _description_
            model (PhilipsBaseModel): _description_

        Raises:
            ValueError: _description_
        """
        if model is None:
            raise ValueError("Model object is None")

        data = self.serialize_object(model)

        logging.info("PACKET REQUEST:", data)

        response = requests.put(self.get_base_url() + endpoint, data, timeout=10)

        if response.status_code == requests.codes["ok"] and "error" not in str(
            response.content
        ):
            logging.info(
                str(response.status_code)
                + ", "
                + response.reason
                + " | "
                + str(response.content)
            )
        elif response.status_code != requests.codes["ok"]:
            logging.error(
                str(response.status_code)
                + ", "
                + response.reason
                + " | "
                + str(response.content)
            )
        else:
            logging.error(str(response.text))

    def serialize_object(self, model: PhilipsBaseModel) -> json:
        """_summary_

        Args:
            model (PhilipsBaseModel): _description_

        Returns:
            json: _description_
        """
        data = model.__dict__
        return json.dumps(data)

    def get_base_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.__base_url

    def populate_object(self, response_json) -> list:
        """_summary_

        Args:
            response_json (_type_): _description_

        Raises:
            PhilipsApiError: _description_

        Returns:
            list: _description_
        """
        raise PhilipsApiError("This method is not allowed!")
