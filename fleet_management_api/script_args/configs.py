from __future__ import annotations
from typing import Optional, Any

import pydantic


class APIConfig(pydantic.BaseModel):
    logging: dict[str, Any]
    http_server: HTTPServer
    database: Database
    security: Security
    api: API
    data: Data


class Data(pydantic.BaseModel):
    orders: OrdersSetup

    class OrdersSetup(pydantic.BaseModel):
        max_active_orders: pydantic.PositiveInt
        max_inactive_orders: pydantic.PositiveInt


class HTTPServer(pydantic.BaseModel):
    base_uri: pydantic.AnyUrl


class Database(pydantic.BaseModel):
    connection: Connection
    test: str = pydantic.Field(default="")
    maximum_number_of_table_rows: dict[str, int]

    class Connection(pydantic.BaseModel):
        username: str
        password: str
        location: str = pydantic.Field(min_length=1)
        port: int
        database_name: str

    @pydantic.validator("maximum_number_of_table_rows")
    @classmethod
    def maximum_row_number_at_least_one(cls, val_dict: dict[str, int]) -> dict[str, int]:
        for key, value in val_dict.items():
            if value < 1:
                raise ValueError(
                    f"The maximum number of rows in a table '{key}' must be at least one."
                )
        return val_dict


class Security(pydantic.BaseModel):
    keycloak_url: pydantic.AnyUrl
    client_id: str
    client_secret_key: str
    scope: str
    realm: str
    callback: pydantic.AnyUrl = pydantic.Field(Optional)


class API(pydantic.BaseModel):
    request_for_data: Requests

    class Requests(pydantic.BaseModel):
        timeout_in_seconds: pydantic.NonNegativeInt
