import logging

import requests


class BridgeException(Exception):
    @staticmethod
    def status_respons(response: requests.Response):
        msg = f"Response status: {response.status_code, response.reason}"
        logging.error(msg)
        return BridgeException(msg)
