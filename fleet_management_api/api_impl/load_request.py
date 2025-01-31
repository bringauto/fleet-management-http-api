from __future__ import annotations
import dataclasses
from typing import Any
import abc

import connexion  # type: ignore
from flask.wrappers import Request as _Request


@dataclasses.dataclass
class Request(abc.ABC):
    data: Any
    headers: dict[str, Any]
    cookies: dict[str, Any] = dataclasses.field(default_factory=dict)
    query: dict[str, Any] = dataclasses.field(default_factory=dict)
    url: str = ""
    method: str = ""

    @classmethod
    def load(cls, current_tenant: str = "") -> Request | None:

        request = connexion.request
        if not cls.ok(request):
            return None
        try:
            authorization = request.headers.environ.get("HTTP_AUTHORIZATION", "")
            headers = {"Authorization": authorization}
        except RuntimeError:
            headers = {"Authorization": ""}

        cookies = dict(request.cookies.copy())
        if current_tenant:
            cookies["tenant"] = current_tenant
        return cls(
            data=cls.get_data(request),
            headers=headers,
            cookies=cookies,
            query=request.args,
            url=request.url,
            method=request.method,
        )

    @property
    def api_key(self) -> str:
        return self.query.get("api_key", "")

    @classmethod
    @abc.abstractmethod
    def get_data(cls, request: _Request) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def ok(cls, request: _Request) -> bool:
        pass


class RequestJSON(Request):

    @classmethod
    def get_data(cls, request: _Request) -> Any:
        try:
            return request.get_json()
        except RuntimeError:
            return None

    @classmethod
    def ok(cls, request: _Request) -> bool:
        return request.is_json


class RequestNoData(Request):

    @classmethod
    def get_data(cls, request: _Request) -> Any:
        return None

    @classmethod
    def ok(cls, request: _Request) -> bool:
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
    def ok(cls, *args, **kwargs) -> bool:
        return True
