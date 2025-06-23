import logging
from ipaddress import IPv4Address
from uuid import UUID

from hue_entertainment_pykit.lowl.clients.device_client import DeviceClient
from hue_entertainment_pykit.lowl.clients.http_client import HttpClient
from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.device.device_hue import DeviceHue
from hue_entertainment_pykit.lowl.models.entertainment_configuration.entertainment_configuration_hue import \
    EntertainmentConfigurationHue
from hue_entertainment_pykit.lowl.models.entertainment_configuration.entertainment_configuration_request import \
    EntertainmentConfigurationRequest, Position
from hue_entertainment_pykit.lowl.models.request.request_body import RequestBody
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader


logger = logging.getLogger(__name__)

class EntertainmentConfigurationClient(HttpClient):
    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def fetch_all(ip_address: IPv4Address,
                  username: str) -> list[EntertainmentConfigurationHue]:
        logger.info(f"Fetching entertainment configurations")
        body, headers = EntertainmentConfigurationClient._send_request(HttpMethodEnum.GET,
                                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                                       ip_address,
                                                                       RequestHeader(username))
        ent_configs = [EntertainmentConfigurationHue(**data) for data in body]
        logger.info(f"Fetched {len(ent_configs)} entertainment configurations")
        return ent_configs

    @staticmethod
    def fetch_by_id(ip_address: IPv4Address,
                    username: str,
                    id: UUID) -> EntertainmentConfigurationHue:
        logger.info(f"Fetching entertainment configurations by id")
        body, headers = EntertainmentConfigurationClient._send_request(HttpMethodEnum.GET,
                                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                                       ip_address,
                                                                       RequestHeader(username),
                                                                       None,
                                                                       id)
        ent_config = EntertainmentConfigurationHue(**body[0])
        logger.info(f"Fetched entertainment configuration with id {id}")
        return ent_config

    @staticmethod
    def create(ip_address: IPv4Address,
               username: str,
               entertainment_configuration_request: EntertainmentConfigurationRequest) ->\
            UUID:
        logger.info(f'Creating Entertainment Configuration {entertainment_configuration_request.metadata.name}')
        body, headers = EntertainmentConfigurationClient._send_request(HttpMethodEnum.POST,
                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                       ip_address,
                                                       RequestHeader(username),
                                                       RequestBody(entertainment_configuration_request.model_dump(
                                                           mode='json')))
        logger.info(f'Entertainment Configuration {entertainment_configuration_request.metadata.name} created')
        return body[0].get('rid')

    @staticmethod
    def put_lights(ip_address: IPv4Address,
                   username: str,
                   id: UUID,
                   lights_names: dict[UUID, Position]):
        logger.info(f'Putting lights to Entertainment Configuration {id}')
        devices: list[DeviceHue] = DeviceClient.fetch_all(ip_address, username)

        # Build a fast lookup: device.id (which matches the light UUID) -> DeviceHue
        devices_by_id: dict[UUID, DeviceHue] = {device.id: device for device in devices}

        entertainment_service_rids: list[UUID] = []

        for light_id in lights_names:
            device = devices_by_id.get(light_id)
            if device is None:
                logger.warning(f'Light with id {light_id} was not found among available devices')
                continue

            entertainment_id: UUID | None = None
            for service in device.services:
                if service.rtype == 'entertainment':
                    entertainment_id = service.rid
                    break

            if entertainment_id is None:
                raise Exception(f'No entertainment service found for device/light id {light_id}')

            entertainment_service_rids.append(entertainment_id)

        # TODO: Need to refactor
        EntertainmentConfigurationClient._send_request(HttpMethodEnum.PUT,
                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                       ip_address,
                                                       RequestHeader(username),
                                                       RequestBody(entertainment_service_rids),
                                                       id)
        logger.info(
            f'Entertainment Configuration {id} put lights {list(lights_names)} '
            f'-> entertainment services {entertainment_service_rids}'
        )


    @staticmethod
    def delete(ip_address: IPv4Address,
               username: str,
               id: UUID):
        logger.info(f'Deleting Entertainment Configuration {id}')
        EntertainmentConfigurationClient._send_request(HttpMethodEnum.DELETE,
                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                       ip_address,
                                                       RequestHeader(username),
                                                       RequestBody({'query_id': id}))
        logger.info(f'Entertainment Configuration {id} deleted')

    @staticmethod
    def put_stream_to_active(ip_address: IPv4Address,
                             username: str,
                             entertainment_configuration_id: UUID) -> None:
        logger.info(f'Putting stream to active entertainment configuration: {entertainment_configuration_id}')
        EntertainmentConfigurationClient._send_request(HttpMethodEnum.PUT,
                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                       ip_address,
                                                       RequestHeader(username),
                                                       RequestBody({
                                                           'query_id': entertainment_configuration_id,
                                                           'action': 'start'
                                                       }))
        logger.info(
            f'Stream successfully put to active entertainment configuration: {entertainment_configuration_id}')

    @staticmethod
    def put_stream_to_inactive(ip_address: IPv4Address,
                               username: str,
                               entertainment_configuration_id: UUID) -> None:
        logger.info(f'Putting stream to inactive entertainment configuration: {entertainment_configuration_id}')
        EntertainmentConfigurationClient._send_request(HttpMethodEnum.PUT,
                                                       EndpointEnum.ENTERTAINMENT_CONFIGURATION,
                                                       ip_address,
                                                       RequestHeader(username),
                                                       RequestBody({
                                                           'query_id': entertainment_configuration_id,
                                                           'action': 'stop'
                                                       }))
        logger.info(
            f'Stream successfully put to inactive entertainment configuration: {entertainment_configuration_id}')
