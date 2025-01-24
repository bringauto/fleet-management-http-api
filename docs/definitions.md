# Design decisions

**(Optional) [Order State](#order-state) request wait period** - When the request to obtain messages (commands or statuses) from the server is made and no such messages are available at the moment, the request can optionally wait for a predefined amount of time (wait period specified in the API server configuration) for the messages to arrive to the server. For further information, see the wait mechanism [documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo).

**Timestamp** is an abbreviation for _Unix timestamp_. For any message (command or status) the timestamp is automatically set to a value corresponding to the time the message was passed to the corresponding POST method of the API.

**Unix timestamp** is used in milliseconds resolution.

All keys identifying data in the response/request structures shall be lowercase. All whitespaces shall be replaced by "\_".

**Authentication** is supported! If the request is unauthorized then the API shall return HTTP code 401.

# Primitives

## GNSS Position

Data structure representing a position in the GNSS coordinate system.

Required data:

- latitude: float
- longitude: float
- altitude: float

Example:

```json
{
  "latitude": 49.06143,
  "longitude": 16.93658,
  "altitude": 430
}
```

## Mobile Phone

Required data:

- phone: string

Example:

```json
{
  "phone": "+420123456789"
}
```

# Entities

- [Car](#car)
- [Car Action State](#car-action-state)
- [Car State](#car-state)
- [Order](#order)
- [Order State](#order-state)
- [Platform HW](#platform-hw)
- [Route](#route)
- [Route Visualization](#route-visualization)
- [Stop](#stop)
- [Tenant](#tenant)

API automatically assigns an ID to each entity passed to a POST method.

The Entity ID is an unsigned integer with a UNIQUE value for a given API instance.

## Car

The Car represents a physical object with an assigned list of [Car States](#car-state).

Required data:

- name: UTF-8 encoded string
- platform HW ID: unsigned integer
- car admin phone: [Mobile Phone](#mobile-phone)
- default route ID: unsigned integer
- under test: boolean

Data assigned by API:

- id: unsigned integer
- timestamp: unsigned integer
- last state: [Car State](#car-state)

Example:

```json
{
  "id": 9,
  "timestamp": 1707805396152,
  "name": "Car 1",
  "platformHwId": 1,
  "carAdminPhone": "123456789",
  "defaultRouteId": 1,
  "underTest": false,
  "lastState": {
    "carId": 9,
    "fuel": 56,
    "id": 1,
    "speed": 10.5,
    "status": "driving",
    "timestamp": 1713774431780
  }
}
```

## Car Action State

Data structure containing action status of a given Car, meaning how the Car reacts to existing Orders (the actual logic is implemented in components further down the line to the Car).

Required data:

- car ID: unsigned integer
- status: enum, available options = {`paused`, `unpaused`}

Example:

```json
{
  "id": 12,
  "timestamp": 1707805396753,
  "carId": 1,
  "status": "paused"
}
```

## Car State

Data structure containing attributes of a given Car, that change in time.

Required data:

- car ID: unsigned integer
- status: enum, available options = {`idle`, `charging`, `out_of_order`, `paused_by_button`}
- fuel: unsigned integer
- speed: float
- position: [GNSSPosition](#gnss-position)

Example:

```json
{
  "id": 12,
  "timestamp": 1707805396753,
  "carId": 1,
  "status": "idle",
  "fuel": 100,
  "speed": 0,
  "position": {
    "latitude": 49.06143,
    "longitude": 16.93658,
    "altitude": 430
  }
}
```

## Order

The Order represents a data structure for controlling the behavior of a given Car.

Required data:

- priority: enum, available options = {low, normal, high}
- user ID: unsigned integer
- notification: string
- target stop ID: unsigned integer
- route ID: unsigned integer
- notification phone: Mobile Phone

Data assigned by API:

- id: unsigned integer
- timestamp: unsigned integer (time of the order's creation)
- last state: [Car State](#car-state)

Example:

```json
{
  "id": 12,
  "priority": "normal",
  "timestamp": 1707805396456,
  "userId": 1,
  "notification": "Please deliver the package to the address",
  "targetStopId": 1,
  "routeId": 1,
  "notificationPhone": "+420123456789",
  "lastState": {
    "id": 8,
    "orderId": 12,
    "status": "done",
    "timestamp": 17090774556492
  }
}
```

## Order State

Data structure containing attributes of a given Order, that change in time.

Required data:

- order status: enum, available options = {to_accept, accepted, in_progress, done, cancelled}

Data assigned by API:

- order ID: unsigned integer
- Timestamp: unsigned integer

Example:

```json
{
  "id": 12,
  "orderId": 1,
  "orderStatus": "accepted",
  "timestamp": 1707805396123
}
```

## Platform HW

This represents a Hardware component required by the Car.

Required data:

- name: string

Example:

```json
{
  "id": 18,
  "name": "Platform HW 1"
}
```

## Route

Route groups Stops together.

Required data:

- name: UTF-8 encoded string
- stop IDs: set of unsigned integers

Data assigned by API:

- id: unsigned integer

Example:

```json
{
    "id": 12,
    "name": "Route 1",
    "stopIds": {1, 2, 3}
}
```

## Route Visualization

Route Visualization represent an ordered set of physical locations for visualization of a particular [Route](#route) on a map.

Required data:

- route ID: unsigned integer
- points: list of GNSSPosition
- hexcolor: string

Data assigned by API:

- id: unsigned integer

Example:

```json
{
  "id": 12,
  "routeId": 1,
  "points": [
    {
      "latitude": 49.06143,
      "longitude": 16.93658,
      "altitude": 430
    },
    {
      "latitude": 49.06143,
      "longitude": 16.93658,
      "altitude": 430
    }
  ],
  "hexcolor": "#FF0000"
}
```

## Stop

Stop represents a target physical location, that can be assigned to an Order.

Required data:

- name: UTF-8 encoded string
- position: [GNSSPosition](#gnss-position)
- notification phone: [Mobile Phone](#mobile-phone)

Data assigned by API:

- id: unsigned integer

Example:

```json
{
  "id": 12,
  "name": "Stop 1",
  "position": {
    "latitude": 49.06143,
    "longitude": 16.93658,
    "altitude": 430
  },
  "notificationPhone": "+420123456789"
}
```

## Tenant

Tenant represents a data owner on the server.

Required data:

- name: UTF-8 encoded string

Data assigned by API:

- id: unsigned integer

Example:

```json
{
  "id": 12,
  "name": "Company X"
}
```
