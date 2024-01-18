import logging
from connexion.lifecycle import ConnexionResponse


API_LOGGER_NAME = "werkzeug"


def log_info(message: str) -> None:
    logger = logging.getLogger(API_LOGGER_NAME)
    logger.info(message)

def log_error(message: str) -> None:
    logger = logging.getLogger(API_LOGGER_NAME)
    logger.error(message)

def log_and_respond(code: int, msg: str) -> ConnexionResponse:
    if 200 <= code < 300:
        log_info(msg)
    else:
        log_error(msg)
    return ConnexionResponse(status_code=code, content_type="text/plain", body=msg)
