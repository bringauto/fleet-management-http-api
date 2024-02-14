import random as _random
import string as _string
from typing import Tuple, Optional

from sqlalchemy import Engine as _Engine

from fleet_management_api.database.db_models import ApiKeyDBModel as _ApiKeyDBModel
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.timestamp import timestamp_ms as _timestamp_ms
import fleet_management_api.database.connection as _connection


_KEY_LENGTH = 30


def create_key(key_name: str, connection_source: _Engine) -> Tuple[int, str]:
    """Create a new API key with name 'key_name'.

    The key name must not be already used.
    """
    key = _generate_key()
    now = _timestamp_ms()
    already_existing_keys = _db_access.get(
        _ApiKeyDBModel, criteria={"name": lambda x: x == key_name}, conn_source=connection_source
    )
    if len(already_existing_keys) > 0:
        return 400, _key_already_exists_msg(key_name)
    else:
        response = _db_access.add(
            _ApiKeyDBModel(key=key, name=key_name, creation_timestamp=now),
            conn_source=connection_source,
        )
        if response.status_code == 400:
            return 400, str(response.body)
        else:
            return 200, _key_added_msg(key_name, key)


def verify_key_and_return_key_info(
    api_key: str, connection_source: Optional[_Engine] = None
) -> Tuple[int, str | _ApiKeyDBModel]:

    """Verify that the API key is valid and return the key info (timestamp of when the key was created and the key name)."""

    if connection_source is None:
        connection_source = _connection.current_connection_source()

    try:
        _key_db_models = _db_access.get(
            _ApiKeyDBModel, criteria={"key": lambda x: x == api_key}, conn_source=connection_source
        )
        if len(_key_db_models) == 0:
            return 401, f"Invalid API key used."
        else:
            return 200, _key_db_models[0]
    except RuntimeError:
        return 503, "Server database is not available."


def _generate_key() -> str:  # pragma: no cover
    return "".join(_random.choice(_string.ascii_letters) for _ in range(_KEY_LENGTH))


def _key_added_msg(name: str, key: str) -> str:
    return f"Admin '{name}' added with key:\n\n{key}\n\n"


def _key_already_exists_msg(name: str) -> str:
    return f"Admin with name '{name}' already exists."
