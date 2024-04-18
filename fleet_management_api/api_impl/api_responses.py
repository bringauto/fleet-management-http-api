from typing import Optional

from connexion.lifecycle import ConnexionResponse as Response  # type: ignore
from connexion.problem import problem as _problem  # type: ignore


def json_response(body: object, code: int = 200) -> Response:
    return Response(body=body, status_code=code, content_type="application/json")


def text_response(msg: str, code: int = 200) -> Response:
    return Response(body=msg, status_code=code, content_type="text/plain")


def error(code: int, msg: str, title: str, type: Optional[str] = None) -> Response:
    return _problem(status=code, title=title, detail=msg, type=type)