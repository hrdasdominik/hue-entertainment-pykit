import logging
from ipaddress import IPv4Address
from uuid import UUID

from hue_entertainment_pykit.lowl.clients.http_client import HttpClient
from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.entertainment.entertainment_hue import EntertainmentHue
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader


logger = logging.getLogger(__name__)

class EntertainmentClient(HttpClient):
    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def fetch_all(ip_address: IPv4Address, username: str) -> list[EntertainmentHue]:
        logger.info(f'Fetching entertainment hue for {ip_address}')
        body, headers = EntertainmentClient._send_request(HttpMethodEnum.GET,
                                                          EndpointEnum.ENTERTAINMENT,
                                                          ip_address,
                                                          RequestHeader(username))

        results = []
        for data in body:
            if 'renderer_reference' in data.keys():
                results.append(EntertainmentHue(**data))
        logger.info(f'Fetched {len(results)} Entertainments')
        return results

    @staticmethod
    def fetch_by_id(ip_address: IPv4Address, username: str, id: UUID) -> EntertainmentHue:
        logger.info(f'Fetching entertainment hue for {id}')
        body, headers = EntertainmentClient._send_request(HttpMethodEnum.GET,
                                                          EndpointEnum.ENTERTAINMENT,
                                                          ip_address,
                                                          RequestHeader(username),
                                                          None,
                                                          id)

        entertainment = EntertainmentHue(**body[0])
        logger.info(f'Fetched entertainment hue for {id}')
        return entertainment