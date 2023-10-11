import json
import logging
import os
import shutil
import unittest
from unittest.mock import patch, Mock

from api.light.light_model import Light
from api.light.light_repository import LightRepository


class TestLightRepository(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("logs"):
            os.makedirs("logs")
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        LightRepository.instance = None

    def tearDown(self):
        logging.shutdown()
        if os.path.exists('logs'):
            shutil.rmtree('logs')

    @patch('api.bridge.bridge.Bridge')
    @patch('requests.request')
    def test_get_light_without_identification_success(self, mock_request,
                                                      bridge):
        with open("lights_mock.json") as f:
            self.mock_response.json.return_value = json.loads(f.read())
        mock_request.return_value = self.mock_response

        light_repo = LightRepository(bridge)

        lights = light_repo.get_lights()

        self.assertEqual(len(lights), 2)
        self.assertIsInstance(lights[0], Light)
        self.assertIsInstance(lights[1], Light)

    @patch('api.bridge.bridge.Bridge')
    @patch('requests.request')
    def test_get_light_with_identification_success(self, mock_request, bridge):
        with open("light_mock.json") as f:
            self.mock_response.json.return_value = json.loads(f.read())
            target_light = Light(self.mock_response.json()["data"][0])
        mock_request.return_value = self.mock_response

        light_repo = LightRepository(bridge)

        lights = light_repo.get_lights("b6f8a28b-cc70-4917-8dbd-25deb8a2b40f")

        self.assertEqual(len(lights), 1)
        self.assertIsInstance(lights[0], Light)
        self.assertEqual(lights[0], target_light)

    @patch('api.bridge.bridge.Bridge')
    @patch('requests.request')
    def test_put_light_success(self, mock_request, bridge):
        with open("light_mock.json") as f:
            data = json.loads(f.read())["data"][0]
            light = Light(data)
        mock_request.return_value = self.mock_response

        light_repo = LightRepository(bridge)

        light_repo.put_light(light)

        mock_request.assert_called_once_with(
            "PUT",
            url=light_repo.get_default_url() + f"resource/light/{light.id}",
            headers=light_repo.get_headers(),
            json=light.to_dict()
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
