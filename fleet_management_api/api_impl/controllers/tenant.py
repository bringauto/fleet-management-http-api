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
from fleet_management_api.api_impl.tenants import AccessibleTenants as _AccessibleTenants
from fleet_management_api.api_impl.tenants import NO_TENANTS


def set_tenant_cookie(tenant_id: int) -> _Response:
    """Set a cookie with the tenant ID."""
    assert isinstance(tenant_id, int), "Tenant ID must be an integer"
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    accessible_tenants = _AccessibleTenants(request, ignore_cookie=True)
    accessible_tenants_in_db = _db_access.get_tenants(accessible_tenants)
    for t in accessible_tenants_in_db:
        if t.id == tenant_id:
            response = _text_response(
                f"Tenant '{t.name}' does exist and is included in Set-Cookie."
            )
            response.headers["Set-Cookie"] = f"tenant={t.name}; Path=/"
            return response
    return _log_error_and_respond(
        f"Tenant with ID={tenant_id} is not accessible", 401, title="Unauthorized"
    )


def get_tenants() -> _Response:
    """Get all existing tenants."""
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    accessible_tenants = _AccessibleTenants(request, ignore_cookie=True)
    tenants = [
        _obj_to_db.tenant_from_db_model(t) for t in _db_access.get_tenants(accessible_tenants)
    ]
    _log_info(f"Found {len(tenants)} tenants.")
    return _json_response(tenants)


def delete_tenant(tenant_id: int) -> _Response:
    """Delete an existing tenant identified by 'tenant_id'.

    The tenant cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(NO_TENANTS, _db_models.CarDB, criteria={"tenant_id": lambda x: x == tenant_id}):  # type: ignore
        return _log_error_and_respond(
            f"Tenant with ID={tenant_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenant = _AccessibleTenants(request)
    response = _db_access.delete(tenant, _db_models.TenantDB, tenant_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Tenant with ID={tenant_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Could not delete tenant with ID={tenant_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
