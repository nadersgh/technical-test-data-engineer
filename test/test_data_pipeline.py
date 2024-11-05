from unittest.mock import patch
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from src.data_ingestion_pipeline.assets import (
    fetch_songs_data, fetch_users_data, fetch_history_data,
    load_songs_data, load_users_data, load_history_data, test_engine
)

# Create an in-memory SQLite engine for testing
test_engine_instance = create_engine("sqlite:///:memory:")

# Fixture to set up the test engine
@pytest.fixture(scope="session", autouse=True)
def setup_test_engine():
    with patch("src.data_ingestion_pipeline.assets.get_engine", return_value=test_engine_instance):
        yield

# Fixture to mock requests.get responses
@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get

# 1. Tests for fetch assets

def test_fetch_songs_data(mock_requests_get):
    mock_response = {
        "items": [
            {
                "id": 1,
                "name": "Song 1",
                "artist": "Artist 1",
                "songwriters": "Writer 1",
                "duration": "3:30",
                "genres": "Pop",
                "album": "Album 1",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    mock_requests_get.return_value.status_code = 200

    df = fetch_songs_data()
    assert isinstance(df, pd.DataFrame)
    assert "id" in df.columns
    assert "name" in df.columns
    assert len(df) == 1

def test_fetch_users_data(mock_requests_get):
    mock_response = {
        "items": [
            {
                "id": 1,
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "gender": "Female",
                "favorite_genres": "Pop",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    mock_requests_get.return_value.status_code = 200

    df = fetch_users_data()
    assert isinstance(df, pd.DataFrame)
    assert "id" in df.columns
    assert "first_name" in df.columns
    assert len(df) == 1

def test_fetch_history_data(mock_requests_get):
    mock_response = {
        "items": [
            {
                "user_id": 1,
                "items": [101, 102],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    mock_requests_get.return_value.status_code = 200

    df = fetch_history_data()
    assert isinstance(df, pd.DataFrame)
    assert "user_id" in df.columns
    assert "created_at" in df.columns
    assert len(df) == 1


# 2. Tests for load assets

def test_load_songs_data():
    test_data = pd.DataFrame([
        {
            "id": 0,
            "name": "string",
            "artist": "string",
            "songwriters": "string",
            "duration": "string",
            "genres": "string",
            "album": "string",
            "created_at": "2024-11-02T05:28:51.111Z",
            "updated_at": "2024-11-02T05:28:51.111Z"
        }
    ])

    load_songs_data(test_data)

    # Verify data is in the test database
    with test_engine_instance.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM songs")).scalar()
        assert count == 1

def test_load_users_data():
    test_data = pd.DataFrame([
        {
            "id": 28347,
            "first_name": "Laura",
            "last_name": "Mathews",
            "email": "jwatts@example.net",
            "gender": "Gender questioning",
            "favorite_genres": "Metal",
            "created_at": "2024-01-25T12:35:51.422906",
            "updated_at": "2024-07-07T15:32:08.545762"
        }
    ])

    load_users_data(test_data)

    # Verify data is in the test database
    with test_engine_instance.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM users")).scalar()
        assert count == 1

def test_load_history_data():
    test_data = pd.DataFrame([
        {
            "user_id": 28347,
            "items": [28208, 3974, 11925, 62140, 72218],
            "created_at": "2024-10-29T03:58:40.584034",
            "updated_at": "2024-10-30T08:36:34.683958"
        }
    ])

    load_history_data(test_data)

    # Verify data in both 'history' and 'history_items' tables in test DB
    with test_engine_instance.connect() as connection:
        history_count = connection.execute(text("SELECT COUNT(*) FROM history")).scalar()
        assert history_count == 1

        history_items_count = connection.execute(text("SELECT COUNT(*) FROM history_items")).scalar()
        assert history_items_count == 5