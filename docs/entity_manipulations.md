
# Index
- [Car](#car)
- [Car State](#car-state)
- [Order](#order)
- [Order State](#order-state)
- [Platform HW](#platform-hw)
- [Route](#route)
- [Route Visualization](#route-visualization)
- [Stop](#stop)


# Manipulation of API Entities

## Car

Entity [description](definitions.md#car).

### Post

The method accepts a list of Car objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- [Platform HW](#platformhw) must exist and must not be used by some other Car.
- [Default route ID](#route) must exist if specified.
- The name must be unique.

Result:
- The Car ID is automatically set by the server.
- A Car is created.
- A [Car State](#car-state) created with the `out_of_order` status.

If creation of any of the objects fails, no changes occur on the server.

### Put

The method accepts a list of Car objects. The server processes the list in the order of the list elements. For each updated object the following applies:

Requirements:
- The Car must exist.
- [Platform HW](#platformhw) must exist and must not be used by some other Car.
- [Default route ID](#route) must exist if specified.
- The name must be unique.

Result:
- A Car is updated.

If update of any of the objects fails, no changes occur on the server.


### Delete

Requirements:
- There must be no [Order](#order) referencing the car.

Result:
- The Car is deleted.
- All the [Car States](#car-state) referencing the Car are deleted.


## Car State

Entity [description](definitions.md#car-state).

There is a maximum number $N_{car\,states}$ of Car States to be stored by the API.

### Post

The method accepts a list of CarState objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- The referenced [Car](#car) must exist.
- There must be no CarState with status DONE or CANCELED for the same Car.

Result:
- The Car State ID is automatically set by the server.
- The Car State's timestamp is set to match the time it was posted.
- A Car State is created.
- Oldest Car States might be deleted, so the number of states stored by the API for the particular [Car](#car) is not greater than $N_{car\,states}$.
- All the Clients waiting for some new Car States of a particular [Car](#car) receive a response (for the order state GET method).

If creation of any of the objects fails, no changes occur on the server.

## Order

Entity [description](definitions.md#order).

Each order falls into one of the following categories:
- **Inactive** - the order has the last [Order State](#order-state) with status DONE or CANCELED.
- **Active** - otherwise.

### Post

The method accepts a list of Order objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- The current number of active orders is lower than specified maximum number.
- [Target Stop](#stop) of the Order must exist.
- [Route](#route) referenced by the Order must exist and must contain the Target Stop.
- [Car](#car) referenced by the Order must exist.

Result:
- The Order ID is automatically set by the server.
- The Order's timestamp is set to match the time it was posted.
- An Order is created.
- An [Order State](#order-state) created with the `to_accept` status.

If creation of any of the objects fails, no changes occur on the server.

### Delete

Requirements:
- None

Result:
- The Order is deleted.
- All [Order States](#order-state) of this Order are deleted.


## Order State

Entity [description](definitions.md#order-state).

There is a maximum number of Order States $N_{order\,states}$ that can be stored by the API.

### Post

The method accepts a list of OrderState objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- The [Order](#order) must exist.

Result:
- The Order State ID is automatically set by the server.
- The Order State's timestamp is set to match the time it was posted.
- An Order State is created IF there is no older Order State with a final status (DONE or CANCELED).
- Oldest Order States might be deleted, so the number of states stored by the API for a particular [Order](#order) is not greater than $N_{order\,states}$.
- All the Clients waiting for some new Order States of a particular [Order](#order) receive a response (for the order state GET method).
- If the Order State has a final status (DONE or CANCELED) and the server already stores maximum allowed number of inactive [Orders](#order), the inactive Order with which has been first marked as inactive is deleted.

If creation of any of the objects fails, no changes occur on the server.

## Platform HW

Entity [description](definitions.md#platform-hw).

### Post

The method accepts a list of PlatformHW objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- None

Result:
- The Platform HW ID is automatically set by the server.
- A Platform HW is created.

If creation of any of the objects fails, no changes occur on the server.

### Delete

Requirements:
- There must be no [Car](#car) referencing the Platform HW.
- The name must be unique.

Result:
- The Platform HW is deleted.


## Route

Entity [description](definitions.md#route).

### Post

The method accepts a list of Route objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- All [Stops](#stop) referenced by the Route must exist.
- The name must be unique.

Result:
- The Route ID is automatically set by the server.
- A Route is created.
- [Route Visualization](#route-visualization) object with an empty list of points is created.

If creation of any of the objects fails, no changes occur on the server.

## Put

The method accepts a list of Route objects. The server processes the list in the order of the list elements. For each updated object the following applies:

Requirements:
- The Route must exist
- All [Stops](#stop) referenced by the Route must exist.
- The Route name must not be taken by another Route.

Result:
- A Route is updated.

If update of any of the objects fails, no changes occur on the server.

### Delete

Requirements:
- There must be no [Order](#order) referencing the Route.

Result:
- The Route is deleted.
- The corresponding [Route Visualization](#route-visualization) object is deleted.
- The default route ID attribute of every [Car](#car) equal to this deleted Route is set to None.


## Route Visualization

Entity [description](definitions.md#route-visualization).

### Post

The method accepts a list of RouteVisualization objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- The referenced [Route](#route) must exist.

Result:
- A new Route Visualization ID is automatically generated by the server.
- The newly posted Route Visualization object replaces the already existing one.

If creation of any of the objects fails, no changes occur on the server.

### Delete
The Route Visualization object is always deleted if and only if the referenced [Route](#route) is deleted or when a new Route Visualization object is posted with the same Route ID.


## Stop

Entity [description](definitions.md#stop).

### Post

The method accepts a list of Stop objects. The server processes the list in the order of the list elements. For each created object the following applies:

Requirements:
- The name must be unique.

Result:
- The Stop ID is automatically set by the server.
- A Stop is created.

If creation of any of the objects fails, no changes occur on the server.

### Put

The method accepts a list of Stop objects. The server processes the list in the order of the list elements. For each updated object the following applies:

Requirements:
- The name must be unique.
- The Stop must exist.

Result:
- A Stop is updated.

If update of any of the objects fails, no changes occur on the server.

### Delete

Requirements:
- There must be no [Order](#order) or [Route](#route) referencing the Stop.

Result
- The Stop is deleted.