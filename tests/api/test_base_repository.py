import logging
import os
import shutil
import unittest
from unittest.mock import patch, mock_open, Mock

from api.base_repository import BaseRepository


class TestBaseRepository(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("logs"):
            os.makedirs("logs")
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_open = mock_open()

    def tearDown(self):
        logging.shutdown()
        if os.path.exists('logs/'):
            shutil.rmtree('logs/')

    @patch('api.bridge.bridge.Bridge')
    @patch('os.path.exists', return_value=True)
    def test_generate_key_loads_existing_key(self, mock_exists, bridge):
        read_data = '{"username": "existing_username", "clientkey": "existing_clientkey"}'
        self.mock_open = mock_open(read_data=read_data)

        with patch('builtins.open', self.mock_open):
            base_repo: BaseRepository = BaseRepository(bridge)
            base_repo.generate_key()

        self.assertEqual(base_repo.get_username(), 'existing_username')
        self.assertEqual(base_repo.get_client_key(), 'existing_clientkey')

    @patch('api.bridge.bridge.Bridge')
    @patch('os.path.exists', return_value=False)
    @patch('requests.request')
    def test_generate_key_generates_new_key(self, mock_request, mock_exists,
                                            bridge):
        self.mock_response.json.return_value = [{
            "success": {"username": "new_username",
                        "clientkey": "new_clientkey"}}]

        mock_request.return_value = self.mock_response

        with patch('builtins.open', self.mock_open):
            base_repo: BaseRepository = BaseRepository(bridge)
            base_repo.generate_key()

        self.assertEqual(base_repo.get_username(), 'new_username')
        self.assertEqual(base_repo.get_client_key(), 'new_clientkey')
        self.mock_open().write.assert_called_once_with(
            '{"username": "new_username", "clientkey": "new_clientkey"}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
