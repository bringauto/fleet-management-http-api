# Design decisions

**(Optional) [Order State](#order-state) request wait period** - When the request to obtain messages (commands or statuses) from the server is made and no such messages are available at the moment, the request can optionally wait for a predefined amount of time (wait period specified in the API server configuration) for the messages to arrive to the server. For further information, see the wait mechanism [documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo).

**Timestamp** is an abbreviation for *Unix timestamp*. For any message (command or status) the timestamp is automatically set to a value corresponding to the time the message was passed to the corresponding POST method of the API.

**Unix timestamp** is used in milliseconds resolution.

All keys identifying data in the response/request structures shall be lowercase. All whitespaces shall be replaced by "_".

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
- phone number: string

Example:
```json
{
    "phone_number": "+420123456789"
}
```

# Entities
- [Car](#car)
- [Car State](#car-state)
- [Order](#order)
- [Order State](#order-state)
- [Platform HW](#platform-hw)
- [Route](#route)
- [Route Points](#route-points)
- [Stop](#stop)

API automatically assigns an ID to each entity passed to a POST method.

The Entity ID is an unsigned integer with a UNIQUE value for a given API instance.

## Car

The Car represents a physical object with an assigned list of [Car States](#car-state).

Required data:
- name: string
- platform HW ID: unsigned integer
- car admin phone: [Mobile Phone](#mobile-phone)
- default route ID: unsigned integer
- under test: boolean

Example:
```json
{
    "id": 12,
    "name": "Car 1",
    "platform_hw_id": 1,
    "car_admin_phone": "123456789",
    "default_route_id": 1,
    "under_test": false
}
```

## Car State

Data structure containing attributes of a given Car, that change in time.

Required data:
- car ID: unsigned integer
- status: enum, available options = {idle, charging, out_of_order, stopped_by_phone}
- fuel: unsigned integer
- speed: float
- position: [GNSSPosition](#gnss-position)

Example:
```json
{
    "id": 12,
    "car_id": 1,
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

Example:
```json
{
    "id": 12,
    "priority": "normal",
    "user_id": 1,
    "notification": "Please deliver the package to the address",
    "target_stop_id": 1,
    "route_id": 1,
    "notification_phone": "+420123456789"
}
```

## Order State

Data structure containing attributes of a given Order, that change in time.

Required data:
- order status: enum, available options = {to_accept, accepted, in_progress, done, cancelled}
- order ID: unsigned integer

Data assigned by API:
- Timestamp: unsigned integer

Example:
```json
{
    "id": 12,
    "order_id": 1,
    "order_status": "accepted",
    "timestamp": 1707805396
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
- name: string
- stop IDs: set of unsigned integers

Example:
```json
{
    "id": 12,
    "name": "Route 1",
    "stop_ids": {1, 2, 3}
}
```

## Route Points

Route Points represent an ordered set of physical locations for visualization of a particular [Route](#route) on a map.

Required data:
- route ID: unsigned integer
- points: list of GNSSPosition

Example:
```json
{
    "id": 12,
    "route_id": 1,
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
    ]
}
```

## Stop

Stop represents a target physical location, that can be assigned to an Order.

Required data:
- name: string
- position: [GNSSPosition](#gnss-position)
- notification phone: [Mobile Phone](#mobile-phone)

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
    "notification_phone": "+420123456789"
}
```