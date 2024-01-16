import sys
sys.path.append('./server')
from typing import Tuple, List, Dict, Optional, Any

import connexion
import logging

from fleet_management_api.models import Car
from fleet_management_api.impl.security import SecurityObj
from flask import redirect, Response


_cars: List[Car] = []


_security = SecurityObj()
def init_security(keycloak_url: str, client_id: str, secret_key: str, scope: str, realm: str, callback: str) -> None:
    _security.set_config(keycloak_url, client_id, secret_key, scope, realm, callback)


def login() -> Response:
#     device: Optional[str] = None
# ) -> Response|Tuple[Dict|str, int]:
    """login

    Redirect to keycloak login page. If empty device is specified, get authentication url and device code. Try authenticate if device code is provided. # noqa: E501

    :rtype: Response | Dict
    """
    # if device == "":
    #     try:
    #         auth_json = _security.device_get_authentication()
    #     except:
    #         msg = "Problem reaching oAuth service."
    #         return _log_and_respond(msg, 500, msg)
    #     return _log_and_respond(auth_json, 200, "Device authentication initialized.")
    # elif device != None:
    #     try:
    #         token = _security.device_token_get(device)
    #         return _log_and_respond(token, 200, "Device authenticated, jwt token generated.")
    #     except:
    #         msg = "Invalid device code or device still authenticating."
    #         return _log_and_respond(msg, 400, msg)
    try:
        return redirect(_security.get_authentication_url())
    except:
            msg = "Problem reaching oAuth service."
            return _log_and_respond(msg, 500, msg)


def token_get(
    state: Optional[str] = None,
    session_state: Optional[str] = None,
    iss: Optional[str] = None,
    code: Optional[str] = None
) -> Tuple[Dict, int]:
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
        return _log_and_respond(msg, 500, msg)
    return _log_and_respond(token, 200, "Jwt token generated.")


def token_refresh(
    refresh_token: str
) -> Tuple[Dict, int]:
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
        return _log_and_respond(msg, 500, msg)
    return _log_and_respond(token, 200, "Jwt token refreshed.")


def create_car(car: Dict) -> Tuple[str, int]:  # noqa: E501
    """Create a new car

     # noqa: E501

    :param car: New car json
    :type car: dict | bytes

    :rtype: Union[Car, Tuple[Car, int], Tuple[Car, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
        _create_car(car)
        return 'Car was succesfully created.'
    return


def get_cars() -> Tuple[List[Car], int]:  # noqa: E501
    """Finds all cars

     # noqa: E501

    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return _cars, 200


def _create_car(car: Car) -> None:
    _cars.append(car)


def _log_and_respond(body: Any, code: int, log_msg: str = "") -> Tuple[Any, int]:
    if log_msg.strip() != "":
        logger = logging.getLogger('werkzeug')
        logger.info(log_msg)
    return body, code  # type: ignore