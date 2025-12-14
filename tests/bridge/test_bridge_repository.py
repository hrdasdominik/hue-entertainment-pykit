"""
Module: test_bridge_repository.py

This module contains the unit tests for the BridgeRepository class in the bridge.bridge_repository module.
It covers various scenarios including initialization, authentication data handling, base URL setting,
HTTP request handling, and fetching various pieces of bridge data. Mocking is extensively used to isolate the tests from
external dependencies like file systems and web requests.

Classes:
    TestBridgeRepository: A collection of unit tests for testing the BridgeRepository class.
"""

import logging
import os
import shutil
import unittest
from unittest.mock import patch, MagicMock

from requests import Response

from hue_entertainment_pykit.bridge.bridge_repository import BridgeRepository
from hue_entertainment_pykit.exceptions.bridge_exception import BridgeException
from hue_entertainment_pykit.utils.file_handler import FileHandler
from hue_entertainment_pykit.utils.status_code import StatusCode


# pylint: disable=protected-access, attribute-defined-outside-init
class TestBridgeRepository(unittest.TestCase):
    """
    The TestBridgeRepository class contains a suite of unit tests for testing the functionality of
    the BridgeRepository class.

    This class tests various functionalities of the BridgeRepository, including initialization, loading and
    saving authentication data, setting the base URL, making HTTP requests, and fetching bridge-specific data like
    software version, application ID, and bridge name.

    Attributes:
        mock_request (MagicMock): A mock object for the requests.request function.
        repo (BridgeRepository): An instance of the BridgeRepository class for testing.

    Methods:
        setUp: Sets up necessary mocks and instances before each test method.
        tearDown: Cleans up after each test method.
        test_initialization: Tests the initialization of the BridgeRepository.
        test_load_auth_data: Tests the _load_auth_data method.
        test_save_auth_data: Tests the _save_auth_data method.
        test_set_base_url: Tests the _set_base_url method.
        test_make_request_successful: Tests the _make_request method for a successful scenario.
        test_make_request_no_base_url: Tests the _make_request method for a scenario where the base URL is not set.
        test_make_request_bad_response: Tests the _make_request method for a scenario with a bad response.
        ... (other test methods) ...
    """

    # pylint: disable=too-many-instance-attributes

    def setUp(self):
        """
        Sets up the test environment by patching necessary functions and creating mock objects.
        """

        self.mock_request_patcher = patch("requests.request")
        self.mock_request = self.mock_request_patcher.start()
        self.mock_response = MagicMock(spec=Response)
        self.mock_response.status_code = StatusCode.OK.value
        self.mock_response.json.return_value = {"success": True}
        self.mock_response.headers = {"Content-Type": "application/json"}
        self.mock_request.return_value = self.mock_response

        self.repo = BridgeRepository()
        self.repo.set_base_url("")

    def tearDown(self):
        """
        Cleans up the test environment, including shutting down logging and removing created directories.
        """

        patch.stopall()

        logging.shutdown()
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def test_initialization(self):
        """
        Tests the correct initialization of the BridgeRepository instance.
        """

        self.assertEqual(self.repo.get_headers()["Content-Type"], "application/json")
        self.assertEqual(self.repo.get_base_url(), "https://")

    @patch("hue_entertainment_pykit.utils.file_handler.FileHandler.read_json")
    def test_load_auth_data(self, mock_read_json):
        """
        Tests the loading of authentication data from a JSON file using the _load_auth_data method.
        """

        mock_read_json.return_value = {"username": "user", "clientkey": "key"}
        data = self.repo._load_auth_data()
        self.assertEqual(data, {"username": "user", "clientkey": "key"})

    @patch("hue_entertainment_pykit.utils.file_handler.FileHandler.write_json")
    def test_save_auth_data(self, mock_write_json):
        """
        Tests the _save_auth_data method to ensure it correctly writes authentication data to a JSON file.
        """

        auth_data = {"username": "user", "clientkey": "key"}
        self.repo._save_auth_data(auth_data)
        mock_write_json.assert_called_with(FileHandler.AUTH_FILE_PATH, auth_data)

    def test_set_base_url(self):
        """
        Tests the _set_base_url method to verify that it correctly sets the base URL for the BridgeRepository instance.
        """

        self.repo.set_base_url("192.168.1.1")
        self.assertEqual(self.repo.get_base_url(), "https://192.168.1.1")

    def test_make_request_successful(self):
        """
        Tests the _make_request method for a successful HTTP request scenario, verifying the response status code.
        """

        self.repo.set_base_url("192.168.1.1")
        response = self.repo._make_request("GET", "/endpoint")
        self.assertEqual(response.status_code, StatusCode.OK.value)

    def test_make_request_no_base_url(self):
        """
        Tests the _make_request method to ensure it raises a ValueError when the base URL is not set.
        """

        with self.assertRaises(ValueError):
            self.repo.set_base_url("")
            self.repo._make_request("GET", "/endpoint")

    def test_make_request_bad_response(self):
        """
        Tests the _make_request method for a scenario where the HTTP request returns a bad response,
        ensuring it raises the appropriate exception.
        """

        self.mock_response.status_code = 500
        self.repo.set_base_url("192.168.1.1")
        with self.assertRaises(Exception):  # Replace with your specific exception class
            self.repo._make_request("GET", "/endpoint")

    def test_register_app_and_fetch_username_client_key_already_loaded(self):
        """
        Tests the _register_app_and_fetch_username_client_key method to ensure it returns
        existing authentication data without making a new registration request.
        """

        self.mock_load_auth_data = patch.object(self.repo, "_load_auth_data").start()
        self.mock_save_auth_data = patch.object(self.repo, "_save_auth_data").start()
        self.mock_load_auth_data.return_value = {"username": "user", "clientkey": "key"}
        username, client_key = self.repo._register_app_and_fetch_username_client_key()
        self.assertEqual(username, "user")
        self.assertEqual(client_key, "key")
        self.mock_save_auth_data.assert_not_called()

    def test_register_app_and_fetch_username_client_key_success(self):
        """
        Tests the _register_app_and_fetch_username_client_key method to verify successful registration
        and fetching of new authentication data.
        """

        self.repo.set_base_url("192.168.1.1")
        self.mock_load_auth_data = patch.object(self.repo, "_load_auth_data").start()
        self.mock_save_auth_data = patch.object(self.repo, "_save_auth_data").start()
        self.mock_load_auth_data.return_value = {}
        self.mock_response.json.return_value = [
            {"success": {"username": "new_user", "clientkey": "new_key"}}
        ]

        username, client_key = self.repo._register_app_and_fetch_username_client_key()
        self.assertEqual(username, "new_user")
        self.assertEqual(client_key, "new_key")
        self.mock_save_auth_data.assert_called_once_with(
            {"username": "new_user", "clientkey": "new_key"}
        )

    def test_register_app_and_fetch_username_client_key_error(self):
        """
        Tests the _register_app_and_fetch_username_client_key method to ensure it raises
        a BridgeException when the registration process fails.
        """

        self.repo.set_base_url("192.168.1.1")
        self.mock_load_auth_data = patch.object(self.repo, "_load_auth_data").start()
        self.mock_save_auth_data = patch.object(self.repo, "_save_auth_data").start()
        self.mock_load_auth_data.return_value = {}
        self.mock_response.json.return_value = [
            {"error": {"description": "registration failed"}}
        ]

        with self.assertRaises(BridgeException):
            self.repo._register_app_and_fetch_username_client_key()

    def test_fetch_swversion(self):
        """
        Tests the _fetch_swversion method to verify it correctly fetches and returns the software version of the bridge.
        """

        self.mock_response.json.return_value = {"swversion": "1935144040"}
        self.repo.set_base_url("testbaseurl.com")

        swversion = self.repo._fetch_swversion()
        self.assertEqual(swversion, 1935144040)

    def test_fetch_hue_application_id(self):
        """
        Tests the _fetch_hue_application_id method to ensure it correctly retrieves the Hue Application ID
        from the bridge.
        """

        self.mock_response.headers["hue-application-id"] = "application_id"
        self.repo.set_base_url("testbaseurl.com")

        app_id = self.repo._fetch_hue_application_id()
        self.assertEqual(app_id, "application_id")

    def test_fetch_bridge_name(self):
        """
        Tests the _fetch_bridge_name method to verify it correctly fetches and returns the name of the bridge.
        """

        self.mock_response.json.return_value = {
            "data": [{"metadata": {"name": "Hue Bridge"}}]
        }
        self.repo.set_base_url("testbaseurl.com")

        bridge_name = self.repo._fetch_bridge_name("0")
        self.assertEqual(bridge_name, "Hue Bridge")

    def test_fetch_bridge_id_and_rid(self):
        """
        Tests the _fetch_bridge_id_and_rid method to ensure it correctly fetches and returns the bridge ID and
        resource ID.
        """

        self.repo.set_base_url("testbaseurl.com")
        self.mock_response.json.return_value = {
            "data": [{"id": "bridge-id", "owner": {"rid": "resource-id"}}]
        }

        bridge_id, rid = self.repo._fetch_bridge_id_and_rid()
        self.assertEqual(bridge_id, "bridge-id")
        self.assertEqual(rid, "resource-id")

    def test_fetch_bridge_rid(self):
        """
        Tests the _fetch_bridge_rid method to verify it correctly retrieves the resource identifier of the bridge.
        """

        self.repo.set_base_url("testbaseurl.com")
        self.mock_response.json.return_value = {
            "data": [{"owner": {"rid": "resource-id"}}]
        }

        rid = self.repo._fetch_bridge_rid()
        self.assertEqual(rid, "resource-id")

    def test_fetch_bridge_data(self):
        """
        Tests the fetch_bridge_data method to ensure it correctly aggregates various pieces of data about the bridge.
        """

        self.mock_fetch_bridge_id_and_rid = patch.object(
            self.repo, "_fetch_bridge_id_and_rid"
        ).start()
        self.mock_fetch_bridge_name = patch.object(
            self.repo, "_fetch_bridge_name"
        ).start()
        self.mock_fetch_swversion = patch.object(self.repo, "_fetch_swversion").start()
        self.mock_fetch_hue_application_id = patch.object(
            self.repo, "_fetch_hue_application_id"
        ).start()
        self.mock_register_app_and_fetch_username_client_key = patch.object(
            self.repo, "_register_app_and_fetch_username_client_key"
        ).start()
        self.mock_register_app_and_fetch_username_client_key.return_value = (
            "username",
            "clientkey",
        )
        self.mock_fetch_hue_application_id.return_value = "hue-app-id"
        self.mock_fetch_swversion.return_value = 1935144040
        self.mock_fetch_bridge_name.return_value = "Hue Bridge"
        self.mock_fetch_bridge_id_and_rid.return_value = ("bridge-id", "resource-id")

        address = "192.168.1.2"
        data = self.repo.fetch_bridge_data(address)

        expected_data = {
            "id": "bridge-id",
            "rid": "resource-id",
            "internalipaddress": address,
            "swversion": 1935144040,
            "username": "username",
            "hue-application-id": "hue-app-id",
            "clientkey": "clientkey",
            "name": "Hue Bridge",
        }

        self.assertEqual(data, expected_data)
        self.mock_register_app_and_fetch_username_client_key.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
