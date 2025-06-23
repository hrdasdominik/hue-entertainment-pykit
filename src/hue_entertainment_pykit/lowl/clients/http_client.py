import logging
from abc import ABC
from ipaddress import IPv4Address
from typing import Optional, Any
from uuid import UUID

import requests
from requests import Response
from requests.structures import CaseInsensitiveDict

from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.request.request_body import RequestBody
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader
from hue_entertainment_pykit.lowl.utils.response_util import ResponseUtil


logger = logging.getLogger(__name__)

class HttpClient(ABC):
    """
    Methods:
        _send_request: Sends HTTP requests to the Bridge and handles responses.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def _send_request(method: HttpMethodEnum,
                      endpoint: EndpointEnum,
                      ip_address: IPv4Address,
                      header: Optional[RequestHeader] = None,
                      body: Optional[RequestBody] = None,
                      resource_id: Optional[UUID] = None
                      ):
        """
        Makes an HTTP request to the Philips Hue Bridge.

        Parameters:
            method (HttpMethodEnum): The HTTP method to use for the request.
            endpoint (EndpointEnum): The API endpoint to target.
            ip_address (IPv4Address): The IP address to target.
            header (Optional[RequestHeader]): The HTTP headers to use.
            body (Optional[RequestBody]): The HTTP body to use.

        Returns:
            Response: The response object from the Hue Bridge.

        Raises:
            ValueError: If the base URL is not set.
            BridgeException: If the response status code indicates an error.
        """
        parts = [f"https://{str(ip_address)}", endpoint.value]

        if resource_id:
            parts.append(str(id))

        url = "/".join(parts)

        headers = header.get_data() if header else None
        if headers:
            logger.trace("Sending headers: %s", headers)

        json_dict = body.get_data() if body else None
        if json_dict:
            logger.trace("Sending body: %s", json_dict)

        response: Response = requests.request(method.value, url, headers=headers, verify=False, timeout=5,
                                              json=json_dict)

        return ResponseUtil.unwrap(response)
