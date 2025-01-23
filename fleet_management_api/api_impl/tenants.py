import json

import jwt
from connexion.lifecycle import ConnexionRequest  # type: ignore
from connexion.exceptions import Unauthorized
from fleet_management_api.api_impl.load_request import Request as _Request
from fleet_management_api.api_impl.auth_controller import get_public_key


class NoAccessibleTenants(Exception):
    pass


class NoHeaderWithJWTToken(Exception):
    pass


class MissingRSAKey(Exception):
    pass


_ALGORITHM = "RS256"


class AccessibleTenants:
    """
    Each instance of the class is initialized with tenant name read from JWT token
    in the Authorization header of the request, given the key for decoding the token.

    If the request contains tenant cookie, the tenant name is checked against the tenants
    listed in the JWT token contained in the request.headers["Authorization"].
    If the header is missing, an exception is raised.

    If the tenant cookie is not specified, the tenant name will be an empty string.
    """

    def __init__(self, request: _Request, key: str = "", audience: str = "account") -> None:
        if not key.strip():
            key = get_public_key()
        self._current, self._all_accessible = _check_and_read(request, key, audience)

    @property
    def current(self) -> str:
        """Return the current tenant."""
        return self._current

    @property
    def all(self) -> list[str]:
        """Return all accessible tenants."""
        return self._all_accessible

    @property
    def unrestricted(self) -> bool:
        """Return True if all tenants existing in the database (regardless of permissions) can be accessed for reading."""
        return self._current == "" and not bool(self._all_accessible)


def _check_and_read(request: ConnexionRequest, key: str, audience: str) -> tuple[str, list[str]]:
    tenant = _tenant_from_cookie(request)
    if "api_key" in request.query:
        return tenant, []
    else:
        # api key is not provided - read tenants from JWT
        tenants = _accessible_tenants_from_jwt(request, key, audience)
        if tenant and tenant not in tenants:
            raise NoAccessibleTenants(
                f"Tenant '{tenant}' set in a cookie is not among accessible tenants ({tenants})."
            )
        return tenant, tenants


def _tenant_from_cookie(request: ConnexionRequest) -> str:
    if hasattr(request, "cookies") and "tenant" in request.cookies:
        return str(request.cookies.get("tenant", "")).strip()
    return ""


def _accessible_tenants_from_jwt(request: ConnexionRequest, key: str, audience: str) -> list[str]:
    # api key is not provided - read tenants from JWT
    if "Authorization" not in request.headers:
        raise NoHeaderWithJWTToken
    bearer = str(request.headers["Authorization"]).split(" ")[-1]
    if not bearer.strip():
        raise Unauthorized("No valid JWT token or API key provided.")
    if not key.strip():
        raise MissingRSAKey("RSA public key is not set.")
    decoded_key = jwt.decode(bearer, key, [_ALGORITHM], audience=audience)
    payload = dict(json.loads(decoded_key["Payload"]))
    group: list[str] = payload.get("group", [])
    tenants = [item.split("/")[-1] for item in group if item.startswith("/customers/")]
    tenants = [tenant for tenant in tenants if tenant]
    if not tenants:
        raise NoAccessibleTenants("No item group in token. Token does not contain tenants.")
    return tenants
