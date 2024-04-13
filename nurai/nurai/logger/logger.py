import inspect
import logging
from logging.handlers import RotatingFileHandler
import os
from colorlog import ColoredFormatter
from configuration import logging_path


def setup_logger():
    """Set up a logger with preconfigured settings, automatically deducing the package name."""
    # Inspect the stack to find the caller's module name
    caller_frame = inspect.stack()[1]
    module = inspect.getmodule(caller_frame[0])
    package_name = module.__name__.split(".")[0] if module else "default"

    log_directory = os.path.join(logging_path, package_name)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = os.path.join(log_directory, "log.log")

    # Create or retrieve a logger
    logger = logging.getLogger(package_name)
    # Check if the logger already has handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # Adjust as needed

        # Create a rotating file handler
        handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5)

        # Define a color coded formatter with timestamp and function name
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
