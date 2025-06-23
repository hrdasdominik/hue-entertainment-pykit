import logging
from ipaddress import IPv4Address
from typing import Optional
from uuid import UUID

from hue_entertainment_pykit.lowl.clients.http_client import HttpClient
from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.bridge.bridge_api_hue import BridgeApiHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_config_hue import BridgeConfigHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_device_hue import BridgeDeviceHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_hue import BridgeHue
from hue_entertainment_pykit.lowl.models.request.request_body import RequestBody
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader


logger = logging.getLogger(__name__)

class BridgeClient(HttpClient):
    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def generate_api_keys(ip_address: IPv4Address, application_name: Optional[str] = 'dev') -> BridgeApiHue:
        logger.info(f"Generating API keys for hep#{application_name} {str(ip_address)}")
        body, headers = BridgeClient._send_request(HttpMethodEnum.POST,
                                                   EndpointEnum.API,
                                                   ip_address,
                                                   body=RequestBody(
                                                       {
                                                           "devicetype": f"hep#{application_name}",
                                                           "generateclientkey": True
                                                       }))
        api_key = BridgeApiHue(**body)
        logger.info(f"Generated successfully API key: {api_key}")
        return api_key

    @staticmethod
    def fetch_bridge(ip_address: IPv4Address, username: str) -> BridgeHue:
        logger.info(f"Fetching bridge for {str(ip_address)}")
        body, headers = BridgeClient._send_request(HttpMethodEnum.GET,
                                                   EndpointEnum.BRIDGE,
                                                   ip_address,
                                                   header=RequestHeader(username))
        bridge = BridgeHue(**body[0])
        logger.info(f"Fetched bridge ({str(ip_address)}) successfully")
        return bridge

    @staticmethod
    def fetch_config(ip_address: IPv4Address, username: str) -> BridgeConfigHue:
        logger.info(f"Fetching bridge configuration for {str(ip_address)}")
        body, headers = BridgeClient._send_request(HttpMethodEnum.GET,
                                                   EndpointEnum.CONFIG,
                                                   ip_address,
                                                   header=RequestHeader(username))
        bridge_config = BridgeConfigHue(**body)
        logger.info(f"Fetched bridge configuration ({str(ip_address)}) successfully")
        return bridge_config

    @staticmethod
    def fetch_device(ip_address: IPv4Address, username: str, id: UUID) -> BridgeDeviceHue:
        logger.info(f'Fetching device for {id}')
        body, headers = BridgeClient._send_request(HttpMethodEnum.GET,
                                                   EndpointEnum.DEVICE,
                                                   ip_address,
                                                   RequestHeader(username),
                                                   None,
                                                   id)
        bridge_device = BridgeDeviceHue(**body[0])
        logger.info(f"Fetched device {id} successfully")
        return bridge_device
