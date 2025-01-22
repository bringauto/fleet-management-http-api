from fleet_management_api.models import Tenant as _Tenant
from fleet_management_api.database import db_access as _db_access
from fleet_management_api.database import db_models as _db_models
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
)
from fleet_management_api.api_impl.load_request import RequestEmpty as _RequestEmpty
from fleet_management_api.database.db_access import NO_TENANT
from fleet_management_api.api_impl.security import AccessibleTenants as _AccessibleTenants


def get_tenants() -> _Response:
    """Get all existing tenants."""
    tenant_id_models = _db_access.get(NO_TENANT, _db_models.TenantDB)
    tenant_ids: list[_Tenant] = [
        _obj_to_db.tenant_from_db_model(tenant_id_model) for tenant_id_model in tenant_id_models
    ]
    _log_info(f"Found {len(tenant_ids)} tenants.")
    return _json_response(tenant_ids)


def delete_tenant(tenant_id: int) -> _Response:
    """Delete an existing tenant identified by 'tenant_id'.

    The tenant cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(_db_models.CarDB, criteria={"tenant_id": lambda x: x == tenant_id}):  # type: ignore
        return _log_error_and_respond(
            f"Tenant with ID={tenant_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    request = _RequestEmpty.load()
    if not request:
        return _log_invalid_request_body_format()
    tenant = _AccessibleTenants(request, "")
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
