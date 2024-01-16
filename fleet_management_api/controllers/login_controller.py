import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api import util


def login():  # noqa: E501
    """login

    Login using keycloak. # noqa: E501


    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def token_get(state=None, session_state=None, iss=None, code=None):  # noqa: E501
    """token_get

    Callback endpoint for keycloak to receive jwt token. # noqa: E501

    :param state: State returned by keycloak authentication.
    :type state: str
    :param session_state: Session state returned by keycloak authentication.
    :type session_state: str
    :param iss: Code issuer returned by keycloak authentication.
    :type iss: str
    :param code: Code used for jwt token generation returned by keycloak authentication.
    :type code: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def token_refresh(refresh_token):  # noqa: E501
    """token_refresh

    Endpoint to receive jwt token from refresh token. # noqa: E501

    :param refresh_token: Refresh token used for jwt token generation.
    :type refresh_token: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'
