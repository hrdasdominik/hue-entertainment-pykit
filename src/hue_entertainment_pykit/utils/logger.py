"""
This module sets up a logging system for the application. It includes configuration for logging to a file
and the console with different formats. The console output is colored based on the log level to enhance visibility.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


class LoggingUtil:  # pylint: disable=too-few-public-methods
    """Utility namespace for setting up library logging.

    This is intentionally a small, static helper (no instances), so pylint's
    `too-few-public-methods` rule is not meaningful here.
    """

    COLORS = {
        "TRACE": "\033[90m",
        "DEBUG": "\033[96m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[91m",
        "ENDC": "\033[0m",
    }

    class _ColoredFormatter(logging.Formatter):
        """Formatter for colored console logs."""

        def format(self, record: logging.LogRecord) -> str:
            log_message = super().format(record)
            color = LoggingUtil.COLORS.get(record.levelname, LoggingUtil.COLORS["ENDC"])
            return f"{color}{log_message}{LoggingUtil.COLORS['ENDC']}"

    @staticmethod
    def setup_logging(level: int, max_file_size: int, backup_count: int):
        """
        Sets up rotating file and colored console logging.
        """

        for noisy in ("urllib3", "requests", "zeroconf"):
            logging.getLogger(noisy).setLevel(logging.WARNING)

        logger = logging.getLogger("hue_entertainment_pykit")
        logger.setLevel(level)
        logger.propagate = False

        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, "philipsLightsLogs.log")

        file_handler = RotatingFileHandler(
            log_file_path, mode="a", maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
        )
        file_handler.custom_philips_hue_handler = True
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            LoggingUtil._ColoredFormatter(
                "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
            )
        )
        logger.addHandler(console_handler)

        for handler in logger.handlers:
            handler.setLevel(level)

        return logger
