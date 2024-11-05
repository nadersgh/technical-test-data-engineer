import os
import uuid
import requests
import pandas as pd
from dagster import asset, RetryPolicy, Jitter, Backoff
from sqlalchemy import create_engine

# Database connection configuration
DB_PATH = os.path.join("data", "recommendation_system.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
default_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Define a test engine, which can be overridden in test environments
test_engine = None

# Base URL for the API
API_BASE_URL = "http://localhost:8000"


def get_engine():
    """Retrieve the appropriate database engine, using the test engine if specified, otherwise defaulting to production."""
    return test_engine if test_engine is not None else default_engine


fetching_data_from_api_retry_policy = RetryPolicy(
    max_retries=3,
    delay=2,  # Start with a 2-second delay
    backoff=Backoff.EXPONENTIAL,  # Exponential backoff multiplier
    jitter=Jitter.PLUS_MINUS,
)


@asset(
    name="fetch_songs_data",
    description="Fetch songs data from the API",
    group_name="Songs",
    retry_policy=fetching_data_from_api_retry_policy
)
def fetch_songs_data() -> pd.DataFrame:
    response = requests.get(f"{API_BASE_URL}/tracks")
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data.get("items", []))  # Return an empty DataFrame if no items


@asset(
    name="fetch_users_data",
    description="Fetch users data from the API",
    group_name="Users",
)
def fetch_users_data() -> pd.DataFrame:
    response = requests.get(f"{API_BASE_URL}/users")
    response.raise_for_status()
    data = response.json()
    # Extract "items" if present; return an empty DataFrame otherwise
    return pd.DataFrame(data.get("items", []))


@asset(
    name="load_songs_data",
    description="Load song data into the database",
    group_name="Songs",
)
def load_songs_data(songs_data: pd.DataFrame):
    """Load song data directly into the 'songs' table in the database."""
    with get_engine().connect() as connection:
        songs_data.to_sql("songs", connection, if_exists="append", index=False)


@asset(
    name="load_users_data",
    description="Load user data into the database",
    group_name="Users",
)
def load_users_data(users_data: pd.DataFrame):
    """Load user data directly into the 'users' table in the database."""
    with get_engine().connect() as connection:
        users_data.to_sql("users", connection, if_exists="append", index=False)


@asset(
    name="fetch_history_data",
    description="Fetch listen history data from the API",
    group_name="History",
)
def fetch_history_data() -> pd.DataFrame:
    response = requests.get(f"{API_BASE_URL}/listen_history")
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data.get("items", []))


@asset(
    name="load_history_data",
    description="Load listen history data into the database",
    group_name="History",
)
def load_history_data(history_data: pd.DataFrame):
    """Load history data into 'history' and 'history_items' tables in the database."""
    history_data['history_id'] = [str(uuid.uuid4()) for _ in range(len(history_data))]

    # Prepare history_items data
    history_items_data = []
    for _, row in history_data.iterrows():
        history_id = row['history_id']
        if isinstance(row['items'], list):
            for item_id in row['items']:
                history_items_data.append({"history_id": history_id, "item_id": item_id})

    history_items_df = pd.DataFrame(history_items_data)

    # Separate main history data and save to 'history' table
    history_main = history_data[['history_id', 'user_id', 'created_at', 'updated_at']].drop_duplicates()

    # Insert main history history_items data into 'history_items' table
    with get_engine().connect() as connection:
        history_main.to_sql("history", connection, if_exists="append", index=False)
        history_items_df.to_sql("history_items", connection, if_exists="append", index=False)
