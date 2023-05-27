"""_summary_"""

import logging
import os

LOG_FILE_PATH = "logs/philipsLightsLogs.log"

if not os.path.exists(LOG_FILE_PATH):
    open(LOG_FILE_PATH, 'w', encoding="utf-8").close()
    print(f"Log file created at {LOG_FILE_PATH}")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
