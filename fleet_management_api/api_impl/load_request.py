from __future__ import annotations
import dataclasses
from typing import Any
import abc

import connexion  # type: ignore
from flask.wrappers import Request as _Request

from fleet_management_api.api_impl.constants import (
    AUTHORIZATION_HEADER_NAME as _AUTHORIZATION_HEADER_NAME,
)


@dataclasses.dataclass
class Request(abc.ABC):
    data: Any
    headers: dict[str, Any]
    cookies: dict[str, Any] = dataclasses.field(default_factory=dict)
    query: dict[str, Any] = dataclasses.field(default_factory=dict)
    url: str = ""
    method: str = ""

    @classmethod
    def load(cls) -> Request | None:
        request = connexion.request
        if not cls.is_valid(request):
            return None
        try:
            headers = {
                _AUTHORIZATION_HEADER_NAME: request.headers.environ.get("HTTP_AUTHORIZATION", "")
            }
        except RuntimeError:
            headers = {_AUTHORIZATION_HEADER_NAME: ""}

        return cls(
            data=cls.get_data(request),
            headers=headers,
            cookies=dict(request.cookies.copy()),
            query=request.args,
            url=request.url,
            method=request.method,
        )

    @property
    def api_key(self) -> str:
        return self.query.get("api_key", "")

    @classmethod
    @abc.abstractmethod
    def get_data(cls, request: _Request) -> Any:
        pass

    @classmethod
    @abc.abstractmethod
    def is_valid(cls, request: _Request) -> bool:
        pass


class RequestJSON(Request):
    @classmethod
    def get_data(cls, request: _Request) -> Any:
        try:
            return request.get_json()
        except RuntimeError:
            return None

    @classmethod
    def is_valid(cls, request: _Request) -> bool:
        return request.is_json


class RequestNoData(Request):

    @classmethod
    def get_data(cls, request: _Request) -> Any:
        return None

    @classmethod
    def is_valid(cls, request: _Request) -> bool:
        return True


@dataclasses.dataclass
class RequestEmpty(Request):
    data: Any = None
    headers: dict[str, Any] = dataclasses.field(default_factory=dict)
    cookies: dict[str, Any] = dataclasses.field(default_factory=dict)
    query: dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def get_data(cls, *args, **kwargs) -> Any:
        return None

    @classmethod
    def is_valid(cls, *args, **kwargs) -> bool:
        return True
