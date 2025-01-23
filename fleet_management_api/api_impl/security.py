from typing import Optional
import json
import urllib.parse as _url
import re

from connexion.lifecycle import ConnexionRequest  # type: ignore
from connexion.exceptions import Unauthorized
import jwt
from keycloak import KeycloakOpenID  # type: ignore
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from fleet_management_api.api_impl.load_request import Request as _Request


class TenantNotAccessible(Exception):
    pass


class NoHeaderWithJWTToken(Exception):
    pass


class MissingRSAKey(Exception):
    pass


_public_key: str = ""
_client_id: str = ""


def get_public_key() -> str:
    global _public_key
    return _public_key


def get_client_id() -> str:
    global _client_id
    return _client_id


def set_auth_params(public_key: str, client_id: str) -> None:
    global _public_key
    _public_key = "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"
    global _client_id
    _client_id = client_id


def clear_auth_params() -> None:
    global _public_key
    _public_key = ""
    global _client_id
    _client_id = ""


_testing_public_key: str = ""
_testing_private_key: str = ""


def get_test_public_key(strip: bool = False) -> str:
    if strip:
        return _strip_footer_and_header(_testing_public_key)
    return _testing_public_key


def get_test_private_key(strip: bool = False) -> str:
    if strip:
        return _strip_footer_and_header(_testing_private_key)
    return _testing_private_key


def clear_test_keys() -> None:
    global _testing_public_key, _testing_private_key
    _testing_public_key = ""
    _testing_private_key = ""


def generate_test_keys() -> None:
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


class AccessibleTenants:
    """
    Each instance of the class is initialized with tenant name read from JWT token
    in the Authorization header of the request, given the key for decoding the token.

    If the request contains tenant cookie, the tenant name is checked against the tenants
    listed in the JWT token contained in the request.headers["Authorization"].
    If the header is missing, an exception is raised.

    If the tenant cookie is not specified, the tenant name will be an empty string.
    """

    algorithm = "RS256"

    def __init__(self, request: _Request, key: str = "", audience: str = "account") -> None:
        if not key.strip():
            key = get_public_key()
        self._current, self._all_accessible = self._check_and_read(request, key, audience)

    @property
    def current(self) -> str:
        return self._current

    @property
    def all_accessible(self) -> list[str]:
        return self._all_accessible

    @property
    def unrestricted(self) -> bool:
        return self._current == "" and not bool(self._all_accessible)

    @staticmethod
    def _check_and_read(
        request: ConnexionRequest, key: str, audience: str
    ) -> tuple[str, list[str]]:
        if not hasattr(request, "cookies") or "tenant" not in request.cookies:
            tenant = ""
        else:
            tenant = str(request.cookies.get("tenant", "")).strip()

        if "api_key" in request.query:
            return tenant, []
        else:
            # api key is not provided - read tenants from JWT
            if "Authorization" not in request.headers:
                raise NoHeaderWithJWTToken
            bearer = str(request.headers["Authorization"]).split(" ")[-1]
            if not bearer.strip():
                raise Unauthorized("No valid JWT token or API key provided.")
            if not key.strip():
                raise MissingRSAKey("RSA public key is not set.")
            decoded_str = jwt.decode(
                bearer, key, audience=audience, algorithms=[AccessibleTenants.algorithm]
            )["Payload"]
            payload = json.loads(decoded_str)

            if "group" not in payload:
                raise TenantNotAccessible("No item group in token. Token does not contain tenants.")
            group: list[str] = payload["group"]
            tenants = [item.split("/")[-1] for item in group if item.startswith("/customers/")]
            if not tenants:
                raise TenantNotAccessible("No item group in token. Token does not contain tenants.")
            if tenant != "" and tenant not in tenants:
                raise TenantNotAccessible(
                    f"Tenant {tenant} sent in a cookie is not among accessible tenants sent in JWT token ({tenants})."
                )
            return tenant, tenants


class SecurityObj:
    def set_config(
        self,
        keycloak_url: str,
        client_id: str,
        secret_key: str,
        scope: str,
        realm: str,
        base_uri: str,
    ) -> None:
        """Set configuration for keycloak authentication and initialize KeycloakOpenID."""
        self._keycloak_url = keycloak_url
        self._scope = scope
        self._realm_name = realm
        self._callback = appended_uri(base_uri, "token_get")
        self._state = "state"

        self._oid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm,
            client_secret_key=secret_key,
        )

    def get_authentication_url(self) -> str:
        """Get keycloak url used for authentication."""
        auth_url = self._oid.auth_url(
            redirect_uri=self._callback, state=self._state, scope=self._scope
        )
        return auth_url

    def token_get(
        self,
        state: Optional[str],
        session_state: Optional[str],
        iss: Optional[str],
        code: Optional[str],
    ) -> dict:
        """Get token from keycloak using a code returned by keycloak."""
        if state != self._state:
            raise Exception("Invalid state")

        if _url.urlparse(iss).geturl() != appended_uri(
            self._keycloak_url, "realms", self._realm_name
        ):
            raise Exception("Invalid issuer")

        token = self._oid.token(
            grant_type="authorization_code", code=code, redirect_uri=self._callback
        )
        return token

    def token_refresh(self, refresh_token: str) -> dict:
        """Get a new token from keycloak using the refresh token."""
        token = self._oid.refresh_token(refresh_token=refresh_token)
        return token


def appended_uri(uri: str, *appended: str) -> str:
    """Join URI parts.

    This function return valid URI composed of multiple parts.
    """
    if uri.endswith("//"):
        raise ValueError("Invalid URI: " + uri)
    for part in appended:
        uri = _url.urljoin(base=uri + "/", url=part.strip("/"))
    return uri
