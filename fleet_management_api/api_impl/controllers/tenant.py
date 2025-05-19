from fleet_management_api.database import db_models as _db_models, db_access as _db_access
from fleet_management_api.api_impl import obj_to_db as _obj_to_db
from fleet_management_api.models import Tenant as _Tenant
from fleet_management_api.api_impl.api_logging import (
    log_info as _log_info,
    log_warning_or_error_and_respond as _log_warning_or_error_and_respond,
    log_error_and_respond as _log_error_and_respond,
    log_info_and_respond as _log_info_and_respond,
)
from fleet_management_api.api_impl.api_responses import (
    Response as _Response,
    json_response as _json_response,
    text_response as _text_response,
)
from fleet_management_api.api_impl.tenants import NO_TENANTS as _NO_TENANTS
from fleet_management_api.api_impl.controller_decorators import (
    with_processed_request as _with_processed_request,
    ProcessedRequest as _ProcessedRequest,
)


@_with_processed_request(ignore_tenant_cookie=True)
def set_tenant_cookie(request: _ProcessedRequest, tenant_id: int, **kwargs) -> _Response:
    """Set the tenant cookie to the tenant with the given ID.

    If the tenant with the ID does not exist, return a Unauthorized response."""
    tenants_in_db = _db_access.get_tenants(request.tenants)
    # Validate at runtime even when assertions are disabled
    if not isinstance(tenant_id, int):
        return _log_warning_or_error_and_respond(
            "Tenant ID must be an integer", 400, title="invalid tenant ID type"
        )
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


@_with_processed_request(ignore_tenant_cookie=True, require_data=True)
def create_tenants(request: _ProcessedRequest, **kwargs) -> _Response:
    """Create a new tenant with the given name.

    The tenant name must be unique.
    """

    tenants = [_Tenant.from_dict(t) for t in request.data]
    response = _db_access.add_tenants(*[t.name for t in tenants])

    if response.status_code == 200:
        posted_db_models: list[_db_models.TenantDB] = response.body
        for tenant in posted_db_models:
            _log_info(f"Stop (name='{tenant.name}) has been created.")
        models = [_obj_to_db.tenant_from_db_model(m) for m in posted_db_models]
        return _json_response(models)
    elif response.status_code == 400 and "null value in column" in response.body["detail"]:
        return _log_error_and_respond(
            f"Could not create tenants. {response.body['detail']}",
            400,
            title="Not-null constraint violation",
        )
    else:
        return _log_warning_or_error_and_respond(
            f"Could not create tenants. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )


@_with_processed_request(ignore_tenant_cookie=True)
def get_tenants(request: _ProcessedRequest, **kwargs) -> _Response:
    """Return all tenants, that are accessible to the client based on the authentication
    (e.g., all the tenants contained in the JWT token)
    """
    db_tenants = [
        _obj_to_db.tenant_from_db_model(t) for t in _db_access.get_tenants(request.tenants)
    ]
    _log_info(f"Found {len(db_tenants)} tenants.")
    return _json_response(db_tenants)


@_with_processed_request
def delete_tenant(request: _ProcessedRequest, tenant_id: int) -> _Response:
    """Delete an existing tenant identified by 'tenant_id'.

    The tenant cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(_NO_TENANTS, _db_models.CarDB, criteria={"tenant_id": lambda x: x == tenant_id}):  # type: ignore
        return _log_warning_or_error_and_respond(
            f"Tenant with ID={tenant_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    response = _db_access.delete(request.tenants, _db_models.TenantDB, tenant_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Tenant with ID={tenant_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_warning_or_error_and_respond(
            f"Could not delete tenant with ID={tenant_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
