from __future__ import annotations
import dataclasses

import jwt
from connexion.exceptions import Unauthorized  # type: ignore

from fleet_management_api.api_impl.load_request import LoadedRequest as _Request
from fleet_management_api.api_impl.auth_controller import get_public_key
from fleet_management_api.api_impl.constants import (
    AUTHORIZATION_HEADER_NAME as _AUTHORIZATION_HEADER_NAME,
)


_ALGORITHM = "RS256"


TenantName = str


class UsingEmptyTenant(Exception):
    """Raise when trying use an empty tenant."""

    pass


class TenantNotAccessible(Exception):
    """Raise when the tenant is not accessible."""

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


class AccessibleTenants:
    """
    This class extracts from a request the following information:
    - the name of the current tenant, that is used for reading and writing data to the database.
    - the list of all tenants that can be accessed for reading data from the database.
    """

    def __init__(
        self,
        request: _Request,
        key: str = "",
        audience: str = "account",
        ignore_cookie: bool = False,
    ) -> None:
        """
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
        if "api_key" not in request.query and not key.strip():
            key = get_public_key()
        self._current, self._all_accessible = _extract_current_and_accessible_tenants_from_request(
            request,
            key,
            audience,
            ignore_cookie=ignore_cookie,
        )

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

    @staticmethod
    def from_dict(data: dict) -> AccessibleTenantsFromDict:
        """Return an object created from a dictionary."""
        return AccessibleTenantsFromDict(data)

    def is_accessible(self, tenant_name: str) -> bool:
        """Return True if the tenant is accessible."""
        return (tenant_name in self._all_accessible) or not bool(self._all_accessible)

    def copy(self) -> AccessibleTenants:
        """Return a copy of the current object."""
        return AccessibleTenants.from_dict({"current": self._current, "all": self._all_accessible})


class AccessibleTenantsFromDict(AccessibleTenants):

    def __init__(self, data: dict) -> None:
        self._current = data.get("current", "")
        self._all_accessible = data.get("all", [])


class _EmptyTenant(AccessibleTenants):
    """This class is used when tenant is intentionally not set."""

    def __init__(self, *args, **kwargs):
        """The empty tenant object does not have any accessible tenants or a current tenant."""
        self._current = ""
        self._all_accessible = []

    @property
    def current(self) -> str:
        raise UsingEmptyTenant("Empty tenant object does not have a current tenant.")

    @property
    def all(self) -> list[str]:
        raise UsingEmptyTenant("Empty tenant object does not have any accessible tenants.")


NO_TENANTS = _EmptyTenant()


@dataclasses.dataclass(frozen=True)
class LoadedAccessibleTenants:
    msg: str
    status_code: int = 200
    tenants: AccessibleTenants = NO_TENANTS


def get_accessible_tenants(
    request: _Request,
    key: str = "",
    audience: str = "account",
    ignore_cookie: bool = False,
) -> LoadedAccessibleTenants:
    try:
        tenants = AccessibleTenants(request, key, audience, ignore_cookie)
        return LoadedAccessibleTenants(
            msg="Accessible tenants extracted successfully.",
            status_code=200,
            tenants=tenants,
        )
    except NoAccessibleTenants as e:
        # If the JWT token does not contain any tenants, return an empty tenant object
        return LoadedAccessibleTenants(
            msg=f"JWT token does not contain any accessible tenants. Error: {str(e)}",
            status_code=401,
            tenants=NO_TENANTS,
        )
    except Exception as e:
        return LoadedAccessibleTenants(
            msg=f"Failed to extract accessible tenants: {str(e)}",
            status_code=500,
            tenants=NO_TENANTS,
        )


def _extract_current_and_accessible_tenants_from_request(
    request: _Request, key: str, audience: str, ignore_cookie: bool = False
) -> tuple[str, list[str]]:

    if ignore_cookie:
        current_tenant = ""
    else:
        current_tenant = _get_current_tenant(request)
    if "api_key" in request.query:
        accessible_tenants = []
    else:
        # api key is not provided - read tenants from JWT
        tenants = _get_accessible_tenants_from_auth_headers(request, key, audience)
        _check_current_tenant_is_accessible(current_tenant, tenants)
        accessible_tenants = tenants
    return current_tenant, accessible_tenants


def _check_current_tenant_is_accessible(current: TenantName, accessible: list[TenantName]) -> None:
    if current and current not in accessible:
        raise NoAccessibleTenants(
            f"Current tenant '{current}' set in cookie is not among accessible tenants ({accessible})."
        )


def _get_current_tenant(request: _Request) -> TenantName:
    """Return the tenant name from a cookie. If the cookie is not set, return an empty string."""
    if hasattr(request, "cookies") and "tenant" in request.cookies:
        return str(request.cookies.get("tenant", "")).strip()
    return ""


def _get_accessible_tenants_from_auth_headers(
    request: _Request, key: str, audience: str
) -> list[str]:
    """The accessible tenants extracted from a JWT token.

    If the token is missing or does not contain any tenants, raise an exception.
    """
    # api key is not provided - read tenants from JWT
    if _AUTHORIZATION_HEADER_NAME not in request.headers:
        raise NoHeaderWithJWTToken

    bearer = str(request.headers[_AUTHORIZATION_HEADER_NAME]).split(" ")[-1]
    if not bearer.strip():
        raise Unauthorized("No valid JWT token or API key provided.")
    if not key.strip():
        raise MissingRSAKey("RSA public key is not set.")
    decoded_payload = jwt.decode(bearer, key, [_ALGORITHM], audience=audience)
    if "group" not in decoded_payload:
        raise NoAccessibleTenants("No item 'group' in token. Token does not contain tenants.")
    group: list[str] = decoded_payload.get("group", [])
    tenants = [item.split("/")[-1] for item in group if item.startswith("/customers/")]
    tenants = [tenant for tenant in tenants if tenant]
    if not tenants:
        raise NoAccessibleTenants("No accessible tenants found in the token.")
    return tenants
