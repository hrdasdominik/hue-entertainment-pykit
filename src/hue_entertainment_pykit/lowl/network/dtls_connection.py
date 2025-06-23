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
import logging
import socket
from ipaddress import IPv4Address

from mbedtls.tls import DTLSConfiguration, ClientContext, DTLSVersion

from hue_entertainment_pykit.lowl.network.patched_tls_wrapped_socket import PatchedTLSWrappedSocket


logger = logging.getLogger(__name__)

class DtlsConnection:
    """
    Manages DTLS connections with Philips Hue Bridges using pre-shared keys.

    This class is responsible for setting up and maintaining DTLS connections, including handling key exchanges and
    performing handshakes for secure communication. It provides methods to create the socket, perform handshakes,
    and close the connection.

    Attributes:
        _UDP_PORT (int): The UDP port used for the DTLS connection.
        _CIPHERS (list[str]): List of ciphers used for the DTLS connection.
        _SOCK_TIMEOUT (int): The socket timeout in seconds.
    """

    def __init__(self, ip_address: IPv4Address, username: str, client_key: str) -> None:
        self._UDP_PORT: int = 2100
        self._CIPHERS: tuple[str] = ("TLS-PSK-WITH-AES-128-GCM-SHA256",)
        self._SOCK_TIMEOUT: int = 10
        self._socket: PatchedTLSWrappedSocket | None = None
        self._ip_address: IPv4Address = ip_address
        self._username: str = username
        self._client_key: str = client_key

    def send_message(self, message: bytes) -> None:
        self._socket.send(message)

    def do_handshake(self) -> None:
        """
        Initiates and performs a handshake over the DTLS socket.

        Establishes a DTLS socket if not already present and performs a handshake to initiate secure communication.
        """

        logger.debug("Starting DTLS handshake")
        self._socket.do_handshake()
        logger.debug("DTLS handshake established")

    def close_socket(self) -> None:
        self._socket.close()

    def is_closed(self) -> bool:
        return self._socket.is_closed()

    def create_dtls_socket(self) -> None:
        """
        Creates a DTLS socket with the necessary configuration and context.
        This method is internally used to establish the DTLS connection.
        """

        logger.debug("Creating DTLS socket and context")
        config = DTLSConfiguration(
            pre_shared_key=(self._username, bytes.fromhex(self._client_key)),
            ciphers=self._CIPHERS,
            lowest_supported_version=DTLSVersion.DTLSv1_2
        )
        ip_str = str(self._ip_address)
        dtls_client = ClientContext(config)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.connect((ip_str, self._UDP_PORT))
        udp_socket.settimeout(self._SOCK_TIMEOUT)
        buffer = dtls_client.wrap_buffers(server_hostname=ip_str)

        self._socket = PatchedTLSWrappedSocket(udp_socket, buffer)
        logger.debug("DTLS socket established")
