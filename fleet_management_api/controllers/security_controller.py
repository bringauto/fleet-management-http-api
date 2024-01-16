from typing import List
import jwt


_public_key: str
def set_public_key(public_key: str) -> None:
    global _public_key
    _public_key = public_key


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
    
    #TODO temporary until keycloak configuration is decided
    #roles = decoded_token["realm_access"]["roles"]
    
    #for role in roles:
    #    if role == "test_role":
    #        return {'scopes': {}, 'uid': ''}
    
    return {'scopes': {}, 'uid': ''}
    #return None # type: ignore


def validate_scope_oAuth2AuthCode(required_scopes, token_scopes):
    """
    Validate required scopes are included in token scope

    :param required_scopes Required scope to access called API
    :type required_scopes: List[str]
    :param token_scopes Scope present in token
    :type token_scopes: List[str]
    :return: True if access to called API is allowed
    :rtype: bool
    """
    # looks for scopes returned by the function above
    #return set(required_scopes).issubset(set(token_scopes))
    return True

