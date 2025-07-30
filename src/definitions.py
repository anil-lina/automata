from dagster import Definitions
from src.assets.oracle import load_oracle_assets
from src.assets.oci import load_oci_assets
from src.sensors.daily_trigger import daily_data_load_schedule, all_assets_job
from dagster import json_console_logger

defs = Definitions(
    assets=[*load_oracle_assets(), *load_oci_assets()],
    schedules=[daily_data_load_schedule],
    jobs=[all_assets_job],
    loggers={"console": json_console_logger},
)
