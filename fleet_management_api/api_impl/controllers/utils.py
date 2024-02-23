import connexion as _connexion  # type: ignore
from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

import fleet_management_api.api_impl.api_logging as _api_logging


def log_invalid_request_body_format() -> _Response:
    return _api_logging.log_and_respond(
        400, f"Invalid request format: {_connexion.request.data}. JSON is required."
    )
