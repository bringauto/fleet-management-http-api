import logging as _logging
import connexion as _connexion  # type: ignore

from .api_responses import (
    text_response as _text_response,
    error as _error,
    Response as _Response,
)
from ..logs import LOGGER_NAME


logger = _logging.getLogger(LOGGER_NAME)


def log_info(message: str) -> None:
    """Pass a custom info message to the API logger."""
    logger.info(message)


def log_debug(message: str) -> None:
    """Pass a custom debug message to the API logger."""
    logger.debug(message)


def log_warning(message: str) -> None:
    """Pass a custom warning message to the API logger."""
    logger.warning(message)


def log_error(message: str) -> None:
    """Pass a custom error message to the API logger."""
    logger.error(message)


def log_error_and_respond(msg: str, code: int, title: str) -> _Response:
    """Pass a custom error message to the API logger and return a connexion response with the given code, title and detail."""
    log_error(msg)
    return _error(code, msg, title)


def log_info_and_respond(msg: str) -> _Response:
    """Pass a custom info message to the API logger and return a connexion response with the given code and message."""
    log_info(msg)
    return _text_response(msg, 200)


def log_invalid_request_body_format() -> _Response:
    return log_error_and_respond(
        f"Invalid request format: {_connexion.request.data}. JSON is required.",
        400,
        title="Invalid request format",
    )
