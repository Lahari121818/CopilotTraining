import pytest
from fastapi.testclient import TestClient

import src.app as api


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        api,
        "activities",
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["current@mergington.edu"],
            },
            "Art Club": {
                "description": "Explore drawing and painting",
                "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
                "max_participants": 16,
                "participants": [],
            },
        },
    )

    with TestClient(api.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_activities = api.activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in api.activities["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "current@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert api.activities["Chess Club"]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = "current@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in api.activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_nonparticipant(client):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "current@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
