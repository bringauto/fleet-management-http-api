import jwt
import connexion as _connexion

from fleet_management_api.api_impl.api_keys import (
    verify_key_and_return_key_info as _verify_key_and_return_key_info,
)
from fleet_management_api.api_impl.auth_controller import get_client_id, get_public_key
from fleet_management_api.api_impl.api_logging import log_warning


def info_from_oAuth2AuthCode(token):
    """
    Validate and decode token.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.
    'scope' or 'scopes' will be passed to scope validation function.

    :param token Token provided by Authorization header
    :type token: str
    :return: Decoded token information or None if token is invalid
    :rtype: dict | None
    """

    _raise_for_simultaneous_jwt_and_api_key()
    try:
        decoded_token = jwt.decode(
            token, get_public_key(), algorithms=["RS256"], audience="account"
        )
    except Exception as e:
        log_warning(f"Failed to decode JWT token: {str(e)}")
        return None
    for origin in decoded_token.get("allowed-origins", []):
        if origin == get_client_id():
            return {"scopes": {}, "uid": ""}

    return None  # type: ignore


def validate_scope_oAuth2AuthCode(required_scopes, token_scopes):
    """
    Validate required scopes are included in token scope

    :param required_scopes Required scope to access called API
    :type required_scopes: list[str]
    :param token_scopes Scope present in token
    :type token_scopes: list[str]
    :return: True if access to called API is allowed
    :rtype: bool
    """
    # looks for scopes returned by the function above
    # return set(required_scopes).issubset(set(token_scopes))
    return True


def info_from_APIKeyAuth(api_key, *args) -> None | dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """
    _raise_for_simultaneous_jwt_and_api_key()
    code, info = _verify_key_and_return_key_info(api_key)
    if code == 200:
        return {"name": info.name}  # type: ignore
    else:
        return None


def _raise_for_simultaneous_jwt_and_api_key() -> None:
    request = _connexion.request
    api_key_used = "api_key" in request.query_string.decode()
    jwt_used = "Authorization" in request.headers and request.headers["Authorization"].startswith(
        "Bearer "
    )
    if api_key_used and jwt_used:
        raise _connexion.exceptions.AuthenticationProblem(
            status=401,
            detail="Cannot use both API key and JWT token for authentication.",
            title="Authentication error",
        )
