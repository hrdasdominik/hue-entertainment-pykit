"""
Module: test_dtls_connection.py

Unit tests for the DtlsConnection class. These tests mock all network and
mbedtls interactions to verify behavior without opening real sockets.
"""

import unittest
from ipaddress import IPv4Address
from unittest.mock import MagicMock, patch

from hue_entertainment_pykit.lowl.network.dtls_connection import DtlsConnection
from mbedtls.tls import DTLSVersion


class TestDtlsConnection(unittest.TestCase):
    def setUp(self):
        self.ip = IPv4Address("192.168.1.2")
        self.username = "0123456789abcdef"
        self.client_key = "00112233445566778899aabbccddeeff"
        self.dtls_connection = DtlsConnection(self.ip, self.username, self.client_key)

    @patch("hue_entertainment_pykit.lowl.network.dtls_connection.PatchedTLSWrappedSocket")
    @patch("hue_entertainment_pykit.lowl.network.dtls_connection.socket.socket")
    @patch("hue_entertainment_pykit.lowl.network.dtls_connection.ClientContext")
    @patch("hue_entertainment_pykit.lowl.network.dtls_connection.DTLSConfiguration")
    def test_create_dtls_socket_builds_context_and_wraps(
        self,
        mock_dtls_config,
        mock_client_ctx_ctor,
        mock_socket_ctor,
        mock_wrapped_socket_ctor,
    ):
        udp_sock = MagicMock()
        mock_socket_ctor.return_value = udp_sock

        client_ctx = MagicMock()
        mock_client_ctx_ctor.return_value = client_ctx
        buffer = MagicMock()
        client_ctx.wrap_buffers.return_value = buffer

        wrapped_sock = MagicMock()
        mock_wrapped_socket_ctor.return_value = wrapped_sock

        self.dtls_connection.create_dtls_socket()

        self.assertTrue(mock_dtls_config.called)
        kwargs = mock_dtls_config.call_args.kwargs
        self.assertEqual(kwargs["ciphers"], ("TLS-PSK-WITH-AES-128-GCM-SHA256",))
        self.assertEqual(kwargs["lowest_supported_version"], DTLSVersion.DTLSv1_2)
        self.assertEqual(kwargs["pre_shared_key"][0], self.username)
        self.assertEqual(kwargs["pre_shared_key"][1], bytes.fromhex(self.client_key))

        mock_socket_ctor.assert_called_once()
        udp_sock.connect.assert_called_once_with((str(self.ip), 2100))
        udp_sock.settimeout.assert_called_once_with(10)

        client_ctx.wrap_buffers.assert_called_once_with(server_hostname=str(self.ip))
        mock_wrapped_socket_ctor.assert_called_once_with(udp_sock, buffer)

        self.assertIs(self.dtls_connection._socket, wrapped_sock)

    def test_send_message_delegates_to_wrapped_socket(self):
        mock_sock = MagicMock()
        self.dtls_connection._socket = mock_sock
        payload = b"hello"

        self.dtls_connection.send_message(payload)

        mock_sock.send.assert_called_once_with(payload)

    def test_do_handshake_calls_underlying_socket(self):
        mock_sock = MagicMock()
        self.dtls_connection._socket = mock_sock

        self.dtls_connection.do_handshake()

        mock_sock.do_handshake.assert_called_once()

    def test_close_socket_closes_underlying_socket(self):
        mock_sock = MagicMock()
        self.dtls_connection._socket = mock_sock

        self.dtls_connection.close_socket()

        mock_sock.close.assert_called_once()

    def test_is_closed_propagates_state(self):
        mock_sock = MagicMock()
        mock_sock.is_closed.return_value = True
        self.dtls_connection._socket = mock_sock
        self.assertTrue(self.dtls_connection.is_closed())

        mock_sock.is_closed.return_value = False
        self.assertFalse(self.dtls_connection.is_closed())


if __name__ == "__main__":
    unittest.main()