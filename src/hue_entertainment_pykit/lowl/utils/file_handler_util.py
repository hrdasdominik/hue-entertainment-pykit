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
import logging
import os
from ipaddress import IPv4Address
from typing import Any

from pydantic import BaseModel

from hue_entertainment_pykit.lowl.models.bridge.bridge_api_hue import BridgeApiHue

logger = logging.getLogger(__name__)

class FileHandlerUtil:
    """
    A utility class for handling file operations, particularly for reading from and writing to JSON files.

    This class provides static methods to read data from and write data to JSON files. It is used
    primarily for managing authentication and clients data in JSON format.

    Class Attributes:
        AUTH_FILE_PATH (str): The file path for storing authentication data.
        BRIDGE_DATA_FILE (str): The file path for storing clients data.

    Methods:
        read_json: Reads data from a JSON file and returns it as a dictionary.
        write_json: Writes a dictionary to a JSON file.
    """

    BRIDGE_API_PATH = os.path.join(os.getcwd(), "data", "bridge_api.json")

    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def read_json(file_path: str) -> dict[str, Any] | None:
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
        logger.trace("Trying to read JSON file %s", file_path)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                logger.trace("Read JSON file: %s", data)
                return data
        logger.error("File does not exist: %s", file_path)
        raise FileNotFoundError(file_path)

    @staticmethod
    def write_json(file_path: str, data: Any) -> None:
        """
        Writes JSON-serializable data (dict/list) or a Pydantic BaseModel to a JSON file.

        If the directory in the file path does not exist, it is created. This method is primarily used to write
        configuration and authentication data to a JSON file.

        Parameters:
            file_path (str): The path to the JSON file where the data will be written.
            data (Any): A Pydantic BaseModel or JSON-serializable dict/list to be written to the file.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if isinstance(data, BaseModel):
            payload = data.model_dump()
        else:
            payload = data

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)

    @staticmethod
    def save_bridge_api(ip_address: IPv4Address, data: BridgeApiHue):
        try:
            file = FileHandlerUtil.read_json(FileHandlerUtil.BRIDGE_API_PATH)
        except FileNotFoundError:
            file = {}

        file[str(ip_address)] = data.model_dump()

        logger.debug('Saving bridge api data: %s', data)
        FileHandlerUtil.write_json(FileHandlerUtil.BRIDGE_API_PATH, file)
        logger.debug('Saved successfully bridge api data')

    @staticmethod
    def load_bridge_api(ip_address: IPv4Address) -> BridgeApiHue:
        logger.debug('Trying to load bridge api data')
        data = FileHandlerUtil.read_json(FileHandlerUtil.BRIDGE_API_PATH)
        data = data[str(ip_address)]
        api = BridgeApiHue(**data)
        logger.debug('Loaded successfully bridge api data')
        return api
