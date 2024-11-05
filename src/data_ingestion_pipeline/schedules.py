from dagster import schedule
from .jobs import data_ingestion_job


@schedule(cron_schedule="0 0 * * *", job=data_ingestion_job, execution_timezone="UTC")
def daily_data_ingestion_schedule(_context):
    return {}