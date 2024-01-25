"""
This module sets up a logging system for the application. It includes configuration for logging to a file
and the console with different formats. The console output is colored based on the log level to enhance visibility.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

COLORS = {
    "WARNING": "\033[93m",
    "INFO": "\033[94m",
    "DEBUG": "\033[92m",
    "CRITICAL": "\033[91m",
    "ERROR": "\033[91m",
    "ENDC": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """
    This custom formatter colors the log messages based on their severity level.
    It extends the logging.Formatter class and overrides the format method to add color codes.
    """

    def format(self, record):
        log_message = super().format(record)
        return f"{COLORS.get(record.levelname, COLORS['ENDC'])}{log_message}{COLORS['ENDC']}"


def setup_logging(
    level: int,
    max_file_size: int,
    backup_count: int,
):
    """
    Configures the logging system for the library with file and console handlers, using a rotating log file.

    This function sets up a rotating log file in the 'logs' directory within the user's project's current working
    directory.
    The log file rotates when it reaches the specified maximum size, preserving a set number of backup files.

    The console output is enhanced with colored log levels for improved readability. It verifies if the root logger has
    existing handlers to avoid duplicate configurations.

    The function is designed to be idempotent, allowing for repeated calls without introducing side effects like
    multiple handlers.

    Note:
        Importing this library triggers the creation of a 'logs' directory in the current working directory.
        Users desiring a different
        logging setup should configure their logging prior to importing this library.

    Args:
        level (int): The logging level, such as logging.DEBUG, logging.INFO, etc.
        max_file_size (int): Maximum size in bytes for the log file before it rotates. There are no default values;
        users must specify this.
        backup_count (int): Number of backup log files to retain. Users must provide this value as there are
        no defaults.
    """

    if not logging.getLogger().hasHandlers():
        logs_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)

        log_file_path = os.path.join(logs_dir, "philipsLightsLogs.log")

        file_handler = RotatingFileHandler(
            log_file_path, mode="a", maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)

        logging.basicConfig(level=level, handlers=[file_handler, console_handler])
