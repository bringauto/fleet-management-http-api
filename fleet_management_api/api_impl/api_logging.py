import logging


API_LOGGER_NAME = "werkzeug"


def log_info(message: str) -> None:
    logger = logging.getLogger(API_LOGGER_NAME)
    logger.info(message)

def log_error(message: str) -> None:
    logger = logging.getLogger(API_LOGGER_NAME)
    logger.error(message)