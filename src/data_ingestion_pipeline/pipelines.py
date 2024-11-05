from dagster import job, repository

from .jobs import data_ingestion_job
from .schedules import daily_data_ingestion_schedule

@repository
def data_ingestion_pipeline():
    return [data_ingestion_job, daily_data_ingestion_schedule]