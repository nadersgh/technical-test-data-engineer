from dagster import job
from .assets import fetch_songs_data, fetch_users_data, fetch_history_data, load_songs_data, load_users_data, load_history_data

@job(
    name="data_ingestion_job",
    description="Fetches data from the API and loads it into the database",
)
def data_ingestion_job():
    songs_data = fetch_songs_data()
    users_data = fetch_users_data()
    history_data = fetch_history_data()

    load_songs_data(songs_data)
    load_users_data(users_data)
    load_history_data(history_data)

