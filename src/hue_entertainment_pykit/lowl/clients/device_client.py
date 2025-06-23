import logging
from ipaddress import IPv4Address
from uuid import UUID

from hue_entertainment_pykit.lowl.clients.http_client import HttpClient
from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.device.device_hue import DeviceHue
from hue_entertainment_pykit.lowl.models.request.request_body import RequestBody
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader


logger = logging.getLogger(__name__)

class DeviceClient(HttpClient):
    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def fetch_all(ip_address: IPv4Address,
                  username: str):
        logger.info(f'Fetching all devices from {ip_address}')
        body, headers = DeviceClient._send_request(HttpMethodEnum.GET,
                                                   EndpointEnum.DEVICE,
                                                   ip_address,
                                                   RequestHeader(username))
        devices = [DeviceHue(**data) for data in body]
        logger.info(f'Found {len(devices)} devices')
        return devices

    @staticmethod
    def fetch_by_id(ip_address: IPv4Address,
                    username: str,
                    id: UUID):
        logger.info(f"Fetching device by id: {id}")
        body, headers = DeviceClient._send_request(HttpMethodEnum.GET,
                                                   EndpointEnum.DEVICE,
                                                   ip_address,
                                                   RequestHeader(username),
                                                   None,
                                                   id)
        device = DeviceHue(**body[0])
        logger.info(f"Fetched device by id: {id}")
        return device
