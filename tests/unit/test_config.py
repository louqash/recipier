"""
Unit tests for configuration module.
"""

import json

import pytest

from recipier.config import TaskConfig, TodoistConfig


@pytest.mark.unit
class TestTaskConfig:
    """Tests for TaskConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TaskConfig()

        assert config.use_emojis is True
        assert config.language == "polish"
        assert config.todoist.project_name == "Meal Planning"
        assert config.shopping_priority == 2
        assert config.prep_priority == 2
        assert config.cooking_priority == 3
        assert len(config.shopping_categories) == 9

    def test_custom_config(self):
        """Test custom configuration."""
        config = TaskConfig(
            use_emojis=False,
            language="english",
            todoist=TodoistConfig(project_name="Custom Project"),
            shopping_priority=1,
        )

        assert config.use_emojis is False
        assert config.language == "english"
        assert config.todoist.project_name == "Custom Project"
        assert config.shopping_priority == 1

    def test_user_mapping(self):
        """Test user mapping configuration."""
        config = TaskConfig(
            todoist=TodoistConfig(user_mapping={"John": "john_todoist", "Jane": "jane_todoist"}),
            diet_profiles={"John": "high_calorie", "Jane": "low_calorie"},
        )

        assert "John" in config.todoist.user_mapping
        assert config.todoist.user_mapping["John"] == "john_todoist"
        assert config.diet_profiles["John"] == "high_calorie"

    def test_validate_success(self):
        """Test successful validation."""
        # Should not raise when user mapping matches diet profiles
        config = TaskConfig(
            todoist=TodoistConfig(user_mapping={"John": "john_todoist"}), diet_profiles={"John": "high_calorie"}
        )

        # If we got here without exception, validation passed
        assert config is not None

    def test_validate_missing_diet_profile(self):
        """Test validation fails when user missing todoist mapping."""
        # This should fail because Jane has diet profile but no todoist mapping
        with pytest.raises(ValueError, match="Missing Todoist mappings for: Jane"):
            TaskConfig(
                todoist=TodoistConfig(user_mapping={"John": "john_todoist"}),
                diet_profiles={"John": "high_calorie", "Jane": "low_calorie"},
            )

    def test_from_file(self, tmp_path):
        """Test loading configuration from file."""
        config_data = {
            "use_emojis": False,
            "language": "english",
            "todoist": {"project_name": "File Project", "user_mapping": {"Alice": "alice_todoist"}},
            "diet_profiles": {"Alice": "low_calorie"},
        }

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = TaskConfig.from_file(str(config_path))

        assert config.use_emojis is False
        assert config.language == "english"
        assert config.todoist.project_name == "File Project"
        assert config.todoist.user_mapping["Alice"] == "alice_todoist"

    def test_from_file_nonexistent(self):
        """Test loading from non-existent file returns defaults."""
        config = TaskConfig.from_file("nonexistent.json")

        # Should return default config
        assert config.use_emojis is True
        assert config.language == "polish"

    def test_to_file(self, tmp_path):
        """Test saving configuration to file."""
        config = TaskConfig(use_emojis=False, language="english", todoist=TodoistConfig(project_name="Save Test"))

        config_path = tmp_path / "saved_config.json"
        config.to_file(str(config_path))

        # Load and verify
        with open(config_path, "r") as f:
            data = json.load(f)

        assert data["use_emojis"] is False
        assert data["language"] == "english"
        assert data["todoist"]["project_name"] == "Save Test"

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
            "spices",
            "other",
        ]
        assert config.shopping_categories == expected_order

    def test_todoist_config_defaults(self):
        """Test Todoist-specific configuration defaults."""
        config = TaskConfig()

        # Check todoist defaults
        assert config.todoist.project_name == "Meal Planning"
        assert config.todoist.use_sections is True
        assert config.todoist.user_mapping == {}
        assert config.todoist.shopping_labels == []
        assert config.todoist.prep_labels == []
        assert config.todoist.cooking_labels == []
        assert config.todoist.eating_labels == []
