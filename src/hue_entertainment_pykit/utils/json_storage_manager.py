import logging
from typing import Any

from src.hue_entertainment_pykit.utils.file_handler import FileHandler


class JsonStorageManager:
    @staticmethod
    def save_auth_data(data: dict) -> None:
        """
        Saves authentication data to a predefined file path.

        This http_method writes the provided authentication data, such as username and client key, to a JSON file.
        This data is essential for subsequent interactions with the Philips Hue Bridge.

        Parameters:
            data (dict): A dictionary containing authentication information like username and client key to be saved.

        Note:
            The file path is obtained from the FileHandler.AUTH_FILE_PATH constant. If the file does not exist,
            it will be created.
        """
        logging.info("Saving data: {}".format(data))
        FileHandler.write_json(FileHandler.AUTH_FILE_PATH, data)
        logging.info("Saved data: {}".format(data))

    @staticmethod
    def load_auth_data() -> dict[str, Any]:
        """
        Loads authentication data from a predefined file path.

        This http_method reads a JSON file containing authentication information necessary for interacting
        with the Philips Hue Bridge. The authentication data typically includes credentials like username
        and client key.

        Returns:
            dict: A dictionary containing authentication data such as username and client key. The dictionary
            will be empty if the file does not exist or is empty.

        Note:
            The file path is obtained from the FileHandler.AUTH_FILE_PATH constant.
        """
        logging.debug("Loading AUTH data")
        read_json = FileHandler.read_json(FileHandler.AUTH_FILE_PATH)
        logging.debug("Loaded AUTH Data {}".format(read_json))
        return read_json

    @staticmethod
    def save_configuration():
        ...

    @staticmethod
    def load_configuration():
        ...