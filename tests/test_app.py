from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


BASE_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["existing@mergington.edu"],
    }
}


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def isolated_activities(monkeypatch):
    test_activities = deepcopy(BASE_ACTIVITIES)
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


def test_get_activities_returns_activity_data(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[activity_name] == isolated_activities[activity_name]


def test_signup_adds_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in isolated_activities[activity_name]["participants"]


def test_signup_rejects_unknown_activity(client, isolated_activities):
    # Arrange
    activity_name = "Unknown Activity"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert isolated_activities[activity_name]["participants"].count(email) == 1


def test_cancel_signup_removes_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Canceled signup for {email} in {activity_name}"
    }
    assert email not in isolated_activities[activity_name]["participants"]


def test_cancel_signup_rejects_unknown_activity(client, isolated_activities):
    # Arrange
    activity_name = "Unknown Activity"
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_cancel_signup_rejects_unregistered_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"