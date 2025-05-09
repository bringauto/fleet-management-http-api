"""Constants used in the Fleet Management API implementation, namely by the tenant-related modules."""

AUTHORIZATION_HEADER_NAME = "Authorization"
AUTHORIZATION_ENVIRONMENT_NAME = "HTTP_AUTHORIZATION"
TENANT_PAYLOAD_ITEM = (
    "group"  # The name of the field in the JWT payload that contains the tenant information.
)
