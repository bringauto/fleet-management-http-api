
# Index
- [Car](#car)
- [Car State](#car-state)
- [Order](#order)
- [Order State](#order-state)
- [Platform HW](#platform-hw)
- [Route](#route)
- [Route Points](#route-points)
- [Stop](#stop)


# Manipulation of API Entities


## Car

### Post

Requirements:
- A unique ID.
- [Platform HW](#platformhw) must exist and must not be used by some other Car.

Result:
- A Car is created.

### Delete

Requirements:
- There must be no [Order](#order) referencing the car.

Result:
- The Car is deleted.
- All the [Car States](#car-state) referencing the Car are deleted.


## Car State

There is a maximum number $N_{car\,states}$ of Car States to be stored by the API.

### Post

Requirements:
- A unique ID.
- The referenced [Car](#car) must exist.

Result:
- A Car State is created.
- Oldest Car States might be deleted, so the number of states stored by the API for the particular [Car](#car) is not greater than $N_{car\,states}$.


## Order

### Post

Requirements:
- A unique ID.
- [Target Stop](#stop) of the Order must exist.
- [Route](#route) referenced by the Order must exist.
- [Car](#car) referenced by the Order must exist.

Result:
- An Order is created.

### Delete

Requirements:
- A unique ID.

Result:
- The Order is deleted.
- All [Order States](#order-state) of this Order are deleted.


## Order State

There is a maximum number of Order States $N_{order\,states}$ that can be stored by the API.

### Post

Requirements:
- A unique ID.
- The [Order](#order) must exist.

Result:
- An Order State is created.
- The Order State's timestamp is updated to match the time it was posted.
- Oldest Order States might be deleted, so the number of states stored by the API for a particular [Order](#order) is not greater than $N_{order\,states}$.
- All the Clients waiting for new Order States of a particular [Order](#order) receive a response (for the order state GET method).


## Platform HW

### Post

Requirements:
- A unique ID.

Result:
- A Platform HW is created.

### Delete

Requirements:
- There must be no [Car](#car) referencing the Platform HW.

Result:
- The Platform HW is deleted.


## Route

### Post

Requirements:
- A unique ID.
- All [Stops](#stop) referenced by the Route must exist.

Result:
- A Route is created.
- [Route Points](#route-points) object with an empty list of points is created.

### Delete

Requirements:
- There must be no [Order](#order) referencing the Route.

Result:
- The Route is deleted.
- The corresponding [Route Points](#route-points) object is deleted.


## Route Points

### Post

Requirements:
- A unique ID.
- Referenced [Route](#route) must exist.

Result:
- The newly posted Route Points object replaces the already existing one.

### Delete
The Route Points object is always deleted if and only if the referenced [Route](#route) is deleted or when a new Route Points object is posted with the same Route ID.


## Stop

### Post

Requirements:
- A unique ID.

Result:
- A Stop is created.

### Delete

Requirements:
- There must be no [Order](#order) or [Route](#route) referencing the Stop.

Result
- The Stop is deleted.