import oci
from dagster import resource, Field

@resource({
    "user": Field(str, description="OCID of the user"),
    "fingerprint": Field(str, description="API key fingerprint"),
    "key_file": Field(str, description="Path to the private API key file"),
    "tenancy": Field(str, description="OCID of the tenancy"),
    "region": Field(str, description="OCI region (e.g., 'us-ashburn-1')"),
})
def oci_resource(context):
    """
    A Dagster resource for connecting to OCI Object Storage.
    """
    config = context.resource_config

    # Validate the config
    oci.config.validate_config(config)

    # Create and return the client
    object_storage_client = oci.object_storage.ObjectStorageClient(config)

    yield object_storage_client
