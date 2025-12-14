"""
Module: test_file_handler.py

This module contains unit tests for the FileHandler class, focusing on testing its functionality for
reading from and writing to JSON files, commonly used for configuration and data storage.

Classes:
    TestFileHandler: A suite of unit tests for the FileHandler class.
"""

import json
import os
import unittest
from unittest.mock import patch, mock_open

from hue_entertainment_pykit.utils.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    """
    Test suite for the FileHandler class, which handles file operations for JSON data.

    This class tests the read and write functionalities provided by FileHandler, ensuring accurate and
    reliable file operations for JSON formatted data.
    """

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_read_json(self, mock_file, mock_exists):
        """
        Tests the read_json method to verify reading JSON data from files and handling file not found scenarios.
        """

        # pylint: disable=unused-argument

        mock_exists.return_value = True
        result = FileHandler.read_json(FileHandler.AUTH_FILE_PATH)
        self.assertEqual(result, {"test": "data"})

        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            FileHandler.read_json(FileHandler.AUTH_FILE_PATH)

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_json(self, mock_file, mock_makedirs):
        """
        Tests the write_json method to ensure correct writing of JSON data to files and
        creation of necessary directories.
        """

        data = {"key": "value"}
        FileHandler.write_json(FileHandler.BRIDGE_FILE_PATH, data)

        mock_makedirs.assert_called_with(
            os.path.dirname(FileHandler.BRIDGE_FILE_PATH), exist_ok=True
        )

        mock_file.assert_called_with(
            FileHandler.BRIDGE_FILE_PATH, "w", encoding="utf-8"
        )

        handle = mock_file()
        written_data = handle.write.call_args_list
        written_content = "".join(call_arg[0][0] for call_arg in written_data)
        expected_content = json.dumps(data)
        self.assertEqual(written_content, expected_content)


if __name__ == "__main__":
    unittest.main()
