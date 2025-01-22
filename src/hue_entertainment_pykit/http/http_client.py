import logging
from typing import Any

import requests
from requests import Response

from src.hue_entertainment_pykit.http.http_exception import HttpException
from src.hue_entertainment_pykit.http.http_method_enum import HttpMethodEnum
from src.hue_entertainment_pykit.http.http_status_code_enum import HttpStatusCodeEnum
from src.hue_entertainment_pykit.utils.endpoint_enum import EndpointEnum


class HttpClient:
    def __init__(self):
        self._base_url: str = ""
        self._headers: dict[str, str] = {"Content-Type": "application/json"}

    def get_base_url(self) -> str:
        return self._base_url

    def get_headers(self) -> dict[str, str]:
        return self._headers

    def set_base_url(self, ip_address: str) -> None:
        self._base_url = "https://" + ip_address

    def add_headers(self, key: str, value: Any):
        self._headers[key] = value

    def del_headers(self, key: str):
        del self._headers[key]

    def make_request(self, http_method: HttpMethodEnum, endpoint: EndpointEnum, **kwargs) -> Response:
        """
        Makes an HTTP request to the Philips Hue Bridge.

        Parameters:
            http_method (HttpMethodEnum): The HTTP method to use for the request.
            endpoint (str): The API endpoint to target.
            **kwargs: Additional keyword arguments passed to the requests.request method,
            such as http_request data or custom headers.

        Returns:
            Response: The response object from the Hue Bridge.

        Raises:
            ValueError: If the base URL is not set.
            BridgeException: If the response status code indicates an error.
        """

        if self._base_url == "":
            raise ValueError("Base url is not set.")

        url = f"{self._base_url}{endpoint.value}"
        logging.debug(f"URL set to: {url}")

        identification = kwargs.pop("identification", None)
        if identification:
            url = f"{url}/{identification}"
            logging.debug(f"URL: {url} updated with ID: {identification}")

        rid = kwargs.pop("rid", None)
        if rid:
            url = f"{url}/{rid}"
            logging.debug(f"URL set to: {url} updated with RID: {rid}")

        logging.debug(f"headers: {self._headers}")

        body = kwargs.pop("json", None)
        logging.debug(f"body: {body}")

        response = requests.request(
            http_method.value, url, headers=self._headers, verify=False, timeout=5, json=body
        )

        logging.debug(f"response-headers: {response.headers}")
        logging.debug(f"response-body: {response.json()}")

        if response.status_code != HttpStatusCodeEnum.OK.value:
            raise HttpException(
                f"Response status: {response.status_code}, {response.reason}"
            )
        return response