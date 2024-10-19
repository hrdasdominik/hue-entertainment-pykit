"""
Contains the StreamingService class for managing the streaming of color data to Philips Hue lights.
This class is responsible for the DTLS connection setup and maintenance, and facilitates color data
transmission to lights in a Philips Hue Entertainment setup.
"""

import logging
import queue
import struct
import threading
import time
from socket import error as SocketError
from typing import Union, Optional

from src.hue_entertainment_pykit.bridge.entertainment_configuration_repository import (
    EntertainmentConfigurationRepository,
)
from src.hue_entertainment_pykit.models.entertainment_configuration import (
    EntertainmentConfiguration,
)
from src.hue_entertainment_pykit.models.payload import Payload
from src.hue_entertainment_pykit.network.dtls import Dtls
from src.hue_entertainment_pykit.utils.converter import Converter

from src.hue_entertainment_pykit.models.light import LightBase

from src.hue_entertainment_pykit.exceptions.connection_exception import ConnectionException


# pylint: disable=too-many-instance-attributes
class StreamingService:
    """
    Manages streaming color data to Philips Hue lights via a DTLS connection.

    This service handles the setup and maintenance of DTLS connections and transmits color information to lights.
    It includes methods for starting/stopping the stream, setting the color space, and processing color input.

    Attributes:
        _KEEP_ALIVE_INTERVAL (float): Interval for sending keep-alive messages.
        _DEFAULT_CHANNEL_VALUE (bytes): Default value for initializing streaming messages.
    """

    _KEEP_ALIVE_INTERVAL = 9.5
    _DEFAULT_CHANNEL_VALUE = struct.pack(">B", 0x00)
    _COLOR_SPACE = ["rgb", "xyb"]

    def __init__(
            self,
            entertainment_configuration: EntertainmentConfiguration,
            entertainment_configuration_repository: EntertainmentConfigurationRepository,
            dtls_service: Dtls,
    ):
        """
        Initializes the StreamingService with the necessary configuration and services.

        Args:
            entertainment_configuration (EntertainmentConfiguration): Configuration for the entertainment setup.
            entertainment_configuration_repository (EntertainmentConfigurationRepository): Repository for
            managing entertainment configurations.
            dtls_service (Dtls): Service for managing DTLS (Datagram Transport Layer Security) connections.
        """

        self._entertainment_configuration = entertainment_configuration
        self._entertainment_configuration_repository = (
            entertainment_configuration_repository
        )
        self._dtls_service = dtls_service

        self._protocol_name = "HueStream".encode("utf-8")
        self._version = struct.pack(">BB", 0x02, 0x00)
        self._sequence_id = struct.pack(">B", 0x07)
        self._reserved = b"\x00\x00"
        self._color_space = self._DEFAULT_CHANNEL_VALUE
        self._reserved2 = b"\x00"
        self._entertainment_id = self._entertainment_configuration.id.encode("utf-8")

        self._channel_data = b""
        self._last_message = self._init_message()
        self._is_connection_alive = False

        self._input_queue = queue.Queue()
        self._connection_thread = threading.Thread(target=self._keep_connection_alive)
        self._processing_thread = threading.Thread(target=self._watch_user_input)

        self._reconnect_attempts = 0
        self._reconnect_lock = threading.Lock()

    def is_stream_active(self) -> bool:
        """Check if the streaming service is currently active.

        Returns:
            bool: True if the stream is active, False otherwise.
        """

        return self._is_connection_alive

    def set_color_space(self, value: str):
        """Set the color space for the streaming service.

        Args:
            value (str): The color space value to set ('rgb' or 'xyb').

        Raises:
            ValueError: If an invalid color space is provided.
        """

        if value.lower() in self._COLOR_SPACE:
            self._color_space = struct.pack(">B", 0x00 if value == "rgb" else 0x01)
        else:
            raise ValueError(f"Invalid color space '{value}'. Use 'rgb' or 'xyb'.")

    def start_stream(self):
        """Starts the streaming service.

        This method initiates the streaming process by setting up the DTLS connection and
        starting the threads responsible for keeping the connection alive and monitoring user input.
        It also notifies the entertainment configuration repository to start the streaming session.
        """

        payload = (
            Payload()
            .set_key_and_or_value("id", self._entertainment_configuration.id)
            .set_key_and_or_value("action", "start")
        )
        self._entertainment_configuration_repository.put_configuration(payload)

        try:
            self._dtls_service.do_handshake()
        except Exception as e:
            logging.exception(f"Error during handshake for DTLS connection.\n error: {e}")
            self._dtls_service.close_socket()
            stop_payload = Payload()
            stop_payload.set_key_and_or_value("id", self._entertainment_configuration.id)
            stop_payload.set_key_and_or_value("action", "stop")
            self._entertainment_configuration_repository.put_configuration(stop_payload)
            raise ConnectionException("Failed DTLS handshake cause of ", e)

        self._is_connection_alive = True

        self._connection_thread.start()
        self._processing_thread.start()

    def stop_stream(self):
        """Stops the streaming service, ensuring that all resources are properly released.

        This method stops the streaming process by terminating the connection threads and closing the DTLS socket.
        It also updates the entertainment configuration repository to indicate that the streaming session has stopped.
        """

        logging.info("Stopping streaming")
        if self._dtls_service.get_socket() and self._is_connection_alive:
            self._is_connection_alive = False

            logging.info("Stopping DTLS socket")
            self._connection_thread.join(timeout=10)
            self._processing_thread.join(timeout=10)

            if self._connection_thread.is_alive() or self._processing_thread.is_alive():
                logging.warning("One or more threads did not terminate as expected.")

            self._dtls_service.close_socket()
            logging.info("DTLS socket closed successfully")

            payload = (
                Payload()
                .set_key_and_or_value("id", self._entertainment_configuration.id)
                .set_key_and_or_value("action", "stop")
            )
            self._entertainment_configuration_repository.put_configuration(payload)
            logging.info("Stream stopped successfully")
        else:
            raise SocketError(
                "Unable to stop stream: DTLS socket is not available or stream is not active."
            )

    def set_input(
            self,
            light_list: list[LightBase],
            # transition_time: Optional[float] = 0.0
    ):
        """Sets the user input for processing.

        Args:
            light_list (list[LightBase]): The user input data, either
            in RGB8 or XYB format, along with a light identifier. The input should be a tuple containing either
            three integer values (RGB) or three float values (XYB) followed by the light identifier as a string.
            transition_time (float)
        """
        processed_user_input = []
        for light in light_list:
            rgb16_and_light_id: tuple[int, int, int, int] = Converter.xyb_or_rgb8_to_rgb16(
                light.get_colors()) + (light.get_id(),)
            processed_user_input.append(rgb16_and_light_id)

        self._input_queue.put(processed_user_input)

    def _build_message(self, channel_data_list):
        """Constructs a message for streaming with the given channel data.

        Args:
            channel_data_list (list[bytes]): The channel data to be included in the message. It includes various
            parameters such as protocol name, version, sequence ID, reserved bytes, color space, and entertainment ID,
            concatenated with the actual channel data.

        Returns:
            bytes: The constructed message, ready to be sent over the network.
        """

        message = (
                self._protocol_name
                + self._version
                + self._sequence_id
                + self._reserved
                + self._color_space
                + self._reserved2
                + self._entertainment_id
        )

        for channel_data in channel_data_list:
            message += channel_data

        return message

    def _init_message(self) -> bytes:
        """Initialize the streaming message with default channel data.

        Returns:
            bytes: The initialized message.
        """

        x, y, b = Converter.xyb_or_rgb8_to_rgb16((0.0, 0.0, 0.0))

        self._channel_data = self._DEFAULT_CHANNEL_VALUE
        self._channel_data += struct.pack(">HHH", x, y, b)

        return self._build_message([self._channel_data])

    def _keep_connection_alive(self):
        """Keeps the DTLS connection alive by sending messages at regular intervals.

        This method runs in a separate thread and is responsible for maintaining the DTLS connection.
        It periodically sends the last known message to keep the connection active.
        If the connection is lost, it attempts to reconnect.
        """

        while self._is_connection_alive:
            try:
                self._dtls_service.get_socket().sendto(
                    self._last_message, self._dtls_service.get_server_address()
                )
            except SocketError as e:
                logging.error("Connection lost: %s", e)
                if self._is_connection_alive:
                    logging.info("Attempting to reconnect...")
                    self._attempt_reconnect()
            time.sleep(self._KEEP_ALIVE_INTERVAL)

    def _watch_user_input(self):
        """Monitors and processes user input in a separate thread while the stream is active.

        This method continuously checks for user input in the input queue.
        If input is found, it processes the input according to the specified color space and
        sends the corresponding data to the light.
        """

        while self._is_connection_alive:
            try:
                user_input = self._input_queue.get(
                    timeout=1
                )  # using timeout to avoid busy waiting
                self._process_user_input(user_input)
            except queue.Empty:
                continue
            except ValueError as e:
                logging.error("Error in user input: %s", e)

    def _attempt_reconnect(self):
        """Attempts to reconnect the DTLS service with a limit of 3 attempts.

        This method tries to re-establish the DTLS connection up to three times in case of connection loss.
        It resets the reconnection attempt counter after a successful reconnection.
        """

        with self._reconnect_lock:
            if self._reconnect_attempts >= 3:
                logging.error(
                    "Maximum reconnection attempts reached. Unable to reconnect."
                )
                return

            try:
                self._dtls_service.close_socket()
                self._dtls_service.do_handshake()
                self._reconnect_attempts = 0
                logging.info("Reconnected to the DTLS service.")
            except OSError as e:
                self._reconnect_attempts += 1
                logging.error(
                    "Failed to reconnect attempt %s due to NETWORK error: %s",
                    self._reconnect_attempts,
                    e,
                )
            except Exception as e:  # pylint: disable=broad-except
                self._reconnect_attempts += 1
                logging.error(
                    "Failed to reconnect attempt %s due to UNEXPECTED error: %s",
                    self._reconnect_attempts,
                    e,
                )

    def _process_user_input(self, user_input_list: list[tuple[int, int, int, int]]):
        """Processes the user input received.

        Args:
            user_input_list: list[tuple[int, int, int, int]] The user input to process.
            The input is expected to be a tuple of RGB16 color values along with a light identifier as last int.
        """
        logging.debug("Processing user input: %s", user_input_list)
        if not isinstance(user_input_list, list) and not len(user_input_list) > 0:
            raise ValueError(f"Unexpected input type: {type(user_input_list)} or empty list sent")

        logging.debug("Processing user input: %s", user_input_list)
        channel_data_list = []
        for user_input in user_input_list:
            r, g, b, light_id = user_input
            channel_data_list.append(self._pack_color_data((r, g, b), light_id))
        try:
            self._channel_data = channel_data_list
            message = self._build_message(self._channel_data)
            logging.debug(message)
            self._dtls_service.get_socket().sendto(
                message,
                (
                    self._dtls_service.get_server_address()[0],
                    self._dtls_service.get_server_address()[1],
                ),
            )
            self._last_message = message
        except SocketError as e:
            logging.error("Error sending message: %s", e)
            if self._is_connection_alive:
                logging.info("Attempting to reconnect...")
                self._attempt_reconnect()

    @classmethod
    def _pack_color_data(
            cls, color: Union[tuple[int, int, int], tuple[float, float, float]], light_id: int
    ) -> bytes:
        """Packs the given color data into bytes for transmission.

        Args:
            color (Union[tuple[int, int, int], tuple[float, float, float]]): The color data in either
            RGB8 or XYB format.
            light_id (int): An integer value associated with the color data, such as the light's ID or channel number.

        Returns:
            bytes: The packed color data in byte format, ready for transmission.
        """

        channel_data = b""
        channel_data += struct.pack(">B", light_id)

        rx = color[0]
        gy = color[1]
        bb = color[2]

        logging.debug("Converted values: %s, %s, %s", rx, gy, bb)
        return channel_data + struct.pack(">HHH", rx, gy, bb)
