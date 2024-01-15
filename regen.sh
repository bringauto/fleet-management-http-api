#!/bin/bash


npx @openapitools/openapi-generator-cli generate -i openapi.yaml \
-g python-flask -o . --additional-properties=packageName=fleet_management_api
