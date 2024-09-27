import fleet_management_api.database.connection as _connection
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    text_response as _text_response,
    error as _error,
)


def check_api_is_alive() -> _Response:
    try:
        if not _connection.is_connected_to_database():
            return _error(
                code=503,
                msg="Server database is not available.",
                title="Database connection error",
            )
        else:
            return _text_response("API is alive.")
    except RuntimeError as e:
        return _error(
            503,
            f"Server database is not available. {e}",
            title="Database connection error",
        )
    except Exception as e:
        return _error(
            500,
            f"Server database is not available. {e}",
            title="Database connection error",
        )
