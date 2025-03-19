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
from typing import Union

from models.payload import Payload
from models.entertainment_configuration import (
    EntertainmentConfiguration,
)
from bridge.entertainment_configuration_repository import (
    EntertainmentConfigurationRepository,
)
from network.dtls import Dtls
from utils.converter import Converter


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

        self._entertainment_config = entertainment_configuration
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
        self._entertainment_id = self._entertainment_config.id.encode("utf-8")

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
            .set_key_and_or_value("id", self._entertainment_config.id)
            .set_key_and_or_value("action", "start")
        )
        self._entertainment_configuration_repository.put_configuration(payload)
        self._dtls_service.do_handshake()
        self._is_connection_alive = True

        self._connection_thread.start()
        self._processing_thread.start()

    def stop_stream(self):
        """Stops the streaming service, ensuring that all resources are properly released.

        This method stops the streaming process by terminating the connection threads and closing the DTLS socket.
        It also updates the entertainment configuration repository to indicate that the streaming session has stopped.
        """

        if self._dtls_service.get_socket() and self._is_connection_alive:
            self._is_connection_alive = False

            self._connection_thread.join(timeout=10)
            self._processing_thread.join(timeout=10)

            if self._connection_thread.is_alive() or self._processing_thread.is_alive():
                logging.warning("One or more threads did not terminate as expected.")

            self._dtls_service.close_socket()

            payload = (
                Payload()
                .set_key_and_or_value("id", self._entertainment_config.id)
                .set_key_and_or_value("action", "stop")
            )
            self._entertainment_configuration_repository.put_configuration(payload)
        else:
            raise SocketError(
                "Unable to stop stream: DTLS socket is not available or stream is not active."
            )

    def set_input(
        self,
        user_input: Union[tuple[int, int, int, int], tuple[float, float, float, int]],
    ):
        """Sets the user input for processing.

        Args:
            user_input (Union[tuple[int, int, int, int], tuple[float, float, float, int]]): The user input data, either
            in RGB8 or XYB format, along with a light identifier. The input should be a tuple containing either
            three integer values (RGB) or three float values (XYB) followed by the light identifier as a string.

            RGB8 min(0) - max(255)
            XYB min(0.0) - max (1.0)
        """

        rx, gy, bb, light_id = user_input
        color = rx, gy, bb
        logging.info("Setting color(%s, %s, %s) on light %s", rx, gy, bb, light_id)
        if self._is_valid_rgb8(color) or self._is_valid_xyb(color):
            self._input_queue.put(user_input)
        else:
            logging.error(
                "Invalid input: values must be a valid rgb8 (0 - 255) or xyb (0.0 - 1.0)"
            )

    def _build_message(self, channel_data):
        """Constructs a message for streaming with the given channel data.

        Args:
            channel_data (bytes): The channel data to be included in the message. It includes various parameters such as
            protocol name, version, sequence ID, reserved bytes, color space, and entertainment ID, concatenated with
            the actual channel data.

        Returns:
            bytes: The constructed message, ready to be sent over the network.
        """

        return (
            self._protocol_name
            + self._version
            + self._sequence_id
            + self._reserved
            + self._color_space
            + self._reserved2
            + self._entertainment_id
            + channel_data
        )

    def _init_message(self) -> bytes:
        """Initialize the streaming message with default channel data.

        Returns:
            bytes: The initialized message.
        """

        x, y, b = Converter.xyb_to_rgb16((0.0, 0.0, 0.0))

        self._channel_data = self._DEFAULT_CHANNEL_VALUE
        self._channel_data += struct.pack(">HHH", x, y, b)

        return self._build_message(self._channel_data)

    def _keep_connection_alive(self):
        """Keeps the DTLS connection alive by sending messages at regular intervals.

        This method runs in a separate thread and is responsible for maintaining the DTLS connection.
        It periodically sends the last known message to keep the connection active.
        If the connection is lost, it attempts to reconnect.
        """

        while self._is_connection_alive:
            try:
                self._dtls_service.get_socket().send(
                    self._last_message
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
                    "Failed to reconnect attempt %s due to network error: %s",
                    self._reconnect_attempts,
                    e,
                )
            except Exception as e:  # pylint: disable=broad-except
                self._reconnect_attempts += 1
                logging.error(
                    "Failed to reconnect attempt %s due to unexpected error: %s",
                    self._reconnect_attempts,
                    e,
                )

    def _process_user_input(self, user_input):
        """Processes the user input received.

        Args:
            user_input: The user input to process. The input is expected to be a tuple of either
            RGB8 or XYB color values along with a light identifier.
        """

        if len(user_input) != 4:
            raise ValueError(f"{user_input} invalid input. Expected 4 values.")

        rx, gy, bb, light_id = user_input
        color = (rx, gy, bb)
        if self._is_valid_rgb8(color) or self._is_valid_xyb(color):
            logging.debug("Processing user input: %s", color)
            self._send_color_to_light(color, light_id)
        else:
            raise ValueError(
                "Invalid input. Neither inputs are rgb8 or xyb compatible."
            )

    def _send_color_to_light(
        self, color: Union[tuple[int, int, int], tuple[float, float, float]], value: int
    ):
        """Sends color data to a light.

        Args:
            color (Union[tuple[int, int, int], tuple[float, float, float]]): The color data to send,
            either as RGB8 or XYB values.
            value (int): An integer representing a specific value related to the light, such as its ID or channel.

        This method packages the color data and sends it over the DTLS connection to the specified light.
        """

        try:
            self._channel_data = self._pack_color_data(color, value)
            message = self._build_message(self._channel_data)
            logging.debug(message)
            self._dtls_service.get_socket().send(
                message
            )
            self._last_message = message
        except SocketError as e:
            logging.error("Error sending message: %s", e)
            if self._is_connection_alive:
                logging.info("Attempting to reconnect...")
                self._attempt_reconnect()

    def _pack_color_data(
        self, color: Union[tuple[int, int, int], tuple[float, float, float]], value: int
    ) -> bytes:
        """Packs the given color data into bytes for transmission.

        Args:
            color (Union[tuple[int, int, int], tuple[float, float, float]]): The color data in either
            RGB8 or XYB format.
            value (int): An integer value associated with the color data, such as the light's ID or channel number.

        Returns:
            bytes: The packed color data in byte format, ready for transmission.
        """

        channel_data = b""
        channel_data += struct.pack(">B", value)
        if self._is_valid_xyb(color):
            rx, gy, bb = Converter.xyb_to_rgb16(color)
        else:
            rx, gy, bb = Converter.rgb8_to_rgb16(color)

        logging.debug("Converted values: %s, %s, %s", rx, gy, bb)
        return channel_data + struct.pack(">HHH", rx, gy, bb)

    @classmethod
    def _is_valid_rgb8(cls, rgb8: tuple[int, int, int]) -> bool:
        """Check if the given RGB8 color is valid.

        Args:
            rgb8 (tuple[int, int, int]): A tuple representing the RGB8 color.

        Returns:
            bool: True if the color is a valid RGB8, False otherwise.
        """

        return all(0 <= value <= 255 for value in rgb8)

    @classmethod
    def _is_valid_xyb(cls, xyb: tuple[float, float, float]) -> bool:
        """Check if the given XYB color is valid.

        Args:
            xyb (tuple[float, float, float]): A tuple representing the XYB color.

        Returns:
            bool: True if the color is a valid XYB, False otherwise.
        """

        return all(0.0 <= value <= 1.0 for value in xyb)
