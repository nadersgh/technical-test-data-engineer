from dagster import Definitions

from src.data_ingestion_pipeline.assets import fetch_users_data, fetch_songs_data, fetch_history_data, load_songs_data, \
    load_users_data, load_history_data
from src.data_ingestion_pipeline.jobs import data_ingestion_job

defs = Definitions(
    assets=[fetch_songs_data, fetch_users_data, fetch_history_data, load_songs_data, load_users_data, load_history_data],
    jobs=[data_ingestion_job],
)