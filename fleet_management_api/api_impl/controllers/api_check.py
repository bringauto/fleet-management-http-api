from connexion.lifecycle import ConnexionResponse as _Response  # type: ignore

import fleet_management_api.database.connection as _connection


def check_api_is_alive() -> _Response:
    try:
        if not _connection.is_connected_to_database():
            return _Response(
                status_code=503, content_type="text/plain", body="Server database is not available."
            )
    except RuntimeError as e:
        return _Response(
            status_code=503,
            content_type="text/plain",
            body=f"Server database is not available. {e}",
        )
    except Exception as e:
        return _Response(status_code=500, content_type="text/plain", body=e)

    return _Response(status_code=200, content_type="text/plain", body="API is alive")
