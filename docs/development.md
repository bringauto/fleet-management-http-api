# Entities with assigned States

The models used by the API include models with assigned states. Current examples are

- Car and Car State,
- Car and Car Action State,
- Order and Order State.

## Entity State

When such an Entity is created, make sure, that an Entity State is automatically created as well!!!

For example, when a Car is created, a Car State with status `out_of_order` is created.
In the case of new Order, an Order State with status `to_accept` is created.

Every state must have (at least) the following attributes:

- ID of the corresponding Entity
- timestamp

All GET methods returning object states must have the following filtering options in terms of their corresponding Entity:

- returning all States for all the existing Entities,
- returning all States for the particular Entity,

For both of these, further filtering must be available:

- return only those States inclusively newer than given timestamp,
- return only up to last N States (with higher timestamp or, if timestamps are equal, with the higher IDs).

### Last State

Each Entity has an attribute "lastState", containing the newest State of the Entity (i.e., State with the largest timestamp, or possibly, largest ID, if some states share the same timestamp).

## Tenant

Each entity except for API keys and Tenants have a Tenant ID attribute representing the Tenant to which the entity belongs.

For non-state Entities, the tenant has to be set in a cookie or in the header of the request to inform the server to which tenant
the entity belongs.

Entity States are exceptions to this rule. The Tenant ID is automatically set by the server when the entity is created. The Tenant ID is equal to the Tenant ID of the corresponding Entity.

The rule is, the Entity belongs to a tenant to which the client has access.
