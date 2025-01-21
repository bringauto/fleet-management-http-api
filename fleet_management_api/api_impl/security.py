from typing import Optional
import json
import urllib.parse as _url

from connexion.lifecycle import ConnexionRequest  # type: ignore
from connexion.exceptions import Unauthorized
import jwt
from keycloak import KeycloakOpenID  # type: ignore

from fleet_management_api.api_impl.load_request import Request as _Request


class TenantNotAccessible(Exception):
    pass


class NoHeaderWithJWTToken(Exception):
    pass


_key = ""


def set_key(key: str) -> None:
    global _key
    _key = key


def get_key() -> str:
    return _key


class TenantFromToken:
    """
    Each instance of the class is initialized with tenant name read from JWT token
    in the Authorization header of the request, given the key for decoding the token.

    If the request contains tenant cookie, the tenant name is checked against the tenants
    listed in the JWT token contained in the request.headers["Authorization"].
    If the header is missing, an exception is raised.

    If the tenant cookie is not specified, the tenant name will be an empty string.
    """

    algorithm = "HS256"

    def __init__(self, request: _Request, key: str = "") -> None:
        if not key.strip():
            key = get_key()
        self._tenant_name = self._check_and_read(request, key)

    @property
    def name(self) -> str:
        return self._tenant_name

    @staticmethod
    def _check_and_read(request: ConnexionRequest, key: str) -> str:
        if not hasattr(request, "cookies"):
            return ""
        tenant = request.cookies.get("tenant", None)
        if not tenant:
            return ""
        if "Authorization" not in request.headers:
            raise NoHeaderWithJWTToken
        bearer = str(request.headers["Authorization"]).split(" ")[-1]

        if not bearer.strip():
            if request.query.get("api_key", ""):
                return tenant
            raise Unauthorized("No valid JWT token or API key provided.")

        try:
            decoded_str = jwt.decode(bearer, key, algorithms=[TenantFromToken.algorithm])["Payload"]
        except jwt.exceptions.DecodeError:
            raise TenantNotAccessible("Invalid JWT token.")
        payload = json.loads(decoded_str)
        if "group" not in payload:
            raise TenantNotAccessible("No item group in token. Token does not contain tenants.")
        group: list[str] = payload["group"]
        tenants = [item.split("/")[-1] for item in group if item.startswith("/customers/")]
        if not tenants:
            return tenant
        if tenant not in tenants:
            raise TenantNotAccessible(
                f"Tenant {tenant} sent in a cookie is not among accessible tenants sent in JWT token ({tenants})."
            )
        return tenant


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
