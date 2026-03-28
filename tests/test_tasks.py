"""Tests for task CRUD endpoints with mocked Supabase."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock the Supabase client."""
    with patch("app.services.task_orchestrator.get_supabase_client") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


def _mock_table_chain(mock_client, table_name, data, count=None):
    """Helper to set up a mock Supabase table query chain."""
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Support chained calls: .select().eq().order().range().execute()
    mock_chain = MagicMock()
    mock_table.select.return_value = mock_chain
    mock_table.insert.return_value = mock_chain
    mock_table.update.return_value = mock_chain

    mock_chain.eq.return_value = mock_chain
    mock_chain.order.return_value = mock_chain
    mock_chain.range.return_value = mock_chain
    mock_chain.limit.return_value = mock_chain

    mock_result = MagicMock()
    mock_result.data = data
    mock_result.count = count
    mock_chain.execute.return_value = mock_result

    return mock_table


class TestListTasks:
    def test_list_tasks_returns_200(self, client, mock_supabase):
        _mock_table_chain(mock_supabase, "tasks", [])
        response = client.get("/tasks/")
        assert response.status_code == 200

    def test_list_tasks_returns_data(self, client, mock_supabase):
        task_data = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Test task",
                "status": "draft",
            }
        ]
        _mock_table_chain(mock_supabase, "tasks", task_data)
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test task"


class TestCreateTask:
    def test_create_task_returns_201(self, client, mock_supabase):
        created = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "New task",
            "status": "draft",
        }
        _mock_table_chain(mock_supabase, "tasks", [created])
        response = client.post("/tasks/", json={"title": "New task"})
        assert response.status_code == 201

    def test_create_task_with_priority(self, client, mock_supabase):
        created = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Urgent task",
            "priority": "high",
            "status": "draft",
        }
        _mock_table_chain(mock_supabase, "tasks", [created])
        response = client.post("/tasks/", json={"title": "Urgent task", "priority": "high"})
        assert response.status_code == 201
        assert response.json()["priority"] == "high"


class TestGetTask:
    def test_get_task_found(self, client, mock_supabase):
        task = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Found task",
            "status": "draft",
        }
        _mock_table_chain(mock_supabase, "tasks", [task])
        response = client.get("/tasks/550e8400-e29b-41d4-a716-446655440000")
        assert response.status_code == 200
        assert response.json()["title"] == "Found task"

    def test_get_task_not_found(self, client, mock_supabase):
        _mock_table_chain(mock_supabase, "tasks", [])
        response = client.get("/tasks/550e8400-e29b-41d4-a716-446655440000")
        assert response.status_code == 404


class TestUpdateTask:
    def test_update_task_returns_updated(self, client, mock_supabase):
        updated = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Updated title",
            "status": "draft",
        }
        _mock_table_chain(mock_supabase, "tasks", [updated])
        response = client.patch(
            "/tasks/550e8400-e29b-41d4-a716-446655440000",
            json={"title": "Updated title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated title"

    def test_update_task_empty_body(self, client, mock_supabase):
        response = client.patch("/tasks/550e8400-e29b-41d4-a716-446655440000", json={})
        assert response.status_code == 400


class TestDeleteTask:
    def test_delete_task_returns_archived(self, client, mock_supabase):
        archived = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "archived",
        }
        _mock_table_chain(mock_supabase, "tasks", [archived])
        response = client.delete("/tasks/550e8400-e29b-41d4-a716-446655440000")
        assert response.status_code == 200
        assert response.json()["status"] == "archived"
