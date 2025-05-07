"""
This module provides decorators for the controller imlpementation in the Fleet Management API.

The decorators pre-load and validate the request data and also the tenant information from the connexion.request object.
"""

from typing import Callable, Concatenate, ParamSpec, Optional
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


def controller_with_tenants(
    controller: Optional[Callable[Concatenate[ProcessedRequest, P], _Response]] = None,
    /,
    *,
    require_data: bool = False,
) -> (
    Callable[Concatenate[P], _Response]
    | Callable[
        [Callable[Concatenate[ProcessedRequest, P], _Response]], Callable[Concatenate[P], _Response]
    ]
):
    """This decorator provides the controller function with the information about tenants, for which data can be created, read or modified.

    The decorator also prevents calling the controller if
    1) the request body is invalid (i.e., it is not a valid JSON if the data is required) or
    2) tenants are not set up correctly, either the tenant cookie is not set for modifying the data or there are no accessible tenants

    Instead of calling the controller, the decorator returns a response with appropriate status code, error message and also logs the event.
    """

    def _controller_with_tenants(
        controller: Callable[Concatenate[ProcessedRequest, P], _Response],
    ) -> Callable[Concatenate[P], _Response]:

        def wrapper(*args, **kwargs) -> _Response:
            request = _load_request(require_data=require_data)
            if not request:
                return _log_invalid_request_body_format()
            tresponse = _get_accessible_tenants(request)
            if tresponse.status_code != 200:
                return _log_error_and_respond(
                    tresponse.body, tresponse.status_code, title="No tenants"
                )
            tenants = tresponse.body
            assert isinstance(tenants, _AccessibleTenants)
            loaded_request = ProcessedRequest(tenants, data=request.data)
            response = controller(loaded_request, *args, **kwargs)
            return response

        return wrapper

    if controller is None:
        return _controller_with_tenants
    else:
        return _controller_with_tenants(controller)
