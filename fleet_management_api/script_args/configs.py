from __future__ import annotations
from typing import Dict, Optional
import os

import pydantic


class APIConfig(pydantic.BaseModel):
    http_server: HTTPServer
    database: Database
    security: Security
    api: API


class HTTPServer(pydantic.BaseModel):
    base_uri: pydantic.AnyUrl


class Database(pydantic.BaseModel):
    connection: Connection
    maximum_number_of_table_rows: Dict[str, int]

    class Connection(pydantic.BaseModel):
        username: str
        password: str
        location: str = pydantic.Field(min_length=1)
        port: int
        database_name: str

    @pydantic.validator("maximum_number_of_table_rows")
    @classmethod
    def maximum_row_number_at_least_one(cls, val_dict: Dict[str, int]) -> Dict[str, int]:
        for key, value in val_dict.items():
            if value < 1:
                raise ValueError(f"The maximum number of rows in a table '{key}' must be at least one.")
        return val_dict


class Security(pydantic.BaseModel):
    keycloak_url: pydantic.AnyUrl
    client_id: str
    client_secret_key: str
    scope: str
    realm: str
    keycloak_public_key_file: str
    callback: pydantic.AnyUrl = pydantic.Field(Optional)

    @pydantic.validator("keycloak_public_key_file")
    @classmethod
    def keycloak_public_key_file_is_valid_or_empty(cls, file_path: str) -> str:
        if file_path == "":
            return file_path
        if not os.path.isfile(file_path):
            raise ValueError(f"The keycloak public key file '{file_path}' does not exist.")
        return file_path


class API(pydantic.BaseModel):
    request_for_data: Requests

    class Requests(pydantic.BaseModel):
        timeout_in_seconds: pydantic.NonNegativeInt