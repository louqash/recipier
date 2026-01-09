"""
Shared pytest fixtures for Recipier tests.
"""

import json
import os
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from recipier.config import TaskConfig
from recipier.localization import Localizer

# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_meals_database() -> Dict[str, Any]:
    """Sample meals database for testing."""
    return {
        "meals": [
            {
                "meal_id": "test_spaghetti",
                "name": "Test Spaghetti Carbonara",
                "base_servings": {"high_calorie": 1.67, "low_calorie": 1.0},
                "ingredients": [
                    {"name": "spaghetti", "quantity": 100, "unit": "g", "category": "pantry"},
                    {"name": "bacon", "quantity": 50, "unit": "g", "category": "meat"},
                    {"name": "eggs", "quantity": 2, "unit": "pcs", "category": "dairy"},
                ],
                "prep_tasks": [],
            },
            {
                "meal_id": "test_salad",
                "name": "Test Caesar Salad",
                "base_servings": {"high_calorie": 1.5, "low_calorie": 1.0},
                "ingredients": [
                    {"name": "lettuce", "quantity": 100, "unit": "g", "category": "produce"},
                    {"name": "chicken breast", "quantity": 80, "unit": "g", "category": "meat"},
                ],
                "prep_tasks": [{"description": "Wash and chop lettuce", "days_before": 1}],
            },
        ],
        "ingredient_details": {
            "spaghetti": {"calories_per_100g": 371, "unit_size": None, "adjustable": True},
            "bacon": {"calories_per_100g": 541, "unit_size": None, "adjustable": True},
            "eggs": {"calories_per_100g": 155, "unit_size": None, "adjustable": True},
            "lettuce": {"calories_per_100g": 15, "unit_size": None, "adjustable": True},
            "chicken breast": {"calories_per_100g": 165, "unit_size": None, "adjustable": True},
        },
    }


@pytest.fixture
def sample_meal_plan() -> Dict[str, Any]:
    """Sample meal plan for testing."""
    return {
        "scheduled_meals": [
            {
                "id": "sm_1704067200000",
                "meal_id": "test_spaghetti",
                "cooking_dates": ["2026-01-06"],
                "eating_dates_per_person": {
                    "John": ["2026-01-06", "2026-01-07"],
                    "Jane": ["2026-01-06"],
                },
                "meal_type": "dinner",
                "assigned_cook": "John",
            },
            {
                "id": "sm_1704153600000",
                "meal_id": "test_salad",
                "cooking_dates": ["2026-01-07", "2026-01-08"],
                "eating_dates_per_person": {
                    "John": ["2026-01-07", "2026-01-08"],
                    "Jane": ["2026-01-07", "2026-01-08"],
                },
                "meal_type": "dinner",
                "assigned_cook": "Jane",
            },
        ],
        "shopping_trips": [
            {
                "shopping_date": "2026-01-05",
                "scheduled_meal_ids": ["sm_1704067200000", "sm_1704153600000"],
            }
        ],
    }


@pytest.fixture
def sample_config() -> TaskConfig:
    """Sample configuration for testing."""
    return TaskConfig(
        shopping_categories=[
            "produce",
            "meat",
            "dairy",
            "pantry",
            "frozen",
            "bakery",
            "beverages",
            "spices",
            "other",
        ],
        use_emojis=True,
        use_category_labels=True,
        ingredient_format="{quantity}{unit} {name}",
        shopping_priority=2,
        prep_priority=2,
        cooking_priority=3,
        eating_priority=3,
        project_name="Test Meal Planning",
        user_mapping={"John": "John Doe", "Jane": "Jane Doe"},
        diet_profiles={"John": "high_calorie", "Jane": "low_calorie"},
        use_sections=True,
        shopping_section_name="Shopping",
        prep_section_name="Prep",
        cooking_section_name="Cooking",
        eating_section_name="Serving",
        language="english",
    )


@pytest.fixture
def temp_meals_database(tmp_path, sample_meals_database):
    """Create temporary meals database file."""
    db_path = tmp_path / "test_meals_database.json"
    with open(db_path, "w") as f:
        json.dump(sample_meals_database, f)
    return db_path


@pytest.fixture
def temp_meal_plan(tmp_path, sample_meal_plan):
    """Create temporary meal plan file."""
    plan_path = tmp_path / "test_meal_plan.json"
    with open(plan_path, "w") as f:
        json.dump(sample_meal_plan, f)
    return plan_path


@pytest.fixture
def temp_config(tmp_path, sample_config):
    """Create temporary config file."""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(sample_config.__dict__, f)
    return config_path


# ============================================================================
# Component Fixtures
# ============================================================================


@pytest.fixture
def localizer_english() -> Localizer:
    """English localizer instance."""
    return Localizer(language="english")


@pytest.fixture
def localizer_polish() -> Localizer:
    """Polish localizer instance."""
    return Localizer(language="polish")


@pytest.fixture
def mock_todoist_adapter(mocker):
    """Mock TodoistAdapter for testing."""
    mock_adapter = mocker.patch("recipier.todoist_adapter.TodoistAdapter")
    mock_instance = mock_adapter.return_value

    # Mock create_tasks to return list of task IDs
    mock_instance.create_tasks.return_value = ["task_1", "task_2", "task_3"]

    # Mock get_or_create_project
    mock_instance.get_or_create_project.return_value = "project_123"

    return mock_adapter


# ============================================================================
# API Test Fixtures
# ============================================================================


@pytest.fixture
def api_client(tmp_path, sample_meals_database, monkeypatch):
    """FastAPI test client with test database."""
    # Create test meals database
    db_path = tmp_path / "meals_database.json"
    with open(db_path, "w") as f:
        json.dump(sample_meals_database, f)

    # Clear any cached imports
    import sys

    for module in list(sys.modules.keys()):
        if module.startswith("backend"):
            del sys.modules[module]

    # Override the MEALS_DB_PATH before importing
    monkeypatch.setattr("backend.routers.meals.MEALS_DB_PATH", str(db_path))

    # Import and create test client
    from backend.main import app

    client = TestClient(app)

    yield client


@pytest.fixture
def mock_env_token(monkeypatch):
    """Mock TODOIST_API_TOKEN environment variable."""
    monkeypatch.setenv("TODOIST_API_TOKEN", "test_token_123")
