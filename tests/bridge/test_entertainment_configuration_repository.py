"""
Module: test_entertainment_configuration_repository.py

This module contains unit tests for the EntertainmentConfigurationRepository class. It focuses on testing
the functionality of communication with a Philips Hue Bridge for managing entertainment configurations.

Classes:
    TestEntertainmentConfigurationRepository: A collection of unit tests for testing
    the EntertainmentConfigurationRepository class.
"""

import unittest
from unittest.mock import MagicMock, patch

from hue_entertainment_pykit.bridge.entertainment_configuration_repository import (
    EntertainmentConfigurationRepository,
)
from hue_entertainment_pykit.exceptions.api_exception import ApiException
from hue_entertainment_pykit.models.bridge import Bridge
from hue_entertainment_pykit.models.entertainment_configuration import EntertainmentConfiguration
from hue_entertainment_pykit.models.payload import Payload
from tests.bridge.entertainment_configuration_mock import (
    ENTERTAINMENT_CONFIGURATION_MOCK,
)


# pylint: disable=protected-access, attribute-defined-outside-init
class TestEntertainmentConfigurationRepository(unittest.TestCase):
    """
    A suite of unit tests for the EntertainmentConfigurationRepository class.

    This class tests various functionalities of the EntertainmentConfigurationRepository, including initialization,
    sending requests to the Philips Hue Bridge, and fetching and updating entertainment configurations.

    Attributes:
        mock_bridge (MagicMock): A mock object for the Bridge class.
        repository (EntertainmentConfigurationRepository): An instance of
        the EntertainmentConfigurationRepository class for testing.
    """

    def setUp(self):
        """
        Sets up the test environment by creating mock objects and an instance of
        the EntertainmentConfigurationRepository.
        """

        self.mock_bridge = MagicMock(spec=Bridge)
        self.mock_bridge.get_ip_address.return_value = "192.168.1.2"
        self.mock_bridge.get_username.return_value = "test_username"
        self.repository = EntertainmentConfigurationRepository(self.mock_bridge)

    def test_initialization(self):
        """
        Tests the correct initialization of the EntertainmentConfigurationRepository instance.
        """
        self.assertEqual(self.repository._bridge, self.mock_bridge)
        self.assertTrue(self.repository._base_url.startswith("https://192.168.1.2"))
        self.assertIn("Content-Type", self.repository._headers)
        self.assertIn("hue-application-key", self.repository._headers)

    @patch("requests.request")
    def test_send_request(self, mock_request):
        """
        Tests the _send_request method for both successful and unsuccessful HTTP request scenarios.
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        response = self.repository._send_request("GET", "https://example.com")
        self.assertEqual(response, mock_response)

        mock_response.status_code = 404
        with self.assertRaises(ApiException):
            self.repository._send_request("GET", "https://example.com")

    @patch("requests.request")
    def test_fetch_configurations(self, mock_request):
        """
        Tests the fetch_configurations method to ensure it correctly retrieves entertainment configurations from
        the Philips Hue Bridge.
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ENTERTAINMENT_CONFIGURATION_MOCK
        mock_request.return_value = mock_response

        configs = self.repository.fetch_configurations()
        self.assertIsInstance(list(configs.values())[0], EntertainmentConfiguration)
        self.assertEqual(len(configs), 1)

    @patch("requests.request")
    def test_put_configuration(self, mock_request):
        """
        Tests the put_configuration method to verify updating a specific entertainment configuration on
        the Philips Hue Bridge.
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        payload = Payload({"id": "1", "name": "Updated Config"})
        self.repository.put_configuration(payload)
        mock_request.assert_called_with(
            "PUT",
            "https://192.168.1.2/clip/v2/resource/entertainment_configuration/1",
            headers=self.repository._headers,
            json={"name": "Updated Config"},
            verify=False,
            timeout=5,
        )


if __name__ == "__main__":
    unittest.main()
