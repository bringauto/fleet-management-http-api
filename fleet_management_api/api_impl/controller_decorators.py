"""
This module provides decorators for the controller imlpementation in the Fleet Management API.

The decorators pre-load and validate the request data and also the tenant information from the connexion.request object.
"""

from typing import Callable, Concatenate, ParamSpec

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


P = ParamSpec("P")


def controller_with_tenants(
    controller: Callable[Concatenate[_AccessibleTenants, P], _Response],
) -> Callable[Concatenate[P], _Response]:
    """This decorator provides the controller function with the information about tenants, for which data can be read or modified.

    The controller also prevents calling the controller if
    1) the request body is in invalid format or
    2) tenants are not set up correctly, either the tenant cookie is not set for modifying the data or there are no accessible tenants
    """

    def wrapper(*args, **kwargs):
        request = _RequestEmpty.load()
        if not request:
            return _log_invalid_request_body_format()
        tresponse = _get_accessible_tenants(request)
        if tresponse.status_code != 200:
            return _log_error_and_respond(tresponse.body, tresponse.status_code, title="No tenants")
        tenants = tresponse.body
        assert isinstance(tenants, _AccessibleTenants)
        response = controller(tenants, *args, **kwargs)
        return response

    return wrapper


def controller_with_tenants_and_data(
    controller: Callable[Concatenate[_AccessibleTenants, list[dict], P], _Response],
) -> Callable[Concatenate[P], _Response]:
    """This decorator provides the controller function with the information about tenants, for which data can be created or modified
    and the data itself (in JSON format).

    The controller also prevents calling the controller if
    1) the request body is not a valid JSON or
    2) tenants are not set up correctly, either the tenant cookie is not set for modifying the data or there are no accessible tenants
    """

    def wrapper(*args, **kwargs):
        request = _RequestJSON.load()
        if not request:
            return _log_invalid_request_body_format()
        tresponse = _get_accessible_tenants(request)
        if tresponse.status_code != 200:
            return _log_error_and_respond(tresponse.body, tresponse.status_code, title="No tenants")
        tenants = tresponse.body
        assert isinstance(tenants, _AccessibleTenants)
        response = controller(tenants, request.data, *args, **kwargs)
        return response

    return wrapper
