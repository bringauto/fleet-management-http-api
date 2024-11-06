from typing import Optional

import urllib.parse as _url

from keycloak import KeycloakOpenID  # type: ignore


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
        auth_url = self._oid.auth_url(redirect_uri=self._callback)
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
