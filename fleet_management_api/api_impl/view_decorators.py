from typing import Callable, Any

from fleet_management_api.api_impl.api_responses import Response as _Response
from fleet_management_api.api_impl.load_request import (
    RequestJSON as _RequestJSON,
    RequestEmpty as _RequestEmpty,
)
from fleet_management_api.api_impl.tenants import (
    AccessibleTenants as _AccessibleTenants,
    get_accessible_tenants as _get_accessible_tenants,
)
from fleet_management_api.api_impl.api_logging import (
    log_invalid_request_body_format as _log_invalid_request_body_format,
    log_error_and_respond as _log_error_and_respond,
)


def view_with_tenants(
    view: Callable[[_AccessibleTenants, Any], _Response],
) -> Callable[[Any], _Response]:

    def wrapper(*args, **kwargs):
        request = _RequestEmpty.load()
        if not request:
            return _log_invalid_request_body_format()
        tresponse = _get_accessible_tenants(request)
        if tresponse.status_code != 200:
            return _log_error_and_respond(tresponse.body, tresponse.status_code, title="No tenants")
        tenants = tresponse.body
        assert isinstance(tenants, _AccessibleTenants)
        response = view(tenants, *args, **kwargs)
        return response

    return wrapper


def view_with_tenants_and_data(
    view: Callable[[_AccessibleTenants, dict | list[dict], Any], _Response],
) -> Callable:

    def wrapper(*args, **kwargs):
        request = _RequestJSON.load()
        if not request:
            return _log_invalid_request_body_format()
        tresponse = _get_accessible_tenants(request)
        if tresponse.status_code != 200:
            return _log_error_and_respond(tresponse.body, tresponse.status_code, title="No tenants")
        tenants = tresponse.body
        assert isinstance(tenants, _AccessibleTenants)
        response = view(tenants, request.data, *args, **kwargs)
        return response

    return wrapper
