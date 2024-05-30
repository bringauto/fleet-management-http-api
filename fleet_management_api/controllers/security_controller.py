import jwt

import fleet_management_api.api_impl as _api
from fleet_management_api.api_impl.api_keys import verify_key_and_return_key_info as _verify_key_and_return_key_info


_public_key: str
_client_id: str
def set_auth_params(public_key: str, client_id: str) -> None:
    global _public_key
    _public_key = public_key
    global _client_id
    _client_id = client_id


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
    try:
        decoded_token = jwt.decode(token, _public_key, algorithms=['RS256'], audience='account')
    except:
        return None

    for origin in decoded_token["allowed-origins"]:
        if origin == _client_id:
            return {'scopes': {}, 'uid': ''}

    return None # type: ignore


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
    #return set(required_scopes).issubset(set(token_scopes))
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

    code, info = _verify_key_and_return_key_info(api_key)
    if code==200:
        return {'name': info.name} # type: ignore
    else:
        return None