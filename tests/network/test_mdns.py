"""
Module: test_mdns.py

Unit tests for the Mdns class. We mock Zeroconf's get_service_info and the returned
ServiceInfo.parsed_addresses() to simulate various discovery scenarios.
"""
import unittest
from unittest.mock import Mock
from ipaddress import IPv4Address

from hue_entertainment_pykit.lowl.network.mdns import Mdns


class _FakeServiceInfo:
    def __init__(self, addrs):
        self._addrs = addrs

    def parsed_addresses(self):
        return list(self._addrs)


class TestMdns(unittest.TestCase):
    def setUp(self):
        self.discovered = []

        def _cb(addresses):
            self.discovered.append(list(addresses))

        self.listener = Mdns(_cb)
        self.zc = Mock()

    def test_add_service_filters_ipv6_and_calls_callback(self):
        info = _FakeServiceInfo(["192.168.1.10", "fe80::1", "10.0.0.5"])
        self.zc.get_service_info.return_value = info

        self.listener.add_service(self.zc, "_hue._tcp.local.", "HueBridge-ABC")

        self.assertEqual(len(self.discovered), 1)
        self.assertEqual(
            self.discovered[0],
            [IPv4Address("192.168.1.10"), IPv4Address("10.0.0.5")],
        )

    def test_update_service_calls_callback_with_ipv4s(self):
        info = _FakeServiceInfo(["172.16.0.2"])
        self.zc.get_service_info.return_value = info

        self.listener.update_service(self.zc, "_hue._tcp.local.", "HueBridge-XYZ")

        self.assertEqual(len(self.discovered), 1)
        self.assertEqual(self.discovered[0], [IPv4Address("172.16.0.2")])

    def test_no_info_no_callback(self):
        self.zc.get_service_info.return_value = None

        self.listener.add_service(self.zc, "_hue._tcp.local.", "HueBridge-GONE")
        self.assertEqual(self.discovered, [])

    def test_only_ipv6_no_callback(self):
        info = _FakeServiceInfo(["fe80::abcd", "::1"])
        self.zc.get_service_info.return_value = info

        self.listener.add_service(self.zc, "_hue._tcp.local.", "HueBridge-IPv6")
        self.assertEqual(self.discovered, [])


if __name__ == "__main__":
    unittest.main()
