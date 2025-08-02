# This file makes the `dagster_oracle_to_oci` directory a Python package.
from .assets.sync import sync_asset
from .resources.oracle import oracle_resource
from .resources.oci import oci_resource

from dagster import Definitions

defs = Definitions(
    assets=[sync_asset],
    resources={
        "oracle": oracle_resource,
        "oci": oci_resource,
    },
)
