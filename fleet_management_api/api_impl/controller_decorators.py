"""
This module provides decorators for the controller imlpementation in the Fleet Management API.

The decorators pre-load and validate the request data and also the tenant information from the connexion.request object.
"""

from typing import Callable, Concatenate, ParamSpec
import dataclasses

from fleet_management_api.api_impl.api_responses import Response as _Response
from fleet_management_api.api_impl.load_request import load_request as _load_request
from fleet_management_api.api_impl.tenants import (
    AccessibleTenants as _AccessibleTenants,
    get_accessible_tenants as _get_accessible_tenants,
)
from fleet_management_api.api_impl.api_logging import (
    log_invalid_request_body_format as _log_invalid_request_body_format,
    log_error_and_respond as _log_error_and_respond,
)


P = ParamSpec("P")


@dataclasses.dataclass(frozen=True)
class ProcessedRequest:
    """Instance of this class contains the accessible tenants info and JSON data (a list of objects) loaded from a single request.

    If the request does not contain the JSON data, the data field is left as an empty list.
    """

    tenants: _AccessibleTenants
    data: list[dict[str, str | None]] = dataclasses.field(default_factory=list)


# The raw controllers are functions defined in the api_impl/controllers module
RawController = Callable[Concatenate[ProcessedRequest, P], _Response]
Controller = Callable[Concatenate[P], _Response]


def controller_with_tenants(controller: RawController) -> Controller:
    """This decorator provides the controller function with the information about tenants, for which data can be read or modified.

    The controller also prevents calling the controller if
    1) the request body is in invalid format or
    2) tenants are not set up correctly, either the tenant cookie is not set for modifying the data or there are no accessible tenants
    """

    def wrapper(*args, **kwargs):
        request = _load_request(require_data=False)
        if not request:
            return _log_invalid_request_body_format()
        tresponse = _get_accessible_tenants(request)
        if tresponse.status_code != 200:
            return _log_error_and_respond(tresponse.body, tresponse.status_code, title="No tenants")
        tenants = tresponse.body
        assert isinstance(tenants, _AccessibleTenants)
        loaded_request = ProcessedRequest(tenants)
        response = controller(loaded_request, *args, **kwargs)
        return response

    return wrapper


def controller_with_tenants_and_data(controller: RawController) -> Controller:
    """This decorator provides the controller function with the information about tenants, for which data can be created or modified
    and the data itself (in JSON format).

    The controller also prevents calling the controller if
    1) the request body is not a valid JSON or
    2) tenants are not set up correctly, either the tenant cookie is not set for modifying the data or there are no accessible tenants
    """

    def wrapper(*args, **kwargs):
        request = _load_request(require_data=True)
        if not request:
            return _log_invalid_request_body_format()
        tresponse = _get_accessible_tenants(request)
        if tresponse.status_code != 200:
            return _log_error_and_respond(tresponse.body, tresponse.status_code, title="No tenants")
        tenants = tresponse.body
        assert isinstance(tenants, _AccessibleTenants)
        loaded_request = ProcessedRequest(tenants, data=request.data)
        response = controller(loaded_request, *args, **kwargs)
        return response

    return wrapper
