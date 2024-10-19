"""
This module contains the DtlsService class, which manages Datagram Transport Layer Security (DTLS)
connections for communication with Philips Hue Bridges. The class is responsible for setting up and
maintaining DTLS connections, handling key exchanges, and performing necessary handshakes to ensure
secure communication.

The DtlsService class abstracts the complexities of DTLS communication, providing a simpler interface
for establishing and managing these connections. It's designed to work with pre-shared keys for
authentication, making it suitable for environments where Philips Hue Bridges utilize DTLS for secure
communication.

Classes:
- Dtls: Handles DTLS connections with Philips Hue Bridges using pre-shared keys.
"""
import errno
import logging
import os
import socket
import time
from typing import Tuple, List

from mbedtls._tls import WantReadError, WantWriteError, HandshakeStep
from mbedtls.tls import TLSWrappedSocket, DTLSConfiguration, ClientContext, DTLSVersion

from src.hue_entertainment_pykit.models.bridge import Bridge


class Dtls:
    """
    Manages DTLS connections with Philips Hue Bridges using pre-shared keys.

    This class is responsible for setting up and maintaining DTLS connections, including handling key exchanges and
    performing handshakes for secure communication. It provides methods to create the socket, perform handshakes,
    and close the connection.

    Attributes:
        _udp_port (int): The UDP port used for the DTLS connection.
        _server_address (Tuple[str, int]): The server address and port for the DTLS connection.
        _psk_key (bytes): The pre-shared key for DTLS authentication.
        _psk_identity (str): The identity associated with the pre-shared key.
        _ciphers (List[str]): List of ciphers used for the DTLS connection.
        _dtls_socket (TLSWrappedSocket | None): The DTLS socket used for the connection.
        _sock_timeout (int): The socket timeout in seconds.
    """

    def __init__(self, bridge: Bridge):
        """
        Initializes the DtlsService with a given bridge.

        Parameters:
            bridge (Bridge): An instance of Bridge to fetch connection details.
        """

        self._udp_port: int = 2100
        self._server_address: Tuple[str, int] = (
            bridge.get_ip_address(),
            self._udp_port,
        )
        self._psk_key = bytes.fromhex(bridge.get_client_key())
        self._psk_identity: str = bridge.get_hue_application_id()
        self._ciphers: List[str] = [
            "TLS-PSK-WITH-AES-128-GCM-SHA256",
        ]
        self._dtls_socket: TLSWrappedSocket | None = None
        self._sock_timeout: int = 5

    def __str__(self) -> str:
        """
        Returns a string representation of the DtlsService instance.

        Returns:
            str: A string describing the DtlsService instance.
        """

        return (
            "DTLS {\n"
            + f"   server_address: {self._server_address},\n"
            + f"   psk_key: {self._psk_key},\n"
            + f"   psk_identity: {self._psk_identity},\n"
            + f"   ciphers: {self._ciphers}\n"
            + "}"
        )

    def get_server_address(self) -> tuple[str, int]:
        """
        Retrieves the server address and port for the DTLS connection.

        Returns:
            Tuple[str, int]: The server address and port.
        """

        return self._server_address

    def get_socket(self) -> TLSWrappedSocket | None:
        """
        Gets or creates the DTLS socket for communication.

        Returns the existing DTLS socket or creates a new one if it does not exist, then returns it.

        Returns:
            TLSWrappedSocket | None: The DTLS socket, or None if unable to create
        """

        return self._dtls_socket

    def _create_dtls_socket(self):
        """
        Creates a DTLS socket with the necessary configuration and context.
        This method is internally used to establish the DTLS connection.
        """

        if self._dtls_socket is None:
            logging.info("Creating DTLS socket and context")
            config = DTLSConfiguration(
                pre_shared_key=(self._psk_identity, self._psk_key),
                ciphers=self._ciphers,
                lowest_supported_version=DTLSVersion.DTLSv1_2
            )
            dtls_client = ClientContext(config)
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.connect(self._server_address)
            udp_socket.settimeout(self._sock_timeout)
            buffer = dtls_client.wrap_buffers(server_hostname=self._server_address[0])

            self._dtls_socket = self.PatchedTLSWrappedSocket(udp_socket, buffer)

    def do_handshake(self):
        """
        Initiates and performs a handshake over the DTLS socket.

        Establishes a DTLS socket if not already present and performs a handshake to initiate secure communication.
        """

        self._create_dtls_socket()
        logging.info("Starting DTLS handshake")
        self._dtls_socket.do_handshake(self._server_address)
        logging.info("DTLS handshake established")

    def close_socket(self):
        """
        Closes the DTLS socket if it exists and sets it to None.
        """

        if self._dtls_socket:
            self._dtls_socket.close()
            self._dtls_socket = None

    class PatchedTLSWrappedSocket(TLSWrappedSocket):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._handshake_retries = 0  # Track the number of handshake attempts

        def do_handshake(self, *args):
            # pylint: disable=too-many-branches
            if args and self.type is not socket.SOCK_DGRAM:
                raise OSError(errno.ENOTCONN, os.strerror(errno.ENOTCONN))

            if len(args) == 0:
                flags, address = 0, None
            elif len(args) == 1:
                flags, address = 0, args[0]
            elif len(args) == 2:
                assert isinstance(args[0], int)
                flags, address = args
            else:
                raise TypeError("do_handshake() takes 0, 1, or 2 arguments")

            while self._handshake_state is not HandshakeStep.HANDSHAKE_OVER:
                try:
                    self._buffer.do_handshake()
                except WantReadError as exc:
                    if address is None:
                        data = self._socket.recv(TLSWrappedSocket.CHUNK_SIZE, flags)
                    else:
                        data, addr = self._socket.recvfrom(TLSWrappedSocket.CHUNK_SIZE, flags)
                        if addr != address:
                            raise OSError(
                                errno.ENOTCONN, os.strerror(errno.ENOTCONN)
                            ) from exc
                    self._buffer.receive_from_network(data)
                except WantWriteError:
                    in_transit = self._buffer.peek_outgoing(TLSWrappedSocket.CHUNK_SIZE)
                    if address is None:
                        amt = self._socket.send(in_transit, flags)
                    else:
                        amt = self._socket.sendto(in_transit, flags, address)
                    self._buffer.consume_outgoing(amt)

                    self._handshake_retries += 1
                    print(f"Retransmission attempt: {self._handshake_retries}")

                    if self._handshake_retries < 3:
                        print("Resending second ClientHello")
                        time.sleep(0.3)
                        if address is None:
                            amt = self._socket.send(in_transit, flags)
                        else:
                            amt = self._socket.sendto(in_transit, flags, address)
                        self._buffer.consume_outgoing(amt)

                    if self._handshake_retries > 3:
                        raise Exception("Maximum handshake retries exceeded")


