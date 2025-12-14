"""
This module provides the FileHandler class, a utility for handling file operations with a focus on JSON data.
The class offers functionalities for reading from and writing to JSON files, which are commonly used for
storing configuration and authentication data.

The FileHandler class simplifies the process of interacting with the file system for JSON data handling,
making it convenient to store and retrieve data such as application settings, user preferences, or
system configurations. It abstracts file operations, providing a straightforward interface for data
access and persistence.

Class:
- FileHandler: A utility class for reading and writing JSON files, with methods to handle JSON data
  storage and retrieval efficiently.
"""

import json
import os
from typing import Any, Dict


class FileHandler:
    """
    A utility class for handling file operations, particularly for reading from and writing to JSON files.

    This class provides static methods to read data from and write data to JSON files. It is used
    primarily for managing authentication and bridge data in JSON format.

    Class Attributes:
        AUTH_FILE_PATH (str): The file path for storing authentication data.
        BRIDGE_DATA_FILE (str): The file path for storing bridge data.

    Methods:
        read_json: Reads data from a JSON file and returns it as a dictionary.
        write_json: Writes a dictionary to a JSON file.
    """

    AUTH_FILE_PATH = os.path.join(os.getcwd(), "data", "auth.json")
    BRIDGE_FILE_PATH = os.path.join(os.getcwd(), "data", "bridge.json")

    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any] | None:
        """
        Reads a JSON file and returns its contents as a dictionary.

        If the file does not exist, an empty dictionary is returned. This method is primarily used to read
        configuration and authentication data from a JSON file.

        Parameters:
            file_path (str): The path to the JSON file to be read.

        Returns:
            dict: The contents of the JSON file as a dictionary.
            If the file does not exist, returns an empty dictionary.
        """
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        raise FileNotFoundError(file_path)

    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any]):
        """
        Writes a dictionary to a JSON file.

        If the directory in the file path does not exist, it is created. This method is primarily used to write
        configuration and authentication data to a JSON file.

        Parameters:
            file_path (str): The path to the JSON file where the data will be written.
            data (dict): The data to be written to the file, in dictionary format.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)
