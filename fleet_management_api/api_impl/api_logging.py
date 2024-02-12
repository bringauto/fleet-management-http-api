import logging as _logging
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore


_API_LOGGER_NAME = "werkzeug"


def log_info(message: str) -> None:
    """Pass a custom info message to the API logger."""
    logger = _logging.getLogger(_API_LOGGER_NAME)
    logger.info(message)


def log_error(message: str) -> None:
    """Pass a custom error message to the API logger."""
    logger = _logging.getLogger(_API_LOGGER_NAME)
    logger.error(message)


def log_and_respond(code: int, msg: str) -> _Response:
    """Pass a custom info message to the API logger and return a connexion response with the given code and message."""
    if 200 <= code < 300:
        log_info(msg)
    else:
        log_error(msg)
    return _Response(status_code=code, content_type="text/plain", body=msg)
