import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleet_management_api.models.error import Error  # noqa: E501
from fleet_management_api.models.tenant import Tenant  # noqa: E501
from fleet_management_api import util


def delete_tenant(tenant_id):  # noqa: E501
    """Delete Tenant with the given ID.

     # noqa: E501

    :param tenant_id: ID of Tenant to delete.
    :type tenant_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_tenants():  # noqa: E501
    """Find and return all existing Tenant.

     # noqa: E501


    :rtype: Union[List[Tenant], Tuple[List[Tenant], int], Tuple[List[Tenant], int, Dict[str, str]]
    """
    return 'do some magic!'


def set_tenant_cookie():  # noqa: E501
    """Make the server to send back response with set-cookie header to set cookie equal to the name of the tenand with the tenantId.

     # noqa: E501


    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'
