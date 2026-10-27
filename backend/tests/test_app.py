from datetime import datetime, timezone
from unittest.mock import MagicMock

import app as flask_app

import pytest


@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True

    with flask_app.app.test_client() as test_client:
        yield test_client


def make_task(task_id=1, title="Test task", completed=False):
    """Create a sample database task row."""
    return (
        task_id,
        title,
        completed,
        datetime.now(timezone.utc),
    )


def setup_database_mock(monkeypatch, fetchone=None, fetchall=None):
    """Mock the PostgreSQL connection and cursor."""
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    cursor.__enter__.return_value = cursor

    connection.cursor.return_value = cursor
    cursor.__enter__.return_value = cursor

    cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall or []

    monkeypatch.setattr(
        flask_app,
        "get_db_connection",
        lambda: connection,
    )

    return cursor


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"CloudTasks" in response.data


def test_health_check_success(client, monkeypatch):
    setup_database_mock(monkeypatch)

    response = client.get("/health")

    assert response.status_code == 200


def test_get_tasks(client, monkeypatch):
    setup_database_mock(
        monkeypatch,
        fetchall=[
            make_task(1, "Learn Docker"),
            make_task(2, "Learn Kubernetes", True),
        ],
    )

    response = client.get("/api/tasks")

    assert response.status_code == 200

    tasks = response.get_json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Learn Docker"
    assert tasks[1]["completed"] is True


def test_create_task(client, monkeypatch):
    setup_database_mock(
        monkeypatch,
        fetchone=make_task(1, "Build CloudTasks"),
    )

    response = client.post(
        "/api/tasks",
        json={"title": "Build CloudTasks"},
    )

    assert response.status_code == 201
    assert response.get_json()["title"] == "Build CloudTasks"


def test_create_task_without_title(client):
    response = client.post(
        "/api/tasks",
        json={"title": "   "},
    )

    assert response.status_code == 400


def test_update_task(client, monkeypatch):
    setup_database_mock(
        monkeypatch,
        fetchone=make_task(1, "Test task", True),
    )

    response = client.patch(
        "/api/tasks/1",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.get_json()["completed"] is True


def test_update_nonexistent_task(client, monkeypatch):
    setup_database_mock(monkeypatch, fetchone=None)

    response = client.patch(
        "/api/tasks/999",
        json={"completed": True},
    )

    assert response.status_code == 404


def test_delete_task(client, monkeypatch):
    cursor = setup_database_mock(
        monkeypatch,
        fetchone=(1,),
    )

    response = client.delete("/api/tasks/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Task deleted"


def test_delete_nonexistent_task(client, monkeypatch):
    setup_database_mock(monkeypatch, fetchone=None)

    response = client.delete("/api/tasks/999")

    assert response.status_code == 404
