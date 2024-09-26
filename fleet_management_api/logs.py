from __future__ import annotations
import logging.handlers
import os
import logging.config

from typing import TypeVar, Mapping


T = TypeVar("T", bound=Mapping)


LOGGER_NAME = "werkzeug"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


log_level_by_verbosity = {False: logging.WARNING, True: logging.DEBUG}


def configure_logging(component_name: str, config: dict) -> None:
    """Configure the logging for the application.

    The component name is written in the log messages to identify the source of the log message.

    The logging configuration is read from a JSON file. If the file is not found, a default configuration is used.
    """
    try:
        config["logging"]
        logger = logging.getLogger(LOGGER_NAME)
        verbose: bool = config["logging"]["verbose"]
        logger.setLevel(log_level_by_verbosity[verbose])

        # create formatter
        formatter = logging.Formatter(_log_format(component_name), datefmt=_DATE_FORMAT)

        # file handler
        file_path = os.path.join(
            config["logging"]["log-path"], _log_file_name(component_name) + ".log"
        )
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=10485760, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # console handler
        if verbose:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    except Exception as e:
        logging.error(f"{component_name}: Could not configure logging. {e}")


def _log_format(component_name: str) -> str:
    log_component_name = "-".join(component_name.lower().split())
    return f"[%(asctime)s.%(msecs)03d] [{log_component_name}] [%(levelname)s]\t %(message)s"


def _log_file_name(component_name: str) -> str:
    return "_".join(component_name.lower().split())
