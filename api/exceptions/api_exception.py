import logging
from typing import Any

import requests


class ApiException(Exception):
    @staticmethod
    def response_status(response: requests.Response):
        msg = f"Response status: {response.status_code, response.reason}"
        logging.error(msg)
        return ApiException(msg)

    @staticmethod
    def api_return_error(data: dict[str, Any]):
        msg = f"Api returned error: {data['error']['description']}"
        logging.error(msg)
        return ApiException(msg)

    @staticmethod
    def invalid_response(data: dict[str, Any]):
        msg = f"Invalid response: {data}"
        logging.error(msg)
        return ApiException(msg)
