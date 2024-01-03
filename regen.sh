#!/bin/bash

pushd server
npx @openapitools/openapi-generator-cli generate -i ../input_openapi_yaml/input_openapi.yaml -g python-flask -o . --additional-properties=packageName=openapi_server
popd