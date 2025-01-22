"""
This module sets up a logging system for the application. It includes configuration for logging to a file
and the console with different formats. The console output is colored based on the log level to enhance visibility.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

COLORS = {
    "DEBUG": "\033[92m",
    "INFO": "\033[94m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[91m",
    "ENDC": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """
    This custom formatter colors the log messages based on their severity level.
    It extends the logging.Formatter class and overrides the format http_method to add color codes.
    """

    def format(self, record):
        log_message = super().format(record)
        return f"{COLORS.get(record.levelname, COLORS['ENDC'])}{log_message}{COLORS['ENDC']}"


def setup_logging(
        level: int = logging.INFO,
        max_file_size: int = 1024 * 1024 * 5,
        backup_count: int = 3,
        reconfigure: bool = False,
):
    """
    Configures or reconfigures the logging system for the library.

    Args:
        level (int): The logging level, such as logging.DEBUG, logging.INFO, etc.
        max_file_size (int): Maximum size in bytes for the log file before it rotates.
        backup_count (int): Number of backup log files to retain.
        reconfigure (bool): Whether to replace existing handlers. Default is False.
    """

    logger = logging.getLogger()
    logger.setLevel(level)

    if reconfigure:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logs_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_file_path = os.path.join(logs_dir, "philipsLightsLogs.log")

    file_handler = RotatingFileHandler(
        log_file_path, mode="a", maxBytes=max_file_size, backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
