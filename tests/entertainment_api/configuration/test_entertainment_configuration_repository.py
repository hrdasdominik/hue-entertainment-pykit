import json
import logging
import os
import shutil
import unittest
from unittest.mock import patch, Mock

from entertainment_api.configuration.entertainment_configuration_model import \
    EntertainmentConfiguration
from entertainment_api.configuration.entertainment_configuration_repository import \
    EntertainmentConfigurationRepository


class TestEntertainmentConfigurationRepository(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("logs"):
            os.makedirs("logs")
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        EntertainmentConfigurationRepository.instance = None

    def tearDown(self):
        logging.shutdown()
        if os.path.exists('logs'):
            shutil.rmtree('logs')

    @patch("api.bridge.bridge.Bridge")
    @patch("requests.request")
    def test_get_config_success(self, mock_request, bridge):
        with open("mocks.json") as f:
            self.mock_response.json.return_value = json.loads(f.read())

        mock_request.return_value = self.mock_response

        repo = EntertainmentConfigurationRepository(bridge)

        entertainments = repo.get_configuration()

        self.assertEqual(len(entertainments), 3)
        self.assertIsInstance(entertainments[0], EntertainmentConfiguration)
        self.assertIsInstance(entertainments[1], EntertainmentConfiguration)
        self.assertIsInstance(entertainments[2], EntertainmentConfiguration)

    @patch('api.bridge.bridge.Bridge')
    @patch('requests.request')
    def test_get_config_with_identification_success(self, mock_request, bridge):
        with open("mock.json") as f:
            self.mock_response.json.return_value = json.loads(f.read())
            target_entertainment = EntertainmentConfiguration(
                self.mock_response.json()["data"][0])
        mock_request.return_value = self.mock_response

        repo = EntertainmentConfigurationRepository(bridge)

        entertainments = repo.get_configuration("2022ffc4-1b73-4a43-b376-4c45369bf207")

        self.assertEqual(len(entertainments), 1)
        self.assertIsInstance(entertainments[0], EntertainmentConfiguration)
        self.assertEqual(entertainments[0], target_entertainment)


if __name__ == '__main__':
    unittest.main()
