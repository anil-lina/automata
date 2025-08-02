from dagster import ScheduleDefinition, define_asset_job
from .assets.sync import sync_asset

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
