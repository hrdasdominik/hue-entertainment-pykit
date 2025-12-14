"""
Module: test_discovery_service.py

This module contains unit tests for the DiscoveryService class, focusing on testing the functionality of
discovering Philips Hue bridges using various methods like mDNS, cloud discovery, and manual IP input.

Classes:
    TestDiscoveryService: A suite of unit tests for the DiscoveryService class.
"""

import json
import logging
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, call

from zeroconf import Zeroconf

from hue_entertainment_pykit.models.bridge import Bridge
from hue_entertainment_pykit.bridge.bridge_repository import BridgeRepository
from hue_entertainment_pykit.services.discovery_service import DiscoveryService
from hue_entertainment_pykit.network.mdns import Mdns
from hue_entertainment_pykit.exceptions.bridge_exception import BridgeException
from hue_entertainment_pykit.utils.file_handler import FileHandler
from hue_entertainment_pykit.utils.status_code import StatusCode


# pylint: disable=protected-access, attribute-defined-outside-init
class TestDiscoveryService(unittest.TestCase):
    """
    Test suite for the DiscoveryService class, which handles discovery of Philips Hue bridges.

    Attributes:
        mdns_service (MagicMock): A mock of the Mdns class.
        bridge_repository (MagicMock): A mock of the BridgeRepository class.
        discovery_service (DiscoveryService): An instance of the DiscoveryService class for testing.
    """

    def setUp(self):
        """
        Initializes the DiscoveryService with mock dependencies for testing.
        """

        self.mdns_service = MagicMock(spec=Mdns)
        self.bridge_repository = MagicMock(spec=BridgeRepository)
        self.discovery_service = DiscoveryService(
            self.mdns_service, self.bridge_repository
        )

    def tearDown(self):
        """
        Cleans up logging and any created directories after tests.
        """

        logging.shutdown()
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def test_does_support_streaming_data(self):
        """
        Tests the _does_support_streaming_data method to verify streaming support based on bridge software version.
        """

        bridge = MagicMock(spec=Bridge)

        bridge.get_swversion.return_value = self.discovery_service._MIN_SWVERSION
        self.assertTrue(self.discovery_service._does_support_streaming_data(bridge))

        bridge.get_swversion.return_value = self.discovery_service._MIN_SWVERSION - 1
        self.assertFalse(self.discovery_service._does_support_streaming_data(bridge))

    @patch.object(DiscoveryService, "_does_support_streaming_data")
    def test_filter_supported_bridges(self, mock_does_support_streaming):
        """
        Tests the _filter_supported_bridges method to ensure it filters bridges based on streaming support.
        """

        bridge1 = MagicMock(spec=Bridge)
        bridge2 = MagicMock(spec=Bridge)
        bridge3 = MagicMock(spec=Bridge)

        mock_does_support_streaming.side_effect = [True, False, True]

        bridges = [bridge1, bridge2, bridge3]
        supported_bridges = self.discovery_service._filter_supported_bridges(bridges)

        self.assertEqual(supported_bridges, [bridge1, bridge3])
        mock_does_support_streaming.assert_has_calls(
            [call(bridge1), call(bridge2), call(bridge3)], any_order=True
        )

    @patch("hue_entertainment_pykit.utils.file_handler.FileHandler.write_json")
    @patch("hue_entertainment_pykit.models.bridge.Bridge.from_dict")
    def test_create_bridges_from_addresses(
        self, mock_bridge_from_dict, mock_write_json
    ):
        """
        Tests the _create_bridges_from_addresses method to verify creation of bridge instances from IP addresses.
        """

        test_addresses = ["192.168.1.3", "192.168.1.4"]

        self.bridge_repository.fetch_bridge_data.side_effect = [
            {
                "id": "id",
                "rid": "rid",
                "internalipaddress": address,
                "swversion": 1962097030,
                "username": "username",
                "hue-application-id": "hue-id",
                "clientkey": "clientkey",
                "name": "bridge",
            }
            for address in test_addresses
        ]

        mock_bridge1 = MagicMock(spec=Bridge)
        mock_bridge2 = MagicMock(spec=Bridge)
        mock_bridge_from_dict.side_effect = [mock_bridge1, mock_bridge2]

        bridges = self.discovery_service._create_bridges_from_addresses(test_addresses)

        self.assertEqual(len(bridges), 2)
        self.assertEqual(bridges[0], mock_bridge1)
        self.assertEqual(bridges[1], mock_bridge2)

        self.bridge_repository.fetch_bridge_data.assert_has_calls(
            [call(address) for address in test_addresses], any_order=True
        )

        expected_bridge_data = [
            {
                "id": "id",
                "rid": "rid",
                "internalipaddress": "192.168.1.3",
                "swversion": 1962097030,
                "username": "username",
                "hue-application-id": "hue-id",
                "clientkey": "clientkey",
                "name": "bridge",
            },
            {
                "id": "id",
                "rid": "rid",
                "internalipaddress": "192.168.1.4",
                "swversion": 1962097030,
                "username": "username",
                "hue-application-id": "hue-id",
                "clientkey": "clientkey",
                "name": "bridge",
            },
        ]
        mock_bridge_from_dict.assert_has_calls(
            [call(data) for data in expected_bridge_data]
        )

        mock_write_json.assert_has_calls(
            [
                call(FileHandler.BRIDGE_FILE_PATH, bridge.to_dict())
                for bridge in [mock_bridge1, mock_bridge2]
            ],
            any_order=True,
        )

    @patch("hue_entertainment_pykit.services.discovery_service.Zeroconf")
    @patch("hue_entertainment_pykit.services.discovery_service.ServiceBrowser")
    def test_discover_via_mdns(self, mock_service_browser, mock_zeroconf):
        """
        Tests the _discover_via_mdns method to verify bridge discovery using the mDNS protocol.
        """

        mock_zeroconf.return_value = MagicMock(spec=Zeroconf)

        self.mdns_service.get_service_discovered().wait.return_value = True
        self.mdns_service.get_addresses.return_value = ["192.168.1.2"]

        with patch.object(
            self.discovery_service, "_create_bridges_from_addresses"
        ) as mock_create:
            mock_create.return_value = [
                MagicMock(name="Bridge1"),
                MagicMock(name="Bridge2"),
            ]
            bridges = self.discovery_service._discover_via_mdns()

            self.assertEqual(len(bridges), 2)
            mock_zeroconf.assert_called_once()
            mock_service_browser.assert_called_once()
            self.mdns_service.get_service_discovered().wait.assert_called_once_with(
                timeout=10
            )
            self.mdns_service.get_addresses.assert_called_once()
            mock_create.assert_called_once_with(["192.168.1.2"])

    @patch("requests.get")
    @patch.object(DiscoveryService, "_create_bridges_from_addresses")
    def test_discover_via_cloud_success(self, mock_create_bridges, mock_get):
        """
        Tests the _discover_via_cloud method for a successful cloud-based discovery scenario.
        """

        mock_response = MagicMock()
        mock_response.status_code = StatusCode.OK.value
        mock_response.json.return_value = [{"internalipaddress": "192.168.1.2"}]
        mock_get.return_value = mock_response

        mock_create_bridges.return_value = [MagicMock(name="Bridge1")]

        bridges = self.discovery_service._discover_via_cloud()

        self.assertEqual(len(bridges), 1)
        mock_get.assert_called_once_with(self.discovery_service._CLOUD_URL, timeout=5)
        mock_create_bridges.assert_called_once_with(["192.168.1.2"])

    @patch("requests.get")
    def test_discover_via_cloud_failure(self, mock_get):
        """
        Tests the _discover_via_cloud method for a failure scenario in cloud-based discovery.
        """

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(BridgeException):
            self.discovery_service._discover_via_cloud()

        mock_get.assert_called_once_with(self.discovery_service._CLOUD_URL, timeout=5)

    @patch.object(DiscoveryService, "_create_bridges_from_addresses")
    def test_discover_manually(self, mock_create_bridges):
        """
        Tests the _discover_manually method to ensure correct discovery using a manual IP address.
        """

        test_ip = "192.168.1.3"
        mock_bridge = MagicMock(name="ManualBridge")
        mock_create_bridges.return_value = [mock_bridge]

        bridges = self.discovery_service._discover_manually(test_ip)

        mock_create_bridges.assert_called_once_with([test_ip])
        self.assertEqual(len(bridges), 1)
        self.assertEqual(bridges[0], mock_bridge)

    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService._filter_supported_bridges")
    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService._load_bridge_data")
    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService._discover_via_mdns")
    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService._discover_via_cloud")
    def test_discover(
        self,
        mock_discover_via_cloud,
        mock_discover_via_mdns,
        mock_load_bridge_data,
        mock_filter_supported_bridges,
    ):
        """
        Tests the discover method to verify comprehensive bridge discovery using various methods.
        """

        mock_cloud_bridge = MagicMock()
        mock_cloud_bridge.get_name.return_value = "CloudBridge"
        mock_cloud_bridge.get_swversion.return_value = 1948086000
        mock_mdns_bridge = MagicMock()
        mock_mdns_bridge.get_name.return_value = "MdnsBridge"
        mock_mdns_bridge.get_swversion.return_value = 1948086000
        mock_saved_bridge = MagicMock()
        mock_saved_bridge.get_name.return_value = "SavedBridge"
        mock_saved_bridge.get_swversion.return_value = 1948086000

        mock_discover_via_cloud.return_value = [mock_cloud_bridge]
        mock_discover_via_mdns.return_value = [mock_mdns_bridge]
        mock_load_bridge_data.return_value = [mock_saved_bridge]
        mock_filter_supported_bridges.side_effect = lambda bridges: bridges

        bridges = self.discovery_service.discover()
        self.assertTrue("SavedBridge" in bridges)

        with patch(
            "hue_entertainment_pykit.services.discovery_service.DiscoveryService._discover_manually"
        ) as mock_discover_manually:
            mock_manual_bridge = MagicMock()
            mock_manual_bridge.get_name.return_value = "ManualBridge"
            mock_manual_bridge.get_swversion.return_value = 1948086000
            mock_discover_manually.return_value = [mock_manual_bridge]

            bridges = self.discovery_service.discover(ip_address="192.168.1.2")
            self.assertTrue("ManualBridge" in bridges)

    @mock.patch("hue_entertainment_pykit.utils.file_handler.FileHandler.read_json")
    @mock.patch("hue_entertainment_pykit.models.bridge.Bridge.from_dict")
    def test_load_bridge_data(self, mock_bridge_from_dict, mock_read_json):
        """
        Tests the _load_bridge_data method to verify loading bridge data from a file.
        """

        mock_bridge = mock.MagicMock(spec=Bridge)
        mock_bridge_from_dict.return_value = mock_bridge

        mock_read_json.return_value = [
            {
                "id": "id",
                "rid": "rid",
                "internalipaddress": "192.168.1.3",
                "swversion": 1962097030,
                "username": "username",
                "hue-application-id": "hue-id",
                "clientkey": "clientkey",
                "name": "bridge",
            }
        ]

        bridges = DiscoveryService._load_bridge_data()
        self.assertEqual(len(bridges), 1)
        self.assertIsInstance(bridges[0], Bridge)

        mock_read_json.return_value = {
            "id": "id",
            "rid": "rid",
            "internalipaddress": "192.168.1.4",
            "swversion": 1962097030,
            "username": "username",
            "hue-application-id": "hue-id",
            "clientkey": "clientkey",
            "name": "bridge",
        }
        bridges = DiscoveryService._load_bridge_data()
        self.assertEqual(len(bridges), 1)
        self.assertIsInstance(bridges[0], Bridge)

        mock_read_json.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            DiscoveryService._load_bridge_data()

        mock_read_json.side_effect = json.JSONDecodeError(
            "Expecting ',' delimiter", '{"test": "bad json"}', 10
        )
        with self.assertRaises(json.JSONDecodeError):
            DiscoveryService._load_bridge_data()

        mock_read_json.side_effect = None  # Reset side effect
        mock_read_json.return_value = "Not a list or a dict"
        with self.assertRaises(ValueError):
            DiscoveryService._load_bridge_data()

    def test_is_valid_ip(self):
        """
        Tests the _is_valid_ip method to verify IP address validation.
        """

        self.assertTrue(DiscoveryService._is_valid_ip("192.168.1.1"))
        self.assertTrue(DiscoveryService._is_valid_ip("255.255.255.255"))
        self.assertTrue(DiscoveryService._is_valid_ip("0.0.0.0"))
        self.assertTrue(DiscoveryService._is_valid_ip("127.0.0.1"))

        self.assertFalse(DiscoveryService._is_valid_ip("256.256.256.256"))
        self.assertFalse(DiscoveryService._is_valid_ip("192.168.1.256"))
        self.assertFalse(DiscoveryService._is_valid_ip("192.168.1"))
        self.assertFalse(DiscoveryService._is_valid_ip("192.168.1.1.1"))
        self.assertFalse(DiscoveryService._is_valid_ip("abc.def.ghi.jkl"))
        self.assertFalse(DiscoveryService._is_valid_ip(""))
        self.assertFalse(DiscoveryService._is_valid_ip("192.168.1.1a"))
        self.assertFalse(DiscoveryService._is_valid_ip("192.168.1."))
        self.assertFalse(DiscoveryService._is_valid_ip(".192.168.1.1"))
        self.assertFalse(DiscoveryService._is_valid_ip("192.168.1.01"))


if __name__ == "__main__":
    unittest.main()
