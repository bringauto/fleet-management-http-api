import secrets as _secrets
import string as _string
from typing import Optional
import logging

from sqlalchemy import Engine as _Engine

from fleet_management_api.database.db_models import ApiKeyDB as _ApiKeyDB
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.timestamp import timestamp_ms as _timestamp_ms
import fleet_management_api.database.connection as _connection
from fleet_management_api.logs import LOGGER_NAME as _LOGGER_NAME


logger = logging.getLogger(_LOGGER_NAME)


_KEY_LENGTH = 30


def create_key(key_name: str, connection_source: _Engine) -> tuple[int, str]:
    """Create a new API key with name 'key_name'.

    The key name must not be already used.
    """
    key = _generate_key()
    now = _timestamp_ms()
    already_existing_keys = _db_access.get(
        _db_access.NO_TENANTS,
        _ApiKeyDB,
        criteria={"name": lambda x: x == key_name},
        connection_source=connection_source,
    )
    if len(already_existing_keys) > 0:
        return 400, _key_already_exists_msg(key_name)
    else:
        response = _db_access.add_without_tenant(
            _ApiKeyDB(key=key, name=key_name, creation_timestamp=now),
            connection_source=connection_source,
        )
        if response.status_code == 400:
            return 400, str(response.body)
        else:
            return 200, _key_added_msg(key_name, key)


def verify_key_and_return_key_info(
    api_key: str, connection_source: Optional[_Engine] = None
) -> tuple[int, str | _ApiKeyDB]:
    """Verify that the API key is valid and return the key info (timestamp of when the key was created and the key name)."""

    if connection_source is None:
        connection_source = _connection.current_connection_source()
    try:
        _key_db_models = _db_access.get(
            _db_access.NO_TENANTS,
            _ApiKeyDB,
            criteria={"key": lambda x: x == api_key},
            connection_source=connection_source,
        )
    except Exception as e:
        logger.error(f"Error while verifying key: {e}")
        return 500, "Internal server error."
    if len(_key_db_models) == 0:
        return 401, "Invalid API key used."
    else:
        return 200, _key_db_models[0]


def _generate_key() -> str:  # pragma: no cover
    return "".join(_secrets.choice(_string.ascii_letters) for _ in range(_KEY_LENGTH))


def _key_added_msg(name: str, key: str) -> str:
    return f"Admin '{name}' added with key:\n\n{key}\n\n"


def _key_already_exists_msg(name: str) -> str:
    return f"Admin with name '{name}' already exists."
