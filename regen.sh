#!/bin/bash


npx @openapitools/openapi-generator-cli generate -i openapi/openapi.yaml \
-g python-flask -o . --additional-properties=packageName=fleet_management_api
