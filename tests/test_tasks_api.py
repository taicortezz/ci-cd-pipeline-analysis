import pytest
from fastapi.testclient import TestClient

from app.main import app, task_service


@pytest.fixture(autouse=True)
def clear_tasks():
    task_service.clear()


@pytest.fixture
def client():
    return TestClient(app)


def create_task(client, title="Study CI", priority="medium"):
    response = client.post(
        "/tasks",
        json={
            "title": title,
            "description": "Prepare pipeline experiment",
            "priority": priority,
        },
    )
    return response


def test_create_task_returns_created_task(client):
    response = create_task(client)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Study CI"
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert "created_at" in data


def test_create_task_with_invalid_payload_returns_validation_error(client):
    response = client.post("/tasks", json={"title": "Missing fields"})

    assert response.status_code == 422


def test_create_task_with_empty_title_returns_validation_error(client):
    response = client.post(
        "/tasks",
        json={
            "title": "",
            "description": "Invalid title",
            "priority": "medium",
        },
    )

    assert response.status_code == 422


def test_create_task_with_invalid_priority_returns_validation_error(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Study",
            "description": "Invalid priority",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422


def test_list_tasks_returns_created_tasks(client):
    create_task(client, title="First")
    create_task(client, title="Second", priority="high")

    response = client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "First"
    assert data[1]["title"] == "Second"


def test_list_tasks_returns_empty_list_when_no_tasks_exist(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_get_task_by_id_returns_task(client):
    created = create_task(client).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_task_by_unknown_id_returns_not_found(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_complete_task_updates_status(client):
    created = create_task(client).json()

    response = client.patch(f"/tasks/{created['id']}/complete")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_complete_unknown_task_returns_not_found(client):
    response = client.patch("/tasks/999/complete")

    assert response.status_code == 404


def test_delete_task_removes_task(client):
    created = create_task(client).json()

    delete_response = client.delete(f"/tasks/{created['id']}")
    get_response = client.get(f"/tasks/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_unknown_task_returns_not_found(client):
    response = client.delete("/tasks/999")

    assert response.status_code == 404


def test_task_stats_counts_pending_and_completed_tasks(client):
    first = create_task(client).json()
    create_task(client, title="Second")
    client.patch(f"/tasks/{first['id']}/complete")

    response = client.get("/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 2,
        "completed_tasks": 1,
        "pending_tasks": 1,
    }
