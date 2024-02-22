import fleet_management_api.database.connection as _connection
from fleet_management_api.api_impl import Response as _Response, text_response as _text_response


def check_api_is_alive() -> _Response:
    try:
        if not _connection.is_connected_to_database():
            return _text_response(503, "Server database is not available.")
        else:
            return _text_response(200, "API is alive.")
    except RuntimeError as e:
        return _text_response(503, f"Server database is not available. {e}")
    except Exception as e:
        return _text_response(500, f"Server database is not available. {e}")
