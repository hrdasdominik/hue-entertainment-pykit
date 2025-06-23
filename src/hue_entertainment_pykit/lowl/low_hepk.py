import logging
from contextlib import contextmanager
from ipaddress import IPv4Address
from typing import Generator
from uuid import UUID

from hue_entertainment_pykit.lowl.clients.bridge_client import BridgeClient
from hue_entertainment_pykit.lowl.clients.device_client import DeviceClient
from hue_entertainment_pykit.lowl.clients.entertainment_client import EntertainmentClient
from hue_entertainment_pykit.lowl.clients.entertainment_configuration_client import EntertainmentConfigurationClient
from hue_entertainment_pykit.lowl.clients.light_client import LightClient
from hue_entertainment_pykit.lowl.enums.color_space_enum import ColorSpaceEnum
from hue_entertainment_pykit.lowl.enums.log_level_enum import LogLevelEnum
from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import (StreamStopError, FetchLightsError)
from hue_entertainment_pykit.lowl.models.bridge.bridge_combination_hue import BridgeCombinationHue
from hue_entertainment_pykit.lowl.models.device.device_hue import DeviceHue
from hue_entertainment_pykit.lowl.models.entertainment.entertainment_hue import EntertainmentHue
from hue_entertainment_pykit.lowl.models.entertainment_configuration.entertainment_configuration_request import \
    EntertainmentConfigurationRequest
from hue_entertainment_pykit.lowl.models.entertainment_configuration.entertainment_configuration_hue import \
    EntertainmentConfigurationHue
from hue_entertainment_pykit.lowl.models.light.light_base import LightBase
from hue_entertainment_pykit.lowl.models.light.light_hue import LightHue
from hue_entertainment_pykit.lowl.network.dtls_connection import DtlsConnection
from hue_entertainment_pykit.lowl.utils.discovery_util import DiscoveryUtil
from hue_entertainment_pykit.lowl.utils.light_builder_util import LightBuilderUtil
from hue_entertainment_pykit.lowl.utils.logging_util import LoggingUtil
from hue_entertainment_pykit.lowl.utils.streaming_util import StreamingUtil


logger = logging.getLogger(__name__)

class LowHepk:
    @staticmethod
    def discover_bridges(application_name: str = 'dev',
                         ip_addresses: list[IPv4Address] = None) -> list[BridgeCombinationHue]:
        return DiscoveryUtil.discover(application_name, ip_addresses, True)

    @staticmethod
    def fetch_entertainment_configurations(ip_address: IPv4Address,
                                           username: str) -> list[EntertainmentConfigurationHue]:
        return EntertainmentConfigurationClient.fetch_all(ip_address, username)

    @staticmethod
    def create_entertainment_configuration(ip_address: IPv4Address,
                                           username: str,
                                           request: EntertainmentConfigurationRequest) -> UUID:
        return EntertainmentConfigurationClient.create(ip_address,
                                                       username,
                                                       request)

    @staticmethod
    def delete_entertainment_configuration(ip_address: IPv4Address,
                                           username: str,
                                           id: UUID):
        EntertainmentConfigurationClient.delete(ip_address,
                                                username,
                                                id)

    @staticmethod
    def fetch_entertainment_by_id(ip_address: IPv4Address,
                                  username: str,
                                  id: UUID) -> EntertainmentHue:
        return EntertainmentClient.fetch_by_id(ip_address, username, id)

    @staticmethod
    def fetch_entertainments(ip_address: IPv4Address,
                             username: str) -> list[EntertainmentHue]:
        return EntertainmentClient.fetch_all(ip_address, username)

    @staticmethod
    def fetch_device_by_id(ip_address: IPv4Address,
                           username: str,
                           id: UUID) -> DeviceHue:
        return DeviceClient.fetch_by_id(ip_address, username, id)

    @staticmethod
    def fetch_lights_from_bridge(ip_address: IPv4Address,
                                 username: str) -> list[LightHue]:
        return LightClient.fetch_lights_from_bridge(ip_address, username)

    @staticmethod
    def fetch_lights_from_entertainment_configuration(ip_address: IPv4Address,
                                                      username: str,
                                                      entertainment_configuration_id: UUID,
                                                      color_space: ColorSpaceEnum = ColorSpaceEnum.XYB) -> list[LightBase]:
        light_list = LightClient.fetch_lights_from_bridge(ip_address, username)
        ent_conf = EntertainmentConfigurationClient.fetch_by_id(ip_address,
                                                                username,
                                                                entertainment_configuration_id)
        ent_list = EntertainmentClient.fetch_all(ip_address, username)
        bridge = BridgeClient.fetch_bridge(ip_address, username)

        ents_by_rid = {str(ent.id): ent for ent in ent_list}
        lights_by_rid = {str(light.id): light for light in light_list}

        light_base_list: list[LightBase] = []

        for channel in ent_conf.channels:
            if not channel.members:
                raise FetchLightsError(
                    f"Channel {channel.channel_id} has no members in configuration {entertainment_configuration_id}.")

            member = next((m for m in channel.members if getattr(m.service, "rid", None)), None)
            if not member:
                raise FetchLightsError(f"Channel {channel.channel_id} has no member with a renderer reference.")

            ent = ents_by_rid.get(str(member.service.rid))
            if not ent:
                raise FetchLightsError(f"Entertainment entity missing or incomplete for channel {channel.channel_id}.")

            light = lights_by_rid.get(str(ent.renderer_reference.rid))
            if not light:
                raise FetchLightsError(
                    f"No bridge light matches renderer {ent.renderer_reference.rid} on channel {channel.channel_id}.")

            light_base_list.append(
                LightBuilderUtil.build(
                    light, color_space, channel.channel_id, entertainment_configuration_id, bridge.id
                )
            )

        return light_base_list

    @staticmethod
    @contextmanager
    def start_stream(ip_address: IPv4Address,
                     username: str,
                     client_key: str,
                     entertainment_configuration_id: UUID) -> Generator[DtlsConnection, None, None]:
        dtls_connection: DtlsConnection = StreamingUtil.start_stream(ip_address,
                                                                     username,
                                                                     client_key,
                                                                     entertainment_configuration_id)

        try:
            yield dtls_connection
        finally:
            try:
                LowHepk.stop_stream(ip_address, username, entertainment_configuration_id, dtls_connection)
            except StreamStopError as e:
                logger.error(e)
                dtls_connection.close_socket()

    @staticmethod
    def stop_stream(ip_address: IPv4Address,
                    username: str,
                    entertainment_configuration_id: UUID,
                    dtls_connection: DtlsConnection) -> None:
        StreamingUtil.stop_stream(ip_address,
                                  username,
                                  entertainment_configuration_id,
                                  dtls_connection)

    @staticmethod
    def send_message_to_bridge(entertainment_configuration_id: UUID,
                               dtls_connection: DtlsConnection,
                               lights: list[LightBase]) -> None:
        StreamingUtil.send_input(
            entertainment_configuration_id, dtls_connection, lights)

    @staticmethod
    def configure_logs(level: LogLevelEnum = LogLevelEnum.DEBUG,
                       max_file_size: int = 1024 * 1024 * 5,
                       backup_count: int = 3) -> None:
        LoggingUtil.setup_logging(level, max_file_size, backup_count)
