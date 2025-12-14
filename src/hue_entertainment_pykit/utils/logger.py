"""
This module sets up a logging system for the application. It includes configuration for logging to a file
and the console with different formats. The console output is colored based on the log level to enhance visibility.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

class LoggingUtil:
    _COLORS = {
        'TRACE': '\033[90m',
        'DEBUG': '\033[96m',
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'CRITICAL': '\033[91m',
        'ENDC': '\033[0m',
    }

    class _ColoredFormatter(logging.Formatter):
        """Formatter for colored console logs."""

        def format(self, record):
            log_message = super().format(record)
            color = LoggingUtil._COLORS.get(record.levelname, LoggingUtil._COLORS["ENDC"])
            return f"{color}{log_message}{LoggingUtil._COLORS['ENDC']}"

    @staticmethod
    def setup_logging(level: int, max_file_size: int, backup_count: int):
        """
        Sets up rotating file and colored console logging.
        """

        logger = logging.getLogger("hue_entertainment_pykit")
        logger.setLevel(level)

        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, "philipsLightsLogs.log")

        file_handler = RotatingFileHandler(
            log_file_path, mode="a", maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))
        file_handler._custom_philips_hue_handler = True  # marker
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            LoggingUtil._ColoredFormatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
        )
        logger.addHandler(console_handler)

        for handler in logger.handlers:
            handler.setLevel(level)

        return logger
