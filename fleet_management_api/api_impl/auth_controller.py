from typing import Optional
import re

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from fleet_management_api.api_impl.security import SecurityObj
from flask import redirect
from fleet_management_api.api_impl.api_logging import log_info, log_error, log_debug
from fleet_management_api.api_impl.api_responses import Response as _Response, error as _error


_public_key: str = ""
_client_id: str = ""
_testing_public_key: str = ""
_testing_private_key: str = ""
_security = SecurityObj()


def init_security(
    keycloak_url: str,
    client_id: str,
    secret_key: str,
    scope: str,
    realm: str,
    callback: str,
) -> None:
    _security.set_config(keycloak_url, client_id, secret_key, scope, realm, callback)


def login() -> _Response:
    """login

    Redirect to keycloak login page. # noqa: E501

    :rtype: Response | Dict
    """
    try:
        return redirect(_security.get_authentication_url())
    except Exception as e:
        msg = "Problem reaching oAuth service."
        log_debug(str(e))
        log_error(msg)
        return _error(500, msg, "oAuth service error")


def token_get(
    state: Optional[str] = None,
    session_state: Optional[str] = None,
    iss: Optional[str] = None,
    code: Optional[str] = None,
) -> _Response:
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
    except Exception as e:
        msg = f"Problem getting token from oAuth service. Error: {e}"
        log_error(msg)
        return _error(500, msg, "oAuth service error")
    log_info("Jwt token generated.")
    return _Response(body=token, status_code=200)


def token_refresh(refresh_token: str) -> _Response:
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
        return _error(500, msg, "oAuth service error")
    log_info("Jwt token refreshed.")
    return _Response(body=token, status_code=200)


def get_public_key() -> str:
    """Return the public key for authorization."""
    global _public_key
    return _public_key


def get_client_id() -> str:
    """Return the client ID for authorization."""
    global _client_id
    return _client_id


def set_auth_params(public_key: str, client_id: str) -> None:
    """Set the public key and client ID for authorization."""
    global _public_key
    _public_key = "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"
    global _client_id
    _client_id = client_id


def clear_auth_params() -> None:
    """Clear the public key and client ID. If the parameters are not set, this function does nothing."""
    global _public_key
    _public_key = ""
    global _client_id
    _client_id = ""


def get_test_public_key(strip: bool = False) -> str:
    """Return the testing public key. If strip is True, the key is returned without header and footer."""
    if strip:
        return _strip_footer_and_header(_testing_public_key)
    return _testing_public_key


def get_test_private_key(strip: bool = False) -> str:
    """Return the testing private key. If strip is True, the key is returned without header and footer."""
    if strip:
        return _strip_footer_and_header(_testing_private_key)
    return _testing_private_key


def clear_test_keys() -> None:
    """Clear the testing pair of RSA keys. If the keys are not set, this function does nothing."""
    global _testing_public_key, _testing_private_key
    _testing_public_key = ""
    _testing_private_key = ""


def generate_test_keys() -> None:
    """Generate a pair of RSA keys for testing purposes.

    This does not affect the existing security object or authorization parameters.
    """
    # Generate a private key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # Serialize the private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    # Generate the corresponding public key
    public_key = private_key.public_key()
    # Serialize the public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    global _testing_public_key, _testing_private_key
    _testing_public_key = public_pem.decode()
    _testing_private_key = private_pem.decode()


def _strip_footer_and_header(key: str) -> str:
    stripped_key = re.sub(r"-----.+-----\n?", "", key)
    stripped_key = re.sub(r"\n?-----.+-----", "", stripped_key)
    # Remove any remaining newlines
    stripped_key = stripped_key.replace("\n", "")
    return stripped_key
