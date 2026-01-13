"""
API tests for config endpoints.
"""

import os

import pytest


@pytest.mark.api
class TestConfigAPI:
    """Tests for /api/config endpoints."""

    def test_config_status_with_env_token(self, api_client, mock_env_token):
        """Test config status with environment token set."""
        response = api_client.get("/api/config/status")

        assert response.status_code == 200
        data = response.json()
        assert data["has_env_token"] is True

    def test_config_status_without_env_token(self, api_client, monkeypatch):
        """Test config status without environment token."""
        monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)

        response = api_client.get("/api/config/status")

        assert response.status_code == 200
        data = response.json()
        assert data["has_env_token"] is False

    def test_get_users_with_config_file(self, api_client, tmp_path, monkeypatch):
        """Test getting users when config file exists."""
        import json

        # Create config file
        config_data = {
            "todoist": {"user_mapping": {"John": "john_todoist", "Jane": "jane_todoist"}},
            "diet_profiles": {"John": "high_calorie", "Jane": "low_calorie"},
        }

        config_path = tmp_path / "my_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Change working directory to tmp_path
        monkeypatch.chdir(tmp_path)

        response = api_client.get("/api/config/users")

        assert response.status_code == 200
        data = response.json()
        # API returns only diet_profiles, users are keys of diet_profiles
        assert set(data["diet_profiles"].keys()) == {"John", "Jane"}
        assert data["diet_profiles"]["John"] == "high_calorie"
        assert data["diet_profiles"]["Jane"] == "low_calorie"

    def test_get_users_without_config_file(self, api_client, tmp_path, monkeypatch):
        """Test getting users when config file doesn't exist."""
        # Create a fresh empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Change to empty directory (no config file here)
        monkeypatch.chdir(empty_dir)

        # Clear the config cache so it reloads from new directory
        from backend.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        response = api_client.get("/api/config/users")

        assert response.status_code == 200
        data = response.json()
        # API returns empty diet_profiles dict when config doesn't exist
        assert data["diet_profiles"] == {}

    def test_get_users_with_invalid_config_file(self, api_client, tmp_path, monkeypatch):
        """Test getting users when config file is invalid JSON."""
        # Create a fresh directory with invalid config
        invalid_dir = tmp_path / "invalid"
        invalid_dir.mkdir()

        # Create invalid JSON file
        config_path = invalid_dir / "my_config.json"
        with open(config_path, "w") as f:
            f.write("{invalid json")

        monkeypatch.chdir(invalid_dir)

        # Clear the config cache so it reloads from new directory
        from backend.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        response = api_client.get("/api/config/users")

        assert response.status_code == 200
        data = response.json()
        # Should return empty dict on error
        assert data["diet_profiles"] == {}
