import logging
from ipaddress import IPv4Address
from socket import error as socket_error
from typing import Sequence
from uuid import UUID

from hue_entertainment_pykit.lowl.clients.entertainment_configuration_client import EntertainmentConfigurationClient
from hue_entertainment_pykit.lowl.enums.color_space_enum import ColorSpaceEnum
from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import EncodingLightDataError, StreamStartError
from hue_entertainment_pykit.lowl.models.light.light_base import LightBase
from hue_entertainment_pykit.lowl.models.light.light_rgb import LightRGB
from hue_entertainment_pykit.lowl.models.light.light_xyb import LightXYB
from hue_entertainment_pykit.lowl.network.dtls_connection import DtlsConnection
from hue_entertainment_pykit.lowl.utils.streaming_message_builder_util import StreamingMessageBuilderUtil


logger = logging.getLogger(__name__)

class StreamingUtil:
    """
    Manages streaming color data to Philips Hue lights via a DTLS connection.

    This service handles the setup and maintenance of DTLS connections and transmits color information to lights.
    It includes methods for starting/stopping the stream, setting the color space, and processing color input.

    Attributes:
        _KEEP_ALIVE_INTERVAL (float): Interval for sending keep-alive messages.
    """

    _KEEP_ALIVE_INTERVAL = 9.5

    def __new__(cls, *args, **kwargs):
        raise TypeError('This class cannot be instantiated.')

    @staticmethod
    def get_keep_alive_interval() -> float:
        return StreamingUtil._KEEP_ALIVE_INTERVAL

    @staticmethod
    def start_stream(ip_address: IPv4Address,
                     username: str,
                     client_key: str,
                     entertainment_configuration_id: UUID) -> DtlsConnection:
        """Starts the streaming service.

        This method initiates the streaming process by setting up the DTLS connection and
        starting the threads responsible for keeping the connection alive and monitoring user input.
        It also notifies the entertainment configuration repository to start the streaming session.
        """
        logger.info('Starting streaming session')

        EntertainmentConfigurationClient.put_stream_to_active(ip_address,
                                                              username,
                                                              entertainment_configuration_id)

        dtls_connection: DtlsConnection = DtlsConnection(ip_address, username, client_key)

        try:
            dtls_connection.create_dtls_socket()
        except socket_error:
            EntertainmentConfigurationClient.put_stream_to_inactive(ip_address,
                                                                    username,
                                                                    entertainment_configuration_id)
            logger.error('Failed to create DTLS socket')
            raise StreamStartError('Failed to create DTLS socket')

        try:
            dtls_connection.do_handshake()
        except socket_error:
            EntertainmentConfigurationClient.put_stream_to_inactive(ip_address,
                                                                    username,
                                                                    entertainment_configuration_id)
            logger.error('Failed to handshake DTLS socket')
            raise StreamStartError('Failed to handshake DTLS socket')

        logger.info('Streaming session started')
        return dtls_connection

    @staticmethod
    def stop_stream(ip_address: IPv4Address,
                    hue_application_key: str,
                    entertainment_configuration_id: UUID,
                    dtls_connection: DtlsConnection) -> None:
        """Stops the streaming service, ensuring that all resources are properly released.

        This method stops the streaming process by terminating the connection threads and closing the DTLS socket.
        It also updates the entertainment configuration repository to indicate that the streaming session has stopped.
        """

        logger.info('Stopping streaming session')

        EntertainmentConfigurationClient.put_stream_to_inactive(ip_address,
                                                                hue_application_key,
                                                                entertainment_configuration_id)

        logger.debug('DTLS connection closing.')
        dtls_connection.close_socket()
        logger.debug('DTLS connection closed successfully.')

        logger.info('Stream stopped successfully')

    @staticmethod
    def send_input(entertainment_configuration_id: UUID,
                   dtls_connection: DtlsConnection,
                   lights: Sequence[LightBase]) -> None:
        """

        """

        logger.debug('Processing user input: %s', lights)

        if isinstance(lights[0], LightRGB):
            color_space = ColorSpaceEnum.RGB
        elif isinstance(lights[0], LightXYB):
            color_space = ColorSpaceEnum.XYB
        else:
            raise Exception('Invalid lights type')

        try:
            channel_data_list = [
                StreamingMessageBuilderUtil.encode_light_data(light_setting)
                for light_setting in lights
            ]
        except Exception as e:
            raise EncodingLightDataError('Failed to encode light data for the bridge.') from e

        try:
            message: bytes = StreamingMessageBuilderUtil.build(entertainment_configuration_id,
                                                               color_space,
                                                               channel_data_list)
            logger.debug('Sending message: %s', message)
            dtls_connection.send_message(message)
        except socket_error as e:
            logger.error('Error sending message: %s', e)
