# Tenants on Fleet Management HTTP API

To add multi-tenancy support to the Fleet Management HTTP API, the server for each request extracts information about the tenant or tenants, under which the data is accessed or modified.

## Accessible tenants

The list of tenants, which the user can read. It can be unrestricted, meaning the user can access all tenants and thus all the data on the server, or restricted to a subset of tenants.

## Current tenant

The tenant, under which the data is accessed or modified.

- if the current tenant is empty, the user can read data from all accessible tenants, but cannot write data to the database.
- if the current tenant is not empty, the user can read and write data fo the current tenant only.

If the accessible tenants is not empty and the current tenant is set, the current tenant must be among accessible tenants.

# Implementation

## Accessible tenants

The accessible tenants are extracted from the request in the following way:

- if API key is provided, the list of accessible tenants is set to empty list, making them unrestricted.
- otherwise, if OAuth authorization is used, the accessible tenants are extracted from the JWT token.
- then, if the request does not contain JWT token containing the accessible tenants, an error is returned.

## Current tenant

The current tenant is extracted from the request in the following way:

- if there is a cookie with the name `tenant`, the current tenant is set to the value of the cookie (it can be empty).
- otherwise, if the cookie is not set, the current tenant is left empty.

If the current tenant is not empty, it is further checked against the accessible tenants. If the accessible tenants is not empty, the current tenant must be among accessible tenants, otherwise an authentication error is returned.

# Storing tenants by the server

The tenants have their own table in the server's database. Each tenant is added to the database in the moment it is used for adding data it owns.

The API then provides endpoints for listing the accessible tenants and for deleting an existing tenant specified by its ID.
