import logging
from ipaddress import IPv4Address

from hue_entertainment_pykit.lowl.clients.http_client import HttpClient
from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.light.light_hue import LightHue
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader


logger = logging.getLogger(__name__)

class LightClient(HttpClient):
    @staticmethod
    def fetch_lights_from_bridge(ip_address: IPv4Address, username: str) -> list[LightHue]:
        logger.info(f"Fetching lights from {ip_address}")
        body, headers = LightClient._send_request(HttpMethodEnum.GET,
                                                  EndpointEnum.LIGHT,
                                                  ip_address,
                                                  RequestHeader(username))

        lights = [LightHue(**data) for data in body]
        logger.info(f"Found {len(lights)} lights")
        return lights
