import errno
import logging
import os
import socket
import time

from mbedtls._tls import WantReadError, WantWriteError, HandshakeStep
from mbedtls.tls import TLSWrappedSocket


logger = logging.getLogger(__name__)

class PatchedTLSWrappedSocket(TLSWrappedSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handshake_retries = 0  # Track the number of handshake attempts

    def is_closed(self):
        return self._closed

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
                logger.debug(f"Retransmission attempt: {self._handshake_retries}")

                if self._handshake_retries <= 3:
                    logger.debug("Resending ClientHello")
                    time.sleep(0.3)
                    if address is None:
                        amt = self._socket.send(in_transit, flags)
                    else:
                        amt = self._socket.sendto(in_transit, flags, address)
                    self._buffer.consume_outgoing(amt)

                else:
                    raise Exception("Maximum handshake retries exceeded")
