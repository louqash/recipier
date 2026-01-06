"""
API tests for task generation endpoints.
"""

import pytest


@pytest.mark.api
class TestTasksAPI:
    """Tests for /api/tasks endpoints."""

    def test_generate_tasks_success(self, api_client, sample_meal_plan, mock_env_token, mocker):
        """Test POST /api/tasks/generate successfully creates tasks."""
        # Mock the TodoistAdapter where it's imported in tasks router
        mock_adapter = mocker.patch("backend.routers.tasks.TodoistAdapter")
        mock_instance = mock_adapter.return_value
        mock_instance.create_tasks.return_value = []  # Returns list of created tasks

        response = api_client.post("/api/tasks/generate", json={"meal_plan": sample_meal_plan, "todoist_token": "env"})

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["tasks_created"] == 7  # 1 shopping + 2 prep + 3 cooking + 1 eating
        assert "message" in data

    def test_generate_tasks_with_custom_token(self, api_client, sample_meal_plan, mocker):
        """Test generating tasks with custom token."""
        mock_adapter = mocker.patch("backend.routers.tasks.TodoistAdapter")
        mock_instance = mock_adapter.return_value
        mock_instance.create_tasks.return_value = []  # Returns list of created tasks

        response = api_client.post(
            "/api/tasks/generate",
            json={"meal_plan": sample_meal_plan, "todoist_token": "custom_token_123"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_generate_tasks_missing_token(self, api_client, sample_meal_plan, monkeypatch):
        """Test generating tasks without token fails."""
        # Remove env token
        monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)

        response = api_client.post("/api/tasks/generate", json={"meal_plan": sample_meal_plan, "todoist_token": ""})

        assert response.status_code == 400
        data = response.json()
        assert "token" in data["detail"].lower()

    def test_generate_tasks_invalid_meal_plan(self, api_client, mock_env_token):
        """Test generating tasks with invalid meal plan."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "nonexistent_meal",
                    "cooking_dates": ["2026-01-06"],
                    "eating_dates_per_person": {},  # Invalid: empty
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/tasks/generate", json={"meal_plan": invalid_plan, "todoist_token": "env"})

        # Should return error about validation or missing meal
        assert response.status_code in [400, 404, 422]

    def test_generate_tasks_validation_error(self, api_client, mock_env_token, mocker):
        """Test generating tasks with invalid meal plan (eating before cooking)."""
        # Mock TodoistAdapter (won't be called due to validation error)
        mock_adapter = mocker.patch("backend.routers.tasks.TodoistAdapter")
        mock_instance = mock_adapter.return_value
        mock_instance.create_tasks.return_value = []

        # Eating date before cooking date
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10"],
                    "eating_dates_per_person": {"John": ["2026-01-05"]},  # Before cooking!
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/tasks/generate", json={"meal_plan": invalid_plan, "todoist_token": "env"})

        # Should fail validation
        assert response.status_code == 422
        data = response.json()
        assert "validation_errors" in data["detail"]

    def test_config_status_with_env_token(self, api_client, mock_env_token):
        """Test GET /api/config/status with environment token."""
        response = api_client.get("/api/config/status")

        assert response.status_code == 200
        data = response.json()

        assert data["has_env_token"] is True

    def test_config_status_without_env_token(self, api_client, monkeypatch):
        """Test GET /api/config/status without environment token."""
        monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)

        response = api_client.get("/api/config/status")

        assert response.status_code == 200
        data = response.json()

        assert data["has_env_token"] is False

    def test_get_users_config(self, api_client, tmp_path):
        """Test GET /api/config/users returns user configuration."""
        # Create config file
        import json

        config_data = {
            "user_mapping": {"John": "john_todoist", "Jane": "jane_todoist"},
            "diet_profiles": {"John": "high_calorie", "Jane": "low_calorie"},
        }

        config_path = tmp_path / "my_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # This test assumes the API looks for my_config.json in cwd
        # In real scenario, you'd need to set up the path properly

        response = api_client.get("/api/config/users")

        assert response.status_code == 200
        data = response.json()

        assert "users" in data
        assert "diet_profiles" in data

    def test_generate_tasks_with_custom_config(self, api_client, sample_meal_plan, mock_env_token, mocker):
        """Test task generation with custom config in request."""
        mock_adapter = mocker.patch("backend.routers.tasks.TodoistAdapter")
        mock_instance = mock_adapter.return_value
        mock_instance.create_tasks.return_value = []

        custom_config = {
            "project_name": "Custom Project",
            "use_emojis": False,
            "language": "english",
        }

        response = api_client.post(
            "/api/tasks/generate",
            json={"meal_plan": sample_meal_plan, "todoist_token": "env", "config": custom_config},
        )

        assert response.status_code == 200
        # Verify custom config was used
        call_args = mock_adapter.call_args
        assert call_args[0][1].project_name == "Custom Project"

    def test_generate_tasks_with_no_config_file(
        self, api_client, sample_meal_plan, mock_env_token, mocker, tmp_path, monkeypatch
    ):
        """Test task generation when no config file exists (uses defaults)."""
        mock_adapter = mocker.patch("backend.routers.tasks.TodoistAdapter")
        mock_instance = mock_adapter.return_value
        mock_instance.create_tasks.return_value = []

        # Change to directory without config file
        monkeypatch.chdir(tmp_path)

        response = api_client.post("/api/tasks/generate", json={"meal_plan": sample_meal_plan, "todoist_token": "env"})

        assert response.status_code == 200
        # Should use default config
        call_args = mock_adapter.call_args
        assert call_args[0][1] is not None

    def test_generate_tasks_meals_db_not_found(self, api_client, sample_meal_plan, mock_env_token, mocker, monkeypatch):
        """Test error when meals database doesn't exist."""
        import sys

        # Clear cached imports
        for module in list(sys.modules.keys()):
            if module.startswith("backend.routers.tasks"):
                del sys.modules[module]

        monkeypatch.setattr("backend.routers.tasks.MEALS_DB_PATH", "/nonexistent/meals.json")

        from fastapi.testclient import TestClient

        from backend.main import app

        client = TestClient(app)

        response = client.post(
            "/api/tasks/generate",
            json={"meal_plan": sample_meal_plan, "todoist_token": "test_token"},
        )

        assert response.status_code == 500
        assert "not found" in response.json()["detail"].lower()
