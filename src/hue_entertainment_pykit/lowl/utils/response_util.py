import json
import logging
from http import HTTPStatus

from requests import Response
from requests.structures import CaseInsensitiveDict

from hue_entertainment_pykit.lowl.exceptions.link_button_not_pressed_exception import LinkButtonNotPressedError
from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import BridgeApiError


logger = logging.getLogger(__name__)

class ResponseUtil:
    @staticmethod
    def unwrap(response: Response) -> tuple[dict, CaseInsensitiveDict[str]]:
        response_headers: CaseInsensitiveDict[str] = response.headers
        response_data: dict = response.json()

        logger.trace("Response-headers: %s", response_headers)
        logger.trace("Response-body: %s", response_data)

        if response.status_code < HTTPStatus.BAD_REQUEST.value:
            if "error" in response_data:
                if response_data["error"]["type"] == 101:
                    error_str: str = "Hue Bridge link button not pressed."
                    logger.error(error_str)
                    raise LinkButtonNotPressedError(error_str)
                else:
                    error_str: str = f"Bridge communication error: {response_data['error']['description']}"
                    logger.error(error_str)
                    raise BridgeApiError(error_str)

            if 'data' in response_data:
                return response_data["data"], response_headers

            if 'apiversion' in response_data:
                return response_data, response_headers

            if isinstance(response_data, list):
                if 'success' in response_data[0]:
                    return response_data[0]['success'], response_headers
                elif 'error' in response_data[0]:
                    logger.error(response_data[0]['error']['description'])
                    if response_data[0]['error']['description'] == "link button not pressed":
                        raise LinkButtonNotPressedError(response_data[0]['error']['description'])
                    raise BridgeApiError(response_data[0]['error']['description'])

            raise BridgeApiError(
                'Response data has changed, please report issue to '
                'https://github.com/hrdasdominik/hue-entertainment-pykit/issues')

        else:
            error_str: str = f'Response status: {response.status_code}, {response.reason}, '

            decoded = response.text.encode('utf-8')
            parsed_json = json.loads(decoded)
            errors = parsed_json.get('errors')
            if errors:
                error = errors[0]
                error_str += error.get('description')

            logger.debug(parsed_json)
            logger.error(error_str)
            raise BridgeApiError(error_str)
