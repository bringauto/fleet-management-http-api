# Entities with assigned States

The models used by the API include models with assigned states. Current examples are
- Car and Car State,
- Order and Order State.

When such an Entity is created, make sure, that an Entity State is automatically created as well!!! For example, when a Car is created, a Car State with status `out_of_order` is created.
