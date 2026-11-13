
# app/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder where log files will be stored
LOG_DIR = BASE_DIR / "logs"

# Main log file
LOG_FILE = LOG_DIR / "weather.log"


def setup_logging():

    # 1. Create logs folder if missing
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Get the root logger
    logger = logging.getLogger()

    # 3. Set the minimum log level
    logger.setLevel(logging.DEBUG)

    # Remove handlers previously created by this setup
    for handler in logger.handlers[:]:
        if getattr(handler, "_weather_handler", False):
            logger.removeHandler(handler)
            handler.close()

    # 4. Define the log format
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Use UTC timestamps
    formatter.converter = time.gmtime

    # 5. Terminal handler
    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    console_handler._weather_handler = True

    # 6. File handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    file_handler._weather_handler = True

    # 7. Attach handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
