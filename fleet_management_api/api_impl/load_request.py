from __future__ import annotations
import dataclasses
from typing import Any
import abc

import connexion  # type: ignore
from flask.wrappers import Request as _Request

from fleet_management_api.api_impl.constants import (
    AUTHORIZATION_HEADER_NAME as _AUTHORIZATION_HEADER_NAME,
    AUTHORIZATION_ENVIRONMENT_NAME as _AUTHORIZATION_ENVIRONMENT_NAME,
)


@dataclasses.dataclass
class LoadedRequest(abc.ABC):
    """A superclass for requests loaded from the Connexion framework."""

    data: Any
    headers: dict[str, Any]
    cookies: dict[str, Any] = dataclasses.field(default_factory=dict)
    query: dict[str, Any] = dataclasses.field(default_factory=dict)
    url: str = ""
    method: str = ""

    @classmethod
    def load(cls) -> LoadedRequest | None:
        request = connexion.request
        if not cls.is_valid(request):
            return None
        try:
            headers = {
                _AUTHORIZATION_HEADER_NAME: request.headers.environ.get(
                    _AUTHORIZATION_ENVIRONMENT_NAME, ""
                )
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


class _LoadedRequestJSON(LoadedRequest):
    """A request loaded from the connexion request object, while expecting a JSON data. The loaded request is valid only if the
    connexion request contained a valid JSON data."""

    @classmethod
    def get_data(cls, request: _Request) -> Any:
        try:
            return request.get_json()
        except RuntimeError:
            return None

    @classmethod
    def is_valid(cls, request: _Request) -> bool:
        return request.is_json


@dataclasses.dataclass
class _LoadedRequestEmpty(LoadedRequest):
    """A request loaded from the connexion request object, while expecting no data. The loaded request is always valid."""

    data: Any = dataclasses.field(default_factory=list)
    headers: dict[str, Any] = dataclasses.field(default_factory=dict)
    cookies: dict[str, Any] = dataclasses.field(default_factory=dict)
    query: dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def get_data(cls, *args, **kwargs) -> Any:
        return []

    @classmethod
    def is_valid(cls, *args, **kwargs) -> bool:
        return True


def load_request(require_data: bool = False) -> LoadedRequest | None:
    """Load the request from the connexion request object.

    If the data is required, the request is loaded only if the request contains valid JSON data, otherwise None is returned.
    """
    return _LoadedRequestJSON.load() if require_data else _LoadedRequestEmpty.load()
