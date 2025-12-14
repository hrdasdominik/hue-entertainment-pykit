"""
Module: test_dtls.py

This module contains unit tests for the Dtls class, focusing on testing its functionality in
establishing a DTLS connection with a Philips Hue Bridge.

Classes:
    TestDtls: A suite of unit tests for the Dtls class.
"""

import unittest
from unittest.mock import MagicMock

from mbedtls.tls import TLSWrappedSocket

from hue_entertainment_pykit.models.bridge import Bridge
from hue_entertainment_pykit.network.dtls import Dtls


# pylint: disable=protected-access, attribute-defined-outside-init
class TestDtls(unittest.TestCase):
    """
    Test suite for the Dtls class, which handles DTLS connections with the Philips Hue Bridge.

    Attributes:
        mock_bridge (MagicMock): A mock of the Bridge class.
        dtls_service (Dtls): An instance of the Dtls class for testing.
    """

    def setUp(self):
        """
        Sets up a mock bridge and initializes the Dtls service for testing.
        """

        self.mock_bridge = MagicMock(spec=Bridge)
        self.mock_bridge.get_ip_address.return_value = "192.168.1.2"
        self.mock_bridge.get_client_key.return_value = "0123456789abcdef"
        self.mock_bridge.get_hue_application_id.return_value = "test_app_id"
        self.dtls_service = Dtls(self.mock_bridge)

    def test_initialization(self):
        """
        Tests the initialization of the Dtls service, ensuring correct setup of server address and PSK key.
        """

        self.assertEqual(self.dtls_service._server_address[0], "192.168.1.2")
        self.assertIsInstance(self.dtls_service._psk_key, bytes)

    def test_get_server_address(self):
        """
        Tests the get_server_address method to ensure it returns the correct server address and port.
        """
        self.assertEqual(self.dtls_service.get_server_address(), ("192.168.1.2", 2100))

    def test_close_socket(self):
        """
        Tests the close_socket method to verify it correctly closes the DTLS socket and cleans up resources.
        """
        mock_tls_socket = MagicMock(spec=TLSWrappedSocket)
        self.dtls_service._dtls_socket = mock_tls_socket
        self.dtls_service.close_socket()
        mock_tls_socket.close.assert_called_once()
        self.assertIsNone(self.dtls_service._dtls_socket)


if __name__ == "__main__":
    unittest.main()
