# General information

“/” at the start of the endpoint refers to an absolute path in the API namespace.


# Index
- [API]()
- [Car](#car-endpoints)
- [Car State](#car-state-endpoints)
- [Order](#order-endpoints)
- [Order State](#order-state-endpoints)
- [Platform HW](#platform-hw-endpoints)
- [Route](#route-endpoints)
- [Route Points](#route-points-endpoints)
- [Stop](#stop-endpoints)
- [Security](#endpoints---keycloak-login)


# API endpoints

## /apialive

### HEAD

Check if the API is alive.

Response codes:
- 200: The API is alive.
- 503: A component of the API is not working properly.


# Car endpoints

Car [description](definitions.md#car).

More on endpoints [here](entity_manipulations.md#car).


## /car

### POST

Create a new car.

Request body format: JSON version of the Car.

Response codes:
- 200: Successfully created a new car.
- 400: Bad request. The request body is not a valid Car.
- 404: Not found. Some of the entities referenced by the Car do not exist.


### GET

Finds all cars.

Response codes:
- 200: Returning all existing cars.


### PUT

Update an existing Car indentified by ID. In contrast to the POST method, the ID of the Car is required.

Request body format: JSON version of the Car.

Response codes:
- 200: Successful car update.
- 400: Bad request. The request body is not a valid Car.
- 404: Not found. The Car with the given ID does not exist.

## /car/{carId}:

### GET

Finds car by ID.

Response format: JSON version of the Car.

Response codes:
- 200: Successfully found a car with the given ID.
- 400: Bad request. The carId is not a valid integer.
- 404: Not found. The Car with the given ID does not exist.

### DELETE

Delete a car.

Response codes:
- 200: Successful car removal.
- 400: Bad request. The carId is not a valid integer.
- 404: Not found. The Car with the given ID does not exist.

# Car State endpoints

Car State [description](definitions.md#car-state).

More on endpoints [here](entity_manipulations.md#car-state).

## /carstate[?allAvailable=<allAvailable>]

### POST

Add a new state for a car by ID.

Request body format:
- allAvailable=true: JSON containing list of the Car States.
- allAvailable=false or unspecified: JSON version of the Car State.

Response codes:
- 200: Successfully added new Car State.
- 400: Bad request. The request body is not a valid Car State.
- 404: Not found. The Car with the given ID does not exist.

### GET

Finds states of all cars.

Response codes:
- 200: Returning all existing car states.

## /carstate/{carId}[?allAvailable=<allAvailable>]

### GET

Finds car states by ID.

Response format:
- allAvailable=true: JSON containing list of the Car States.
- allAvailable=false or unspecified: JSON version of the Car State.

Response codes:
- 200: Successfully found a car state.
- 400: Bad request. The carId is not a valid integer.
- 404: Not found. The Car with the given ID does not exist.

# Order endpoints

Order [description](definitions.md#order).

More on endpoints [here](entity_manipulations.md#order).

## /order

### POST

Create a new order.

Request body format: JSON version of the Order.

Response codes:
- 200: Successfully created a new order.
- 400: Bad request. The request body is not a valid Order.
- 404: Not found. Some of the entities referenced by the Order do not exist.

### GET

Finds all orders.

Response body format: JSON array of Order objects.

Response codes:
- 200: Returning all existing orders.

## /order/{orderId}

### GET

Finds order by ID.

Response format: JSON version of the Order.

Response codes:
- 200: Successfully found an order with the given ID.
- 400: Bad request. The orderId is not a valid integer.
- 404: Not found. The Order with the given ID does not exist.

### DELETE

Delete an order.

Response codes:
- 200: Successful order removal.
- 400: Bad request. The orderId is not a valid integer.
- 404: Not found. The Order with the given ID does not exist.

## /order/wait/{carId}

### GET

Get an order by car ID only if it has changed.

Response format: JSON version of the Order.

Response codes:
- 200: Successfully received a new order.
- 400: Bad request. The carId is not a valid integer.
- 404: Not found. The Car with the given ID does not exist.

# Order State endpoints

Order State [description](definitions.md#order-state).

More on endpoints [here](entity_manipulations.md#order-state).

## /orderstate[?since=<timestamp>&wait=<wait>]

### POST

Create a new order state.

Request body format: JSON version of the OrderState.

Query options since and wait determine the behavior as described in [Wait mechanism documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo)

Response codes:
- 200: Successfully added new order state.
- 400: Bad request. The request body is not a valid Order State.
- 404: Not found. The Order with the given ID does not exist.

### GET

Finds states of all Orders.

Response body format: JSON array of OrderState objects.

Response codes:
- 200: Returning all existing order states.

## /orderstate/{orderId}

### GET

Finds Order States by the Order ID.

Response format: JSON version of the Order State.

Response codes:
- 200: Successfully found order state.
- 400: Bad request. The orderId is not a valid integer.
- 404: Not found. The Order with the given ID does not exist.


# Platform HW endpoints

Platform HW [description](definitions.md#platform-hw).

More on endpoints [here](entity_manipulations.md#platform-hw).

## /platformhw

### POST

Create a new platform HW.

Request body format: JSON version of the PlatformHW.

Response codes:
- 200: Successfully created a new platform HW.
- 400: Bad request. The request body is not a valid Platform HW.
- 404: Not found. Some of the entities referenced by the Platform HW do not exist.

### GET

Finds all platform HW.

Response body format: JSON array of PlatformHW objects.

Response codes:
- 200: Returning all existing platform HW.

## /platformhw/{platformHwId}

### GET

Finds platform HW by ID.

Response format: JSON version of the PlatformHW.

Response codes:
- 200: Successfully found platform HW.
- 400: Bad request. The platformHwId is not a valid integer.
- 404: Not found. The Platform HW with the given ID does not exist.

### DELETE

Delete a platform HW.

Response codes:
- 200: Successful platform HW removal.
- 400: Bad request. The platformHwId is not a valid integer.
- 404: Not found. The Platform HW with the given ID does not exist.


# Route endpoints

Route [description](definitions.md#route).

More on endpoints [here](entity_manipulations.md#route).

## /route

### POST

Create a new route.

Request body format: JSON version of the Route.

Response codes:
- 200: Successfully created a new route.
- 400: Bad request. The request body is not a valid Route.
- 404: Not found. Some of the entities referenced by the Route do not exist.

### GET

Finds all Routes.

Response body format: JSON array of Route objects.

Response codes:
- 200: Returning all existing routes.

### PUT

Update an existing route by ID.

Request body format: JSON version of the Route.

Response codes:
- 200: Successful route update.
- 400: Bad request. The request body is not a valid Route.
- 404: Not found. The Route with the given ID does not exist.

## /route/{routeId}

### GET

Finds route by ID.

Response format: JSON version of the Route.

Response codes:
- 200: Successfully found route.
- 400: Bad request. The routeId is not a valid integer.
- 404: Not found. The Route with the given ID does not exist.

### DELETE

Delete a route.

Response codes:
- 200: Successful route removal.
- 400: Bad request. The routeId is not a valid integer.
- 404: Not found. The Route with the given ID does not exist.

# Route Points endpoints

Route Points [description](definitions.md#route-points).

More on endpoints [here](entity_manipulations.md#route-points).

## /routepoints/{routeId}

### GET

Finds route points for the given route identified by the route's ID.

Response format: JSON version of the RoutePoints.

Response codes:
- 200: Successfully found route points.
- 400: Bad request. The routeId is not a valid integer.
- 404: Not found. The Route with the given ID does not exist.

### POST

Redefine route points for the given route identified by the route's ID.

Request body format: JSON version of the RoutePoints.

Response codes:
- 200: Successfully found route points.
- 400: Bad request. The request body is not a valid Route Points.
- 404: Not found. The Route with the given ID does not exist.

# Stop endpoints

Stop [description](definitions.md#stop).

More on endpoints [here](entity_manipulations.md#stop).

## /stop

### POST

Create a new stop.

Request body format: JSON version of the Stop.

Response codes:
- 200: Successfully created a new stop.
- 400: Bad request. The request body is not a valid Stop.
- 404: Not found. Some of the entities referenced by the Stop do not exist.

### GET

Finds all stops.

Response body format: JSON array of Stop objects.

Response codes:
- 200: Returning all existing stops.

### PUT

Update an existing stop by ID.

Request body format: JSON version of the Stop.

Response codes:
- 200: Successful stop update.
- 400: Bad request. The request body is not a valid Stop.
- 404: Not found. The Stop with the given ID does not exist.

## /stop/{stopId}

### GET

Finds stop by ID.

Response format: JSON version of the Stop.

Response codes:
- 200: Successfully found a stop.
- 400: Bad request. The stopId is not a valid integer.
- 404: Not found. The Stop with the given ID does not exist.

## /stop/{stopId}

### GET

Finds stop by ID.

Response format: JSON version of the Stop.

Response codes:
- 200: Found a stop.
- 400: Bad request. The stopId is not a valid integer.
- 404: Not found. The Stop with the given ID does not exist.

### DELETE

Delete a stop.

Response codes:
- 200: Successful stop removal.
- 400: Bad request. The stopId is not a valid integer.
- 404: Not found. The Stop with the given ID does not exist.


# Endpoints - Keycloak Login

## /login

### GET

Login using Keycloak.

Response codes:
- 302: Redirect to the Keycloak authentication.
- 500: The login failed due to an internal server error.

## /token_get

### GET

Callback endpoint for the Keycloak to receive JWT token.

Response codes:
- 200: Returns a standard Keycloak token.
- 500: The login failed due to an internal server error.

Query options:
- ?state
    - State returned by the Keycloak authentication.
    - type: string
    - example: your_state_infos

- ?session_state
    - Session state returned by the Keycloak authentication.
    - type: string
    - example: 167e141d-2f55-4d...

- ?iss
    - Code issuer returned by the Keycloak authentication.
    - type: string
    - example: http%3A%2F%2Flocalhost%3A8081%2Frealms%2Fmaster

- ?code
    - Code used for JWT token generation returned by Keycloak authentication.
    - type: string
    - example: 5dea27d2-4b2d-48...


## /token_refresh

### GET

Endpoint to receive JWT token from refresh token.

Response codes:
- 200: Returns a new standard Keycloak token.
- 500: Token refresh failed due to an internal server error.

Query options:
?refresh_token
- Refresh token used for JWT token generation.
- required
- type: string
- example: eyJhbGciOiJIUzI1NiIsI...

