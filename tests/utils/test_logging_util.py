import os
import tempfile
import unittest
from unittest.mock import patch

import logging

from hue_entertainment_pykit.lowl.enums.log_level_enum import LogLevelEnum
from hue_entertainment_pykit.lowl.utils.logging_util import LoggingUtil


class TestLoggingUtil(unittest.TestCase):
    def _fresh_logger(self):
        lg = logging.Logger("test_logger")

        lg.addHandler(logging.StreamHandler())
        lg.addHandler(logging.StreamHandler())
        return lg

    def test_setup_logging_adds_rotating_file_and_colored_console(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("os.getcwd", return_value=tmp), patch(
                "logging.getLogger", return_value=self._fresh_logger()
            ) as _:
                LoggingUtil.setup_logging(
                    level=LogLevelEnum.INFO, max_file_size=12345, backup_count=7
                )

                lg = logging.getLogger()
                self.assertEqual(len(lg.handlers), 2)

                file_handler = next(h for h in lg.handlers if hasattr(h, "baseFilename"))
                console_handler = next(h for h in lg.handlers if isinstance(h, logging.StreamHandler) and not hasattr(h, "baseFilename"))

                self.assertTrue(file_handler.baseFilename.endswith(os.path.join("logs", "philipsLightsLogs.log")))
                self.assertEqual(getattr(file_handler, "maxBytes", None), 12345)
                self.assertEqual(getattr(file_handler, "backupCount", None), 7)

                self.assertTrue(getattr(file_handler, "_custom_philips_hue_handler", False))

                self.assertIsInstance(console_handler.formatter, LoggingUtil._ColoredFormatter)

                self.assertTrue(os.path.isdir(os.path.join(tmp, "logs")))

    def test_setup_logging_sets_levels_on_logger_and_handlers(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("os.getcwd", return_value=tmp), patch(
                "logging.getLogger", return_value=self._fresh_logger()
            ) as _:
                LoggingUtil.setup_logging(
                    level=LogLevelEnum.DEBUG, max_file_size=1000, backup_count=1
                )
                lg = logging.getLogger()
                self.assertEqual(lg.level, LogLevelEnum.DEBUG.value)
                self.assertGreaterEqual(len(lg.handlers), 2)
                for h in lg.handlers:
                    self.assertEqual(h.level, LogLevelEnum.DEBUG.value)

    def test_colored_formatter_wraps_message_with_ansi_codes(self):
        fmt = LoggingUtil._ColoredFormatter("%(levelname)s %(message)s")
        record = logging.LogRecord(
            name="x", level=logging.INFO, pathname=__file__, lineno=1, msg="hello", args=(), exc_info=None
        )
        out = fmt.format(record)
        start = LoggingUtil._COLORS["INFO"]
        end = LoggingUtil._COLORS["ENDC"]
        self.assertTrue(out.startswith(start))
        self.assertTrue(out.endswith(end))

        self.assertIn("INFO hello", out)


if __name__ == "__main__":
    unittest.main()