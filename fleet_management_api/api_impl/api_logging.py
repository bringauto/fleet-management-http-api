import logging as _logging
import connexion as _connexion  # type: ignore

from fleet_management_api.api_impl.api_responses import (
    text_response as _text_response,
    error as _error,
    Response as _Response,
)
from fleet_management_api.logs import LOGGER_NAME as _LOGGER_NAME


logger = _logging.getLogger(_LOGGER_NAME)


def log_info(message: str) -> None:
    """Pass a custom info message to the API logger."""
    logger.info(str(message))


def log_debug(message: str) -> None:
    """Pass a custom debug message to the API logger."""
    logger.debug(str(message))


def log_warning(message: str) -> None:
    """Pass a custom warning message to the API logger."""
    logger.warning(str(message))


def log_error(message: str) -> None:
    """Pass a custom error message to the API logger."""
    logger.error(str(message))



def log_warning_or_error_and_respond(msg: str, code: int, title: str) -> _Response:
    """Pass a custom error message to the API logger and return a connexion response with the given code, title and detail."""
    if code < 500:
        log_warning(msg)
    else:
        log_error(msg)
    return _error(code, str(msg), title)


def log_warning_and_respond(msg: str, code: int, title: str) -> _Response:
    """Pass a custom warning message to the API logger and return a connexion response with the given code, title and detail."""
    log_warning(msg)
    return _error(code, str(msg), title)


def log_info_and_respond(msg: str, code: int = 200, title: str = "") -> _Response:
    """Pass a custom info message to the API logger and return a connexion response with the given code and message."""
    log_info(msg)
    if code == 200:
        return _text_response(msg, code)
    return _error(code, str(msg), title)


def log_invalid_request_body_format() -> _Response:
    return log_warning_or_error_and_respond(
        f"Invalid request format: {_connexion.request.data}. JSON is required.",
        400,
        title="Invalid request format",
    )
