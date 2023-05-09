import logging
import os

log_file_path = "logs/philipsLightsLogs.log"

if not os.path.exists(log_file_path):
    open(log_file_path, 'w').close()
    print(f"Log file created at {log_file_path}")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
