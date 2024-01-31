import sys
sys.path.append('./server')
from typing import Optional

from connexion.lifecycle import ConnexionResponse # type: ignore

from fleet_management_api.api_impl.security import SecurityObj
from flask import redirect
from fleet_management_api.api_impl.api_logging import log_info, log_error


_security = SecurityObj()
def init_security(keycloak_url: str, client_id: str, secret_key: str, scope: str, realm: str, callback: str) -> None:
    _security.set_config(keycloak_url, client_id, secret_key, scope, realm, callback)


def login() -> ConnexionResponse:
    """login

    Redirect to keycloak login page. # noqa: E501

    :rtype: Response | Dict
    """
    try:
        return redirect(_security.get_authentication_url())
    except:
        msg = "Problem reaching oAuth service."
        log_error(msg)
        return ConnexionResponse(body=msg, status_code=500)



def token_get(
    state: Optional[str] = None,
    session_state: Optional[str] = None,
    iss: Optional[str] = None,
    code: Optional[str] = None
) -> ConnexionResponse:
    """token_get

    Get token. Should only be used by keycloak. # noqa: E501

    :param state: State
    :type state: str
    :param session_state: Session state
    :type session_state: str
    :param iss: Code issuer
    :type iss: str
    :param code: Code used to get jwt token
    :type code: str

    :rtype: Dict
    """
    try:
        token = _security.token_get(state, session_state, iss, code)
    except:
        msg = "Problem getting token from oAuth service."
        log_error(msg)
        return ConnexionResponse(body=msg, status_code=500)
    log_info("Jwt token generated.")
    return ConnexionResponse(body=token, status_code=200)


def token_refresh(
    refresh_token: str
) -> ConnexionResponse:
    """token_refresh

    Generate a new token using the refresh token. # noqa: E501

    :param refresh_token: Refresh token
    :type refresh_token: str

    :rtype: Dict
    """
    try:
        token = _security.token_refresh(refresh_token)
    except:
        msg = "Problem getting token from oAuth service."
        log_error(msg)
        return ConnexionResponse(body=msg, status_code=500)
    log_info("Jwt token refreshed.")
    return ConnexionResponse(body=token, status_code=200)
