import random as _random
import string as _string
from typing import Tuple

from fleet_management_api.database.db_models import ApiKeyDBModel as _ApiKeyDBModel
import fleet_management_api.database.db_access as _db_access
from fleet_management_api.database.timestamp import timestamp_ms as _timestamp_ms


def create_key(key_name: str) -> Tuple[int, str]:
    key = _generate_key()
    now = _timestamp_ms()
    already_existing_keys = _db_access.get(_ApiKeyDBModel, criteria={"name": lambda x: x==key_name})
    if len(already_existing_keys) > 0:
        return 400, _key_already_exists_msg(key_name)
    else:
        response = _db_access.add(_ApiKeyDBModel, _ApiKeyDBModel(key=key, name=key_name, creation_timestamp=now))
        if response.status_code == 400:
            return 400, str(response.body)
        else:
            return 200, _key_added_msg(key_name, key)


def verify_key_and_return_key_info(api_key: str) -> Tuple[int, str|_ApiKeyDBModel]:
    _key_db_models = _db_access.get(_ApiKeyDBModel, criteria={"key": lambda x: x==api_key})
    if len(_key_db_models) == 0:
        return 401, f"Invalid API key used."
    else:
        return 200, _key_db_models[0]


def _generate_key() -> str: # pragma: no cover
    return ''.join(_random.choice(_string.ascii_letters) for _ in range(30))


def _key_added_msg(name: str, key: str) -> str:
    return f"Admin '{name}' added with key:\n\n{key}\n\n"


def _key_already_exists_msg(name: str) -> str:
    return f"Admin with name '{name}' already exists."
