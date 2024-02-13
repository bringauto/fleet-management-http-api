# Index
- [Car](#car)
- [Car State](#car-state)
- [Order](#order)
- [Order State](#order-state)
- [Platform HW](#platform-hw)
- [Route](#route)
- [Route Points](#route-points)
- [Stop](#stop)


# Car
The Car represents a physical object with an assigned list of Car States.

# Car State
Car State is a data structure containing attributes of a given Car, that change in time.
Required data:
- ID: unsigned integer
- carID: unsigned integer
- status: enum, available options = {idle, charging, out_of_order, stopped_by_phone}
- fuel: unsigned integer
- speed: float
- position: GNSSPosition

# Order
The Order represents a data structure for controlling the behavior of a given Car.

Required data:
- ID: unsigned integer
- priority: enum, available options = {low, normal, high}
- user ID: unsigned integer
- notification: string
- target stop ID: unsigned integer
- route ID: unsigned integer
- notification phone: Mobile Phone


# Order State

# Platform HW

# Route

# Route Enti