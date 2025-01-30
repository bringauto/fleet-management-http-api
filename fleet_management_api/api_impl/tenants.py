import json

import jwt
from connexion.lifecycle import ConnexionRequest  # type: ignore
from connexion.exceptions import Unauthorized
from fleet_management_api.api_impl.load_request import Request as _Request
from fleet_management_api.api_impl.auth_controller import get_public_key


class UsingEmptyTenant(Exception):
    """Raise when trying use an empty tenant."""

    pass


class NoAccessibleTenants(Exception):
    """Raise when no accessible tenants are found in a JWT token."""

    pass


class NoHeaderWithJWTToken(Exception):
    """Raise when no header with a JWT token is found in a request."""

    pass


class MissingRSAKey(Exception):
    """Raise when a RSA key (either public or private) is not set."""

    pass


_ALGORITHM = "RS256"


class AccessibleTenants:
    """
    This class extracts from a request the following information:
    - the name of the current tenant, that is used for reading and writing data to the database.
    - the list of all tenants that can be accessed for reading data from the database.

    Optional arguments include:
    - `key` - a public key used for decoding a JWT token. If left empty, the public key is read using
    the `get_public_key` function from the `auth_controller` module.
    - `audience` - the audience of the JWT token.

    Both current tenant and accessible tenants are extracted based on the authorization method used.
    If an API key is provided, all accessible tenants are set to empty list, meaning there is NO restriction
    on reading data from the database.

    If API key is not provided and request contains a JWT token, the accessible tenants are extracted from the token.
    If the token does not contain any tenants or the token is not provided, an exception is raised.

    The current tenant is read from a cookie. If the tenant is not set in a cookie, the current tenant is set to empty string.
    If the list of accessible tenants is not empty and the current tenant is set, the current tenant must be among accessible tenants,
    otherwise an exception is raised.

    If the current tenant is empty, all data owned by all accessible tenants can be read from the database,
    but no data can be written to the database.

    If the current tenant is not empty, only data owned by the current tenant can be read and written to the database.
    """

    def __init__(
        self, request: _Request, key: str = "", audience: str = "account", current_tenant: str = ""
    ) -> None:
        if not key.strip():
            key = get_public_key()
        if current_tenant:
            request.cookies["tenant"] = current_tenant
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


class _EmptyTenant(AccessibleTenants):
    """This class is used when tenant is intentionally not set."""

    def __init__(self, *args, **kwargs):
        """The empty tenant object does not have any accessible tenants or a current tenant."""
        pass

    @property
    def current(self) -> str:
        raise UsingEmptyTenant("Empty tenant object does not have a current tenant.")

    @property
    def all(self) -> list[str]:
        raise UsingEmptyTenant("Empty tenant object does not have any accessible tenants.")


NO_TENANTS = _EmptyTenant()


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
    """Return the tenant name from a cookie. If the cookie is not set, return an empty string."""
    if hasattr(request, "cookies") and "tenant" in request.cookies:
        return str(request.cookies.get("tenant", "")).strip()
    return ""


def _accessible_tenants_from_jwt(request: ConnexionRequest, key: str, audience: str) -> list[str]:
    """Return the list of accessible tenants extracted from a JWT token.

    If the token is missing or does not contain any tenants, raise an exception.
    """
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
