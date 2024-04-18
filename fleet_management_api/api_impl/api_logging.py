import logging as _logging

from .api_responses import (
    text_response as _text_response,
    error as _error,
    Response as _Response
)


_API_LOGGER_NAME = "werkzeug"


def log_info(message: str) -> None:
    """Pass a custom info message to the API logger."""
    logger = _logging.getLogger(_API_LOGGER_NAME)
    logger.info(message)


def log_error(message: str) -> None:
    """Pass a custom error message to the API logger."""
    logger = _logging.getLogger(_API_LOGGER_NAME)
    logger.error(message)


def log_error_and_respond(msg: str, code: int, title: str) -> _Response:
    """Pass a custom error message to the API logger and return a connexion response with the given code, title and detail."""
    log_error(msg)
    return _error(code, msg, title)


def log_info_and_respond(msg: str) -> _Response:
    """Pass a custom info message to the API logger and return a connexion response with the given code and message."""
    log_info(msg)
    return _text_response(msg, 200)

