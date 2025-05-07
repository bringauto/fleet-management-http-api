from fleet_management_api.database import db_models as _db_models, db_access as _db_access
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_error_and_respond as _log_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
    log_invalid_request_body_format as _log_invalid_request_body_format,
)
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    text_response as _text_response,
)
from fleet_management_api.api_impl.load_request import RequestEmpty as _RequestEmpty
from fleet_management_api.api_impl.tenants import (
    AccessibleTenants as _AccessibleTenants,
    get_accessible_tenants as _get_accessible_tenants,
    NO_TENANTS as _NO_TENANTS,
)
from fleet_management_api.api_impl.controller_decorators import (
    controller_with_tenants as _controller_with_tenants,
    ProcessedRequest as _ProcessedRequest,
)


def set_tenant_cookie(tenant_id: int) -> _Response:
    """Set the tenant cookie to the tenant with the given ID.

    If the tenant with the ID does not exist, return a Unauthorized response."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tresponse = _get_accessible_tenants(request, ignore_cookie=True)
    if tresponse.status_code != 200:
        return tresponse
    tenants = tresponse.body
    tenants_in_db = _db_access.get_tenants(tenants)
    assert isinstance(tenant_id, int), "Tenant ID must be an integer"
    for t in tenants_in_db:
        if t.id == tenant_id:
            response = _text_response(
                f"Tenant '{t.name}' does exist and is included in Set-Cookie."
            )
            response.headers["Set-Cookie"] = f"tenant={t.name}; Path=/"
            return response
    return _log_info_and_respond(
        f"Tenant with ID={tenant_id} is not accessible", 401, title="Unauthorized"
    )


def get_tenants() -> _Response:
    """Return all tenants, that are accessible to the client based on the authentication
    (e.g., all the tenants contained in the JWT token)
    """
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    accessible_tenants = _AccessibleTenants(request, ignore_cookie=True)
    tenants = [
        _obj_to_db.tenant_from_db_model(t) for t in _db_access.get_tenants(accessible_tenants)
    ]
    _log_info(f"Found {len(tenants)} tenants.")
    return _json_response(tenants)


@_controller_with_tenants
def delete_tenant(request: _ProcessedRequest, tenant_id: int) -> _Response:
    """Delete an existing tenant identified by 'tenant_id'.

    The tenant cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(_NO_TENANTS, _db_models.CarDB, criteria={"tenant_id": lambda x: x == tenant_id}):  # type: ignore
        return _log_error_and_respond(
            f"Tenant with ID={tenant_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    response = _db_access.delete(request.tenants, _db_models.TenantDB, tenant_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Tenant with ID={tenant_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Could not delete tenant with ID={tenant_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
