"""
Unit Tests for the Bridge Creation Module

This module contains unit tests for the `create_bridge()` function within the bridge management system, focusing on
validating the creation of Bridge objects under various input scenarios. It includes checks for proper type and format
validation of input parameters such as identification, rid, ip_address, swversion, username, hue_app_id, clientkey,
and name. The suite uses Python's unittest framework to ensure the bridge creation functionality's reliability and
integrity by handling both valid inputs and edge cases for robust error handling.
"""

import unittest
from unittest.mock import patch, MagicMock

from hue_entertainment_pykit import EntertainmentConfiguration
from hue_entertainment_pykit.api import create_bridge, Discovery, Entertainment
from hue_entertainment_pykit.bridge.bridge_repository import BridgeRepository
from hue_entertainment_pykit.models.bridge import Bridge
from hue_entertainment_pykit.models.entertainment_configuration import StatusTypes
from hue_entertainment_pykit.network.mdns import Mdns
from hue_entertainment_pykit.services.discovery_service import DiscoveryService


# pylint: disable=protected-access
class TestCreateBridge(unittest.TestCase):
    """Test cases for the `create_bridge` function with various inputs."""

    def setUp(self):
        """
        Sets up the test environment by patching necessary functions and creating mock objects.
        """

        self.valid_input = {
            "identification": "4abb74df-5b6b-410e-819b-bf4448355dff",
            "rid": "d476df48-83ad-4430-a104-53c30b46b4d0",
            "ip_address": "192.168.30.204",
            "swversion": 1962097030,
            "username": "8nuTIcK2nOf5oi88-5zPvV1YCt0wTHZIGG8MwXpu",
            "hue_app_id": "94530efc-933a-4f7c-97e5-ccf1a9fc79af",
            "clientkey": "B42753E1E1605A1AB90E1B6A0ECF9C51",
            "name": "1st Bridge",
        }

    def test_create_bridge_with_valid_input(self):
        """Test creating a bridge with valid input data ensures successful object creation."""

        bridge = create_bridge(**self.valid_input)
        self.assertIsNotNone(bridge)

    def test_create_bridge_with_invalid_identification(self):
        """Test that passing an invalid type for 'identification' raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["identification"] = 123
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_rid(self):
        """Test that an invalid 'rid' type raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["rid"] = 123
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_ip_address(self):
        """Test that an invalid 'ip_address' format raises a ValueError."""

        invalid_input = self.valid_input.copy()
        invalid_input["ip_address"] = "invalid_ip"
        with self.assertRaises(ValueError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_swversion(self):
        """Test that a non-integer 'swversion' raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["swversion"] = "not_an_integer"
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_username(self):
        """Test that an invalid 'username' type raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["username"] = 123
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_hue_app_id(self):
        """Test that an invalid 'hue_app_id' type raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["hue_app_id"] = 123
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_client_key(self):
        """Test that an invalid 'clientkey' type raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["clientkey"] = 123
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)

    def test_create_bridge_with_invalid_name(self):
        """Test that an invalid 'name' type raises a TypeError."""

        invalid_input = self.valid_input.copy()
        invalid_input["name"] = 123
        with self.assertRaises(TypeError):
            create_bridge(**invalid_input)


class TestDiscovery(unittest.TestCase):
    """Tests for the Discovery class focusing on the discovery of bridges."""

    @patch("hue_entertainment_pykit.network.mdns.Mdns", Mdns)
    @patch("hue_entertainment_pykit.bridge.bridge_repository.BridgeRepository", BridgeRepository)
    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService", DiscoveryService)
    def test_initialization(self):
        """Test the initialization of Discovery, ensuring correct instance creation of its components."""

        discovery = Discovery()
        self.assertIsInstance(discovery._mdns_service, Mdns)
        self.assertIsInstance(discovery._bridge_repository, BridgeRepository)
        self.assertIsInstance(discovery._discovery_service, DiscoveryService)

    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService.discover")
    def test_discover_bridges_without_ip(self, mock_discover):
        """Test bridge discovery without specifying an IP address."""

        mock_bridge1 = MagicMock(spec=Bridge)
        mock_bridge2 = MagicMock(spec=Bridge)

        mock_discover.return_value = {
            "192.168.1.1": mock_bridge1,
            "192.168.1.2": mock_bridge2,
        }
        discovery = Discovery()
        result = discovery.discover_bridges()
        expected_ips = {"192.168.1.1", "192.168.1.2"}

        self.assertEqual(set(result.keys()), expected_ips)

        for bridge in result.values():
            self.assertIsInstance(bridge, Bridge)

    @patch("hue_entertainment_pykit.services.discovery_service.DiscoveryService.discover")
    def test_discover_bridges_with_ip(self, mock_discover):
        """Test bridge discovery when specifying an IP address."""

        mock_discover.return_value = {"192.168.1.1": "Bridge1"}
        discovery = Discovery()
        result = discovery.discover_bridges("192.168.1.1")
        self.assertEqual(result, {"192.168.1.1": "Bridge1"})
        mock_discover.assert_called_with("192.168.1.1")


class TestEntertainment(unittest.TestCase):
    """Tests for the Entertainment class focusing on entertainment configurations."""

    def setUp(self):
        """Set up test case environment, including mock bridge and entertainment instance."""

        self.mock_bridge = MagicMock(spec=Bridge)
        self.entertainment = Entertainment(self.mock_bridge)

    def test_initialization(self):
        """Test initialization of the Entertainment instance."""

        self.assertEqual(self.entertainment._bridge, self.mock_bridge)
        self.assertIsNone(self.entertainment._entertainment_configs)

    def test_get_entertainment_configs_non_empty_cache(self):
        """Test retrieval of entertainment configs when cache is not empty."""

        self.entertainment._entertainment_configs = {"config1": "data1"}
        configs = self.entertainment.get_entertainment_configs()
        self.assertEqual(configs, {"config1": "data1"})

    def test_get_config_by_id_valid(self):
        """Test retrieval of a config by its ID when the ID is valid and exists."""

        self.entertainment._entertainment_configs = {"config1": MagicMock(id="config1")}
        config = self.entertainment.get_config_by_id("config1")
        self.assertIsNotNone(config)

    def test_get_config_by_id_invalid(self):
        """Test retrieval of a config by an ID that does not exist, expecting None."""

        self.entertainment._entertainment_configs = {"config1": MagicMock(id="config1")}
        config = self.entertainment.get_config_by_id("config2")
        self.assertIsNone(config)

    def test_get_ent_conf_repo(self):
        """Test retrieval of the entertainment configuration repository."""

        repo = self.entertainment.get_ent_conf_repo()
        self.assertEqual(repo, self.entertainment._ent_conf_repo)


if __name__ == "__main__":
    unittest.main()
