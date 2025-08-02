# This file makes the `dagster_oracle_to_oci` directory a Python package.
from .assets.sync import sync_asset
from .resources.oracle import oracle_resource
from .resources.oci import oci_resource

from dagster import Definitions, ScheduleDefinition, define_asset_job

# Define a job that will materialize the asset
sync_job = define_asset_job(
    name="oracle_to_oci_sync_job",
    selection=[sync_asset]
)

# Define a schedule to run the job hourly
hourly_schedule = ScheduleDefinition(
    job=sync_job,
    cron_schedule="0 * * * *",
    execution_timezone="UTC",
)

defs = Definitions(
    assets=[sync_asset],
    resources={
        "oracle": oracle_resource,
        "oci": oci_resource,
    },
    schedules=[hourly_schedule],
)
