"""
Module: test_streaming_service.py

This module contains unit tests for the BridgeStreamingService class, focusing on testing the functionality of
streaming light patterns to Philips Hue entertainment areas.

Classes:
    TestStreamingService: A suite of unit tests for the BridgeStreamingService class.
"""

import struct
import unittest
from socket import error as SocketError
from unittest.mock import MagicMock, patch

from bridge.entertainment_configuration_repository import (
    EntertainmentConfigurationRepository,
)
from models.entertainment_configuration import (
    EntertainmentConfiguration,
)
from network.dtls import Dtls
from services.streaming_service import StreamingService


# pylint: disable=protected-access, attribute-defined-outside-init
class TestStreamingService(unittest.TestCase):
    """
    Test suite for the BridgeStreamingService class, which handles streaming to Philips Hue entertainment areas.

    Attributes:
        mock_entertainment_config (MagicMock): A mock of the EntertainmentConfiguration class.
        mock_entertainment_repo (MagicMock): A mock of the EntertainmentConfigurationApiService class.
        mock_dtls_service (MagicMock): A mock of the Dtls class.
        streaming_service (BridgeStreamingService): An instance of the BridgeStreamingService class for testing.
    """

    def setUp(self):
        """
        Initializes the BridgeStreamingService with mock dependencies for testing.
        """

        self.mock_entertainment_config = MagicMock(spec=EntertainmentConfiguration)
        self.mock_entertainment_config.id = "id"
        self.mock_entertainment_repo = MagicMock(
            spec=EntertainmentConfigurationRepository
        )
        self.mock_dtls_service = MagicMock(spec=Dtls)
        self.streaming_service = StreamingService(
            self.mock_entertainment_config,
            self.mock_entertainment_repo,
            self.mock_dtls_service,
        )

    def test_is_stream_active(self):
        """
        Tests the is_stream_active http_method to verify the stream's active status.
        """

        self.assertFalse(self.streaming_service.is_stream_active())
        self.streaming_service._is_connection_alive = True
        self.assertTrue(self.streaming_service.is_stream_active())

    def test_set_color_space_valid(self):
        """
        Tests the set_color_space http_method with valid color spaces (rgb, xyb).
        """

        self.streaming_service.set_color_space("rgb")
        self.assertEqual(self.streaming_service._color_space, struct.pack(">B", 0x00))

        self.streaming_service.set_color_space("xyb")
        self.assertEqual(self.streaming_service._color_space, struct.pack(">B", 0x01))

    def test_set_color_space_invalid(self):
        """
        Tests the set_color_space http_method with an invalid color space, expecting a ValueError.
        """

        with self.assertRaises(ValueError):
            self.streaming_service.set_color_space("invalid_color_space")

    def test_start_stream(self):
        """
        Tests the start_stream http_method to ensure it properly starts the streaming process.
        """

        with patch.object(
            self.streaming_service._connection_thread, "start"
        ) as mock_conn_thread_start, patch.object(
            self.streaming_service._processing_thread, "start"
        ) as mock_proc_thread_start:
            self.streaming_service.setup_for_streaming()

            mock_conn_thread_start.assert_called()
            mock_proc_thread_start.assert_called()

        self.assertTrue(self.streaming_service._is_connection_alive)
        self.mock_entertainment_repo.put_configuration.assert_called()
        self.mock_dtls_service.do_handshake.assert_called()

    @patch("threading.Thread")
    def test_stop_stream_active(self, mock_thread):
        """
        Tests the stop_stream http_method when the stream is active, ensuring proper stream termination.
        """

        mock_thread.return_value.start.side_effect = lambda: None

        self.streaming_service._is_connection_alive = True
        self.streaming_service._connection_thread = mock_thread()
        self.streaming_service._processing_thread = mock_thread()

        self.streaming_service.setup_for_stop_streaming()

        self.assertFalse(self.streaming_service._is_connection_alive)

    @patch("threading.Thread")
    def test_stop_stream_inactive(self, mock_thread):
        """
        Tests the stop_stream http_method when the stream is inactive, expecting a SocketError.
        """

        mock_thread.return_value.start.side_effect = lambda: None
        self.streaming_service._connection_thread = mock_thread()
        self.streaming_service._processing_thread = mock_thread()

        self.streaming_service._is_connection_alive = False
        with self.assertRaises(SocketError):
            self.streaming_service.setup_for_stop_streaming()

    def test_process_user_input_valid(self):
        """
        Tests processing of valid user input for streaming.
        """
        valid_input = (255, 255, 255, 0)
        self.streaming_service.set_input(valid_input)
        self.assertFalse(self.streaming_service._input_queue.empty())

    def test_process_user_input_invalid(self):
        """
        Tests processing of invalid user input, expecting an error log.
        """

        invalid_input = (300, 255, 255, 0)
        with self.assertLogs(level="ERROR") as log:
            self.streaming_service.set_input(invalid_input)
            self.assertIn(
                "ERROR:root:Invalid input: values must be a valid rgb8 (0 - 255) or xyb (0.0 - 1.0)",
                log.output,
            )


if __name__ == "__main__":
    unittest.main()
