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
The Car represents a physical object with assigned list of Car States.

# Car State
Car State is a data structure containing attributes of a given Car, that change in time.
Required data:
- ID: integer
- carID: integer
- status: enum; Available options = {idle, charging, out_of_order, stopped_by_phone}
- fuel: int
- speed: float
- position: GNSSPosition

# Order
The Order represents a data structure for controlling behavior of a given Car.

# Order State

# Platform HW

# Route

# Route Enti