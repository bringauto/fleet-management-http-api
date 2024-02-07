
# Index
- [Car](#car)
- [Car State](#car-state)
- [Order](#order)
- [Order State](#order-state)
- [Platform HW Id](#platform-hw-id)
- [Route](#route)
- [Stop](#stop)


# Manipulation of API Entities

## Car

### Post

Requirements:
- [Platform HW ID](#platformhwid) must exist and must not be used by some other Car.

Result:
- Car is created.

### Delete

Requirements:
- There must be no [Order](#order) referencing the car.

Result:
- Car is deleted.
- All [Car States](#car-state) referencing the Car are deleted.



## Car State

There is a maximum number $N_{car\,states}$ of Car States to be stored by the API.

### Post

Requirements:
- Unique ID.
- [Car](#car) must exist.

Result:
- Car State is created.
- Oldest Car States might be deleted, so the number of states stored by the API for the particular [Car](#car) is not greater than $N_{car\,states}$.



## Order

### Post

Requirements:
- Unique ID.
- [Target Stop](#stop) of the Order must exist.
- [Route](#route) referenced by the Order must exist.
- [Car](#car) referenced by the Order must exist.

Result:
- Order is created.

### Delete

Requirements:
- Unique ID.

Result:
- The Order is deleted.
- All [Order States](#order-state) of this Order are deleted.


## Order State

There is a maximum number $N_{order\,states}$ of Order States to be stored by the API.

### Post

Requirements:
- Unique ID.
- The [Order](#order) must exist.

Result:
- Order State is created.
- Oldest Order States might be deleted, so the number of states stored by the API for the particular [Order](#order) is not greater than $N_{order\,states}$.



## Platform HW ID

### Post

Requirements:
- Unique ID.

Result:
- Platform HW ID is created.

### Delete

Requirements:
- There must be no [Car](#car) referencing the Platform HW ID.

Result:
- The Platform HW ID is deleted.


## Route

### Post

Requirements:
- Unique ID.
- All [Stops](#stop) referenced by the Route must exist.

Result:
- Route is created.
- [Route Points](#route-points) with empty list of points are created.

### Delete

Requirements:
- There must be no [Car](#car) referencing the Platform HW ID.

Result:
- The Platform HW ID is deleted.


## Route Points

### Post

Requirements:
- Referenced [Route](#route) must exist.

Result:
- The newly posted Route Points replace already existing Route Points.


## Stop

### Post

Requirements:
- Unique ID.

Result:
- Stop is created.

### Delete

Requirements:
- There must be no [Order](#order) or [Route](#route) referencing the Stop.

Result
- The Stop is deleted.