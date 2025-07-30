from dagster import ScheduleDefinition, define_asset_job, AssetSelection

all_assets_job = define_asset_job("all_assets_job", selection=AssetSelection.all())

daily_data_load_schedule = ScheduleDefinition(
    job=all_assets_job,
    cron_schedule="0 0 * * *",  # every day at midnight
    name="daily_data_load_schedule",
)
