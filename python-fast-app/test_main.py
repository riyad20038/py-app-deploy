import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from database import search_movies_by_year, upload_movie_data

client = TestClient(app)

# Sample test data
MOCK_MOVIES = [
    {"movie_name": "Inception", "year_of_release": 2010, "box_office": 829.9, "director": "Christopher Nolan", "producer": "Emma Thomas", "cast": "Leonardo DiCaprio"},
    {"movie_name": "Interstellar", "year_of_release": 2014, "box_office": 677.5, "director": "Christopher Nolan", "producer": "Emma Thomas", "cast": "Matthew McConaughey"}
]

@pytest.fixture
def mock_search_movies():
    """Mock the search_movies_by_year function to return sample movie data."""
    with patch("database.search_movies_by_year", return_value=MOCK_MOVIES):
        yield

@pytest.fixture
def mock_upload_movie():
    """Mock the upload_movie_data function to simulate database insertion."""
    with patch("database.upload_movie_data") as mock_upload:
        yield mock_upload


# ✅ 1. Test Home Page
def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Hollywood Movie Database" in response.text


# ✅ 2. Test Movie Search (Valid Year)
def test_search_movies(mock_search_movies):
    response = client.post("/", data={"year_of_release": 2010})
    assert response.status_code == 200
    assert "Inception" in response.text  # Ensures movie appears in response


# ✅ 3. Test Movie Search (Invalid Year)
def test_search_movies_invalid():
    response = client.post("/", data={"year_of_release": "abcd"})  # Sending string instead of int
    assert response.status_code == 422  # FastAPI should return validation error


# ✅ 4. Test Upload Movie Data (Valid Input)
def test_upload_movie_data(mock_upload_movie):
    response = client.post("/upload_data", data={
        "movie_name": "Avatar",
        "year_of_release": 2009,
        "box_office": 2847.0,
        "director": "James Cameron",
        "producer": "Jon Landau",
        "cast": "Sam Worthington"
    })
    assert response.status_code == 200
    assert "Movie uploaded successfully!" in response.text


# ✅ 5. Test Upload Movie Data (Missing Field)
def test_upload_movie_data_missing_field():
    response = client.post("/upload_data", data={
        "movie_name": "Titanic",  # Missing year_of_release
        "box_office": 2200.0,
        "director": "James Cameron",
        "producer": "Jon Landau",
        "cast": "Leonardo DiCaprio"
    })
    assert response.status_code == 422  # FastAPI should return validation error


# ✅ 6. Test Upload Movie Data (Invalid Data Type)
def test_upload_movie_data_invalid_type():
    response = client.post("/upload_data", data={
        "movie_name": "Titanic",
        "year_of_release": "twenty-twelve",  # Invalid year format
        "box_office": "two billion",  # Invalid float format
        "director": "James Cameron",
        "producer": "Jon Landau",
        "cast": "Leonardo DiCaprio"
    })
    assert response.status_code == 422  # FastAPI should return validation error
