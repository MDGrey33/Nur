# filename: logger.py

from loguru import logger
import os
from datetime import datetime
from configuration import logging_path


class _Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_Logger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        # Remove all existing handlers
        logger.remove()

        # Ensure the logging path exists
        if not os.path.exists(logging_path):
            os.makedirs(logging_path)

        # Prepare the log file path with a timestamp to avoid overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(logging_path, f"app_log_{timestamp}.log")

        # Define the log format
        file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"

        # Add only the file handler with rotation
        logger.add(log_file_path, rotation="10 MB", format=file_format, level="DEBUG")
        logger.info(f"Logging to file: {log_file_path}")

    def __getattr__(self, name):
        # Delegate method calls to the underlying Loguru logger
        return getattr(logger, name)


# Singleton instantiation
logging = _Logger()
