import os
import socket
import struct

from api.bridge.bridge import Bridge


class Dtls:
    def __init__(self, bridge: Bridge):
        self._bridge = bridge

    def create_udp_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def create_hello_packet(self):
        random_bytes = os.urandom(32)

        cipher_suites = [0xC0A8]
        cipher_suites_bytes = b"".join(
            struct.pack("!H", cs) for cs in cipher_suites)

        client_hello = struct.pack(
            "!BHHQH",
            0x16,
            0xFEFD,
            0x0000,
            0x0000000000,
            54
        ) + struct.pack(
            "!BHIHHI",
            0x01,
            38,
            0x0000,
            0x000000,
            38
        ) + struct.pack(
            "!H32sB",
            0xFEFD,
            random_bytes,
            0
        ) + struct.pack(
            "!HB",
            len(cipher_suites_bytes),
            1
        ) + cipher_suites_bytes + struct.pack(
            "!B",
            0
        )

    def send_hello_packet(self):
        udp_socket = self.create_udp_socket()
        server_address = (self._bridge.get_ip_address(), 2100)

        client_hello = self.create_hello_packet()

        udp_socket.sendto(udp_socket, server_address, client_hello)

        data, _ = udp_socket.recvfrom(1024)
        server_hello = data
