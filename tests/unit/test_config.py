"""
Unit tests for configuration module.
"""

import json

import pytest

from recipier.config import TaskConfig


@pytest.mark.unit
class TestTaskConfig:
    """Tests for TaskConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TaskConfig()

        assert config.use_emojis is True
        assert config.language == "polish"
        assert config.project_name == "Meal Planning"
        assert config.shopping_priority == 2
        assert config.prep_priority == 2
        assert config.cooking_priority == 3
        assert len(config.shopping_categories) == 8

    def test_custom_config(self):
        """Test custom configuration."""
        config = TaskConfig(use_emojis=False, language="english", project_name="Custom Project", shopping_priority=1)

        assert config.use_emojis is False
        assert config.language == "english"
        assert config.project_name == "Custom Project"
        assert config.shopping_priority == 1

    def test_user_mapping(self):
        """Test user mapping configuration."""
        config = TaskConfig(
            user_mapping={"John": "john_todoist", "Jane": "jane_todoist"},
            diet_profiles={"John": "high_calorie", "Jane": "low_calorie"},
        )

        assert "John" in config.user_mapping
        assert config.user_mapping["John"] == "john_todoist"
        assert config.diet_profiles["John"] == "high_calorie"

    def test_validate_success(self):
        """Test successful validation."""
        config = TaskConfig(user_mapping={"John": "john_todoist"}, diet_profiles={"John": "high_calorie"})

        # Should not raise
        config.validate()

    def test_validate_missing_diet_profile(self):
        """Test validation fails when user missing diet profile."""
        config = TaskConfig(
            user_mapping={"John": "john_todoist", "Jane": "jane_todoist"},
            diet_profiles={"John": "high_calorie"},  # Missing Jane
        )

        with pytest.raises(ValueError, match="Missing diet profiles for: Jane"):
            config.validate()

    def test_from_file(self, tmp_path):
        """Test loading configuration from file."""
        config_data = {
            "use_emojis": False,
            "language": "english",
            "project_name": "File Project",
            "user_mapping": {"Alice": "alice_todoist"},
            "diet_profiles": {"Alice": "low_calorie"},
        }

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = TaskConfig.from_file(str(config_path))

        assert config.use_emojis is False
        assert config.language == "english"
        assert config.project_name == "File Project"
        assert config.user_mapping["Alice"] == "alice_todoist"

    def test_from_file_nonexistent(self):
        """Test loading from non-existent file returns defaults."""
        config = TaskConfig.from_file("nonexistent.json")

        # Should return default config
        assert config.use_emojis is True
        assert config.language == "polish"

    def test_to_file(self, tmp_path):
        """Test saving configuration to file."""
        config = TaskConfig(use_emojis=False, language="english", project_name="Save Test")

        config_path = tmp_path / "saved_config.json"
        config.to_file(str(config_path))

        # Load and verify
        with open(config_path, "r") as f:
            data = json.load(f)

        assert data["use_emojis"] is False
        assert data["language"] == "english"
        assert data["project_name"] == "Save Test"

    def test_shopping_categories_order(self):
        """Test shopping categories maintain order."""
        config = TaskConfig()

        expected_order = [
            "produce",
            "meat",
            "dairy",
            "pantry",
            "frozen",
            "bakery",
            "beverages",
            "other",
        ]
        assert config.shopping_categories == expected_order

    def test_section_names(self):
        """Test section name configuration."""
        config = TaskConfig(
            shopping_section_name="Zakupy",
            prep_section_name="Przygotowania",
            cooking_section_name="Gotowanie",
            eating_section_name="Podawanie",
        )

        assert config.shopping_section_name == "Zakupy"
        assert config.prep_section_name == "Przygotowania"
        assert config.cooking_section_name == "Gotowanie"
        assert config.eating_section_name == "Podawanie"
