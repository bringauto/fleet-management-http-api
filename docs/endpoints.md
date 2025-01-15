# General information

“/” at the start of the endpoint refers to an absolute path in the API namespace.

# Index

- [API](#api-endpoints)
- [Car](#car-endpoints)
- [Car Action](#car-action-endpoints)
- [Car State](#car-state-endpoints)
- [Order](#order-endpoints)
- [Order State](#order-state-endpoints)
- [Platform HW](#platform-hw-endpoints)
- [Route](#route-endpoints)
- [Route Visualization](#route-visualization-endpoints)
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

Create new cars.

Request body format: JSON version of the list of Cars.

Response codes:

- 200: Successfully created new cars.
- 400: Bad request. The request body is not valid list of Cars.
- 404: Not found. Some of the entities referenced by a Car do not exist.

### GET

Finds all cars.

Response codes:

- 200: Returning all existing cars.

### PUT

Update existing Cars. In contrast to the POST method.

Request body format: JSON version of a list of Cars to be updated.

Response codes:

- 200: Successful cars' update.
- 400: Bad request. The request body is not a valid list of Car.
- 404: Not found. Some of the cars to be updated do not exist.

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


# Car Action endpoints

Car Action State [description](definitions.md#car-action-state).

More on endpoints [here](entity_manipulations.md#car-action-state).

## /action/car/{carId}

### GET

Returns action states for a car with the given ID.

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only action states with timestamp >= since.
- 'wait' - boolean (default=False). If True and no action states would be returned, the request will wait for the next relevant action states to be added.
- 'lastN' - integer (default=0). Limits the number of returned action states. If the number of action states is greater than the specified limit, the server returns N action states with the highest timestamp or (if timestamp are equal) the highest ID. If set to 0 or less, number of returned action states is NOT limited.

Query options since and wait determine the behavior as described in [Wait mechanism documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo)

Response format: JSON array of CarActionState objects.

Response codes:

- 200: Successfully found a car action states.
- 400: Bad request. The carId is not a valid integer.
- 404: Not found. The Car with the given ID does not exist.

## /action/car/{carId}/pause

### POST

Pause the car with the given ID if the car is not paused.

Response codes:

- 200: Successfully paused the car.
- 400: Bad request. Either the carId is not a valid integer or the car is not in state that allows pausing.
- 404: Not found. The Car with the given ID does not exist.


## /action/car/{carId}/unpause

### POST

Unpause the car with the given ID if the car is paused.

Response codes:

- 200: Successfully unpaused the car.
- 400: Bad request. Either the carId is not a valid integer or the car is not in state that allows unpausing.
- 404: Not found. The Car with the given ID does not exist.


# Car State endpoints

Car State [description](definitions.md#car-state).

More on endpoints [here](entity_manipulations.md#car-state).

## /carstate

### POST

Add new car states (not necessarily for a single car). Query parameters are ignored for this method.

Request body format: JSON containing a list of Car States data.

Response codes:

- 200: Successfully added new Car States.
- 400: Bad request. The request body is not a valid list of Car States.
- 404: Not found. Some of the Cars do not exist.

### GET

Finds states of all cars.

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only states with timestamp >= since.
- 'wait' - boolean (default=False). If True and no states would be returned, the request will wait for the next relevant state to be added.
- 'lastN' - integer (default=0). Limits the number of returned states. If the number of states is greater than the specified limit, the server returns N states with the highest timestamp or (if timestamp are equal) the highest ID. If set to 0 or less, number of returned states is NOT limited.

Query options since and wait determine the behavior as described in [Wait mechanism documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo)

Response codes:

- 200: Returning all existing car states.

## /carstate/{carId}

### GET

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only states with timestamp >= since.
- 'wait' - boolean (default=False). If True and no states would be returned, the request will wait for the next relevant state to be added.
- 'lastN' - integer (default=0). Limits the number of returned states. If the number of states is greater than the specified limit, the server returns N states with the highest timestamp or (if timestamp are equal) the highest ID. If set to 0 or less, number of returned states is NOT limited.

Query options since and wait determine the behavior as described in [Wait mechanism documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo)

Response codes:

- 200: Successfully found a car state.
- 400: Bad request. The carId is not a valid integer.
- 404: Not found. The Car with the given ID does not exist.

# Order endpoints

Order [description](definitions.md#order).

More on endpoints [here](entity_manipulations.md#order).

## /order

### POST

Create new orders.

Request body format: JSON version of the list of Orders.

Query parameters are ignored for this method.

Response codes:

- 200: Successfully created new orders.
- 400: Bad request. The request body is not a valid list of Orders.
- 403: Cannot add orders. Maximum number of [active orders](entity_manipulations.md#order) specified in the API configuration has been reached. After some of the existing orders are completed or canceled, new orders can be added.
- 404: Not found. Some of the entities referenced by the Orders do not exist.

### GET

Finds all orders.

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only orders with timestamp >= since.

Response body format: JSON array of Order objects.

Response codes:

- 200: Returning all existing orders.

## /order/{carId}

### GET

Finds all orders assigned to a car referenced by car ID.

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only orders with timestamp >= since.

Response body format: JSON array of Order objects.

Response codes:

- 200: Returning all existing orders for given Car.
- 404: Not found. The Car with the given ID does not exist.

## /order/{carId}/{orderId}

### GET

Finds order by car ID and order ID.

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

# Order State endpoints

Order State [description](definitions.md#order-state).

More on endpoints [here](entity_manipulations.md#order-state).

## /orderstate

### POST

Create new order states.

Request body format: JSON version of a list of Order States.

Query parameters are ignored for this method.

Response codes:

- 200: Successfully added new order states.
- 400: Bad request. The request body is not a valid list of Order States.
- 403: Forbidden. The Order States cannot be accepted by the API, because some of the Orders has already received Order State with status DONE or CANCELED.
- 404: Not found. Some of the Orders do not exist.

### GET

Finds states of all Orders.

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only states with timestamp >= since.
- 'wait' - boolean (default=False). If True and no states would be returned, the request will wait for the next relevant state to be added.
- 'lastN' - integer (default=0). Limits the number of returned states. If the number of states is greater than the specified limit, the server returns N states with the highest timestamp or (if timestamp are equal) the highest ID. If set to 0 or less, number of returned states is NOT limited.
- 'carId' - integer or empty (empty by default). If set, the API returns only states for the Orders assigned to a Car with ID=carId. If the car does not exist, an empty list is returned.

Query options since and wait determine the behavior as described in [Wait mechanism documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo)

Response body format: JSON array of OrderState objects.

Response codes:

- 200: Returning all existing order states.

## /orderstate/{orderId}

### GET

Finds Order States by the Order ID.

Query parameters:

- 'since' - timestamp in milliseconds (default=0). API returns only states with timestamp >= since.
- 'wait' - boolean (default=False). If True and no states would be returned, the request will wait for the next relevant state to be added.
- 'lastN' - integer (default=0). Limits the number of returned states. If the number of states is greater than the specified limit, the server returns N states with the highest timestamp or (if timestamp are equal) the highest ID. If set to 0 or less, number of returned states is NOT limited.

Query options since and wait determine the behavior as described in [Wait mechanism documentation](https://docs.google.com/document/d/1DOHSFV2ui8C7Oyrui1sVxadSqaxPjlY3uif-EK2-Uxo)

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

Create new platform HWs.

Request body format: JSON version of the list of PlatformHWs.

Response codes:

- 200: Successfully created new platform HWs.
- 400: Bad request. The request body is not a valid list of Platform HW.
- 404: Not found. Some of the entities referenced by some of the Platform HWs do not exist.

### GET

Finds all platform HW.

Response body format: JSON array of PlatformHW objects.

Response codes:

- 200: Returning all existing platform HWs.

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

Create new routes.

Request body format: JSON version of the list of Routes.

Response codes:

- 200: Successfully created new routes.
- 400: Bad request. The request body is not a valid list of Routes.
- 404: Not found. Some of the entities referenced by some of the Routes do not exist.

### GET

Finds all Routes.

Response body format: JSON array of Route objects.

Response codes:

- 200: Returning all existing routes.

### PUT

Update existing routes.

Request body format: JSON version of the list of Routes to be updated.

Response codes:

- 200: Successful routes' update.
- 400: Bad request. The request body is not a valid list of Routes.
- 404: Not found. Some of the Routes do not exist.

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

# Route Visualization endpoints

Route Visualization [description](definitions.md#route-visualization).

More on endpoints [here](entity_manipulations.md#route-visualization).

## /route-visualization/{routeId}

### GET

Finds route visualization for the given route identified by the route's ID.

Response format: JSON version of the RouteVisualization.

Response codes:

- 200: Successfully found route visualization.
- 400: Bad request. The routeId is not a valid integer.
- 404: Not found. The Route with the given ID does not exist.

### POST

Redefine route visualizations for the given routes identified by the routes' IDs.

Request body format: JSON version of the list of RouteVisualization to be updated.

Response codes:

- 200: Successfully updated route visualizations.
- 400: Bad request. The request body is not a valid list of Route Visualizations.
- 404: Not found. Some of the Routes do not exist.

# Stop endpoints

Stop [description](definitions.md#stop).

More on endpoints [here](entity_manipulations.md#stop).

## /stop

### POST

Create new stops.

Request body format: JSON version of the list of Stop.

Response codes:

- 200: Successfully created new stops.
- 400: Bad request. The request body is not a valid list of Stops.
- 404: Not found. Some of the entities referenced by some of the Stops do not exist.

### GET

Finds all stops.

Response body format: JSON array of Stop objects.

Response codes:

- 200: Returning all existing stops.

### PUT

Update existing stops.

Request body format: JSON version of the list of Stops to be updated.

Response codes:

- 200: Successful stops' update.
- 400: Bad request. The request body is not a valid list of Stop.
- 404: Not found. Some of the Stops do not exist.

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
