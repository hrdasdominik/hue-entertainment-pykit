import json
import logging
import os
import shutil
import unittest
from unittest.mock import patch, Mock

from api.bridge.bridge import Bridge


class TestBridge(unittest.TestCase):

    def tearDown(self):
        logging.shutdown()
        if os.path.exists('logs'):
            shutil.rmtree('logs')

    @patch('requests.get')
    def test_get_ip_with_broker_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps([
            {
                "id": "some_id",
                "internalipaddress": "192.168.0.1",
                "port": 8080
            }
        ])
        mock_get.return_value = mock_response

        bd = Bridge().get_ip_with_broker()

        self.assertEqual(bd._id, "some_id")
        self.assertEqual(bd._internal_ip_address, "192.168.0.1")
        self.assertEqual(bd._port, 8080)

    @patch('requests.get')
    def test_get_ip_with_broker_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        bd = Bridge().get_ip_with_broker()

        self.assertEqual(bd._id, "")
        self.assertEqual(bd._internal_ip_address, "")
        self.assertEqual(bd._port, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
