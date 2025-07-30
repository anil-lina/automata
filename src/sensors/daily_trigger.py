from dagster import ScheduleDefinition, define_asset_job, AssetSelection

all_assets_job = define_asset_job("all_assets_job", selection=AssetSelection.all())

# This schedule runs hourly. To run it bi-hourly, change the cron_schedule to "0 */2 * * *".
# For more information on cron schedules, see: https://crontab.guru/
daily_data_load_schedule = ScheduleDefinition(
    job=all_assets_job,
    cron_schedule="0 * * * *",  # every hour
    name="hourly_data_load_schedule",
)
