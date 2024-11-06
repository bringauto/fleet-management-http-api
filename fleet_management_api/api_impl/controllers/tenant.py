import connexion  # type: ignore

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
from fleet_management_api.response_consts import OBJ_NOT_FOUND as _OBJ_NOT_FOUND


def create_tenants() -> _Response:
    """Create new tenants.

    If some of the tenants' creation fails, no objects are added to the server.

    The tenant creation can succeed only if:
    - there is no tenant with the same name.
    """
    if not connexion.request.is_json:
        return _log_invalid_request_body_format()
    else:
        tenants = [_Tenant.from_dict(p) for p in connexion.request.get_json()]
        tenant_db_model = [_obj_to_db.tenant_to_db_model(p) for p in tenants]
        response: _Response = _db_access.add(*tenant_db_model)
        if response.status_code == 200:
            inserted_models: list[_Tenant] = [
                _obj_to_db.tenant_from_db_model(item) for item in response.body
            ]
            for p in inserted_models:
                assert p.id is not None
                _log_info(f"Tenant (name='{p.name}) has been created.")
            return _json_response(inserted_models)
        else:
            return _log_error_and_respond(
                f"Tenant (names='{[p.name for p in tenants]}) could not be created. {response.body['detail']}",
                response.status_code,
                response.body["title"],
            )


def get_tenants() -> _Response:
    """Get all existing tenants."""
    tenant_id_models = _db_access.get(_db_models.TenantDBModel)
    tenant_ids: list[_Tenant] = [
        _obj_to_db.tenant_from_db_model(tenant_id_model) for tenant_id_model in tenant_id_models
    ]
    _log_info(f"Found {len(tenant_ids)} tenants.")
    return _json_response(tenant_ids)


def get_tenant(tenant_id: int) -> _Response:
    """Get an existing tenant identified by 'tenant_id'."""
    tenant_models = _db_access.get(
        _db_models.TenantDBModel, criteria={"id": lambda x: x == tenant_id}
    )
    tenants = [
        _obj_to_db.tenant_from_db_model(tenant_id_model) for tenant_id_model in tenant_models
    ]
    if len(tenants) == 0:
        return _log_error_and_respond(
            f"Tenant with ID={tenant_id} was not found.",
            404,
            title=_OBJ_NOT_FOUND,
        )
    else:
        _log_info(f"Found {len(tenants)} tenants with ID={tenant_id}")
        return _json_response(tenants[0])


def delete_tenant(tenant_id: int) -> _Response:
    """Delete an existing tenant identified by 'tenant_id'.

    The tenant cannot be deleted if assigned to a Car.
    """
    if _db_access.exists(_db_models.CarDBModel, criteria={"tenant_id": lambda x: x == tenant_id}):  # type: ignore
        return _log_error_and_respond(
            f"Tenant with ID={tenant_id} cannot be deleted because it is assigned to a car.",
            400,
            title="Cannot delete object",
        )
    response = _db_access.delete(_db_models.TenantDBModel, tenant_id)
    if response.status_code == 200:
        return _log_info_and_respond(f"Tenant with ID={tenant_id} has been deleted.")
    else:
        note = " (not found)" if response.status_code == 404 else ""
        return _log_error_and_respond(
            f"Could not delete tenant with ID={tenant_id}{note}. {response.body['detail']}",
            response.status_code,
            response.body["title"],
        )
