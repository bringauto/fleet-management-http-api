from fleet_management_api.api_impl.controllers.order import (
    set_max_n_of_active_orders as _set_max_n_of_active_orders,
    set_max_n_of_inactive_orders as _set_max_n_of_inactive_orders,
)
from fleet_management_api.script_args.configs import Data


def set_up_data(data_config: Data) -> None:
    _set_max_n_of_active_orders(data_config.orders.max_active_orders)
    _set_max_n_of_inactive_orders(data_config.orders.max_inactive_orders)
