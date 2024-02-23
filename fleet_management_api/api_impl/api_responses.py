from connexion.lifecycle import ConnexionResponse as Response  # type: ignore


def json_response(code: int, body: object) -> Response:
    return Response(body=body, status_code=code, content_type="application/json")


def text_response(code: int, msg: str) -> Response:
    return Response(body=msg, status_code=code, content_type="text/plain")
