"""
Module: test_mdns.py

This module contains unit tests for the Mdns class, focusing on testing its functionality in
discovering services using the mDNS protocol.

Classes:
    TestMdns: A suite of unit tests for the Mdns class.
"""

import logging
import os
import shutil
import unittest
from threading import Event
from unittest.mock import MagicMock

from zeroconf import Zeroconf

from hue_entertainment_pykit.network.mdns import Mdns


# pylint: disable=protected-access, attribute-defined-outside-init
class TestMdns(unittest.TestCase):
    """
    Test suite for the Mdns class, which handles service discovery using the mDNS protocol.

    Attributes:
        mdns_service (Mdns): An instance of the Mdns class for testing.
    """

    def setUp(self):
        """
        Initializes the Mdns service for testing.
        """

        self.mdns_service = Mdns()

    def tearDown(self):
        """
        Cleans up logging and any created directories after tests.
        """

        logging.shutdown()
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def test_initialization(self):
        """
        Tests the initialization of the Mdns service, ensuring it starts with an empty list of addresses.
        """

        self.assertEqual(self.mdns_service._addresses, [])
        self.assertIsInstance(self.mdns_service._service_discovered, Event)

    def test_add_service(self):
        """
        Tests the add_service method to verify correct handling and addition of a new service.
        """

        zc = MagicMock(spec=Zeroconf)
        zc.get_service_info.return_value = MagicMock()
        zc.get_service_info.return_value.parsed_addresses.return_value = ["192.168.1.1"]

        self.mdns_service.add_service(zc, "_hue._tcp.local.", "Hue Bridge")
        self.assertIn("192.168.1.1", self.mdns_service._addresses)
        self.assertTrue(self.mdns_service._service_discovered.is_set())

    def test_remove_service(self):
        """
        Tests the remove_service method to ensure proper logging when a service is removed.
        """

        zc = MagicMock(spec=Zeroconf)

        with self.assertLogs(level="INFO") as log:
            self.mdns_service.remove_service(zc, "_hue._tcp.local.", "Hue Bridge")
            self.assertIn(
                "INFO:hue_entertainment_pykit.network.mdns:Service Hue Bridge removed",
                log.output,
            )

    def test_update_service(self):
        """
        Tests the update_service method to verify correct logging behavior when a service is updated.
        """

        zc = MagicMock(spec=Zeroconf)

        with self.assertLogs(level="INFO") as log:
            self.mdns_service.update_service(zc, "_hue._tcp.local.", "Hue Bridge")
            self.assertIn("INFO:hue_entertainment_pykit.network.mdns:Service Hue Bridge updated", log.output)

    def test_get_addresses(self):
        """
        Tests the get_addresses method to ensure it returns the list of discovered service addresses.
        """

        self.mdns_service._addresses = ["192.168.1.1"]
        self.assertEqual(self.mdns_service.get_addresses(), ["192.168.1.1"])

    def test_get_service_discovered(self):
        """
        Tests the get_service_discovered method to verify it returns the service discovery event object.
        """

        self.assertIsInstance(self.mdns_service.get_service_discovered(), Event)


if __name__ == "__main__":
    unittest.main()
