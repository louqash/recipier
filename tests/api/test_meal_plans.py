"""
API tests for meal plan endpoints.
"""

import pytest


@pytest.mark.api
class TestMealPlansAPI:
    """Tests for /api/meal-plan endpoints."""

    def test_validate_meal_plan_with_no_eating_dates(self, api_client):
        """Test validation error when no eating dates provided."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10"],
                    "eating_dates_per_person": {},  # Empty - no one eating
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/meal-plan/validate", json=invalid_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_meal_plan_with_empty_person_dates(self, api_client):
        """Test validation error when person has empty eating dates list."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10"],
                    "eating_dates_per_person": {"John": []},  # Empty list
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/meal-plan/validate", json=invalid_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_meal_plan_with_different_eating_dates_per_person(self, api_client):
        """Test that different people can have different eating dates (all must be in cooking dates)."""
        valid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10", "2026-01-12", "2026-01-14"],  # 3 cooking dates
                    "eating_dates_per_person": {
                        "John": ["2026-01-10", "2026-01-12"],  # Eats 2 days
                        "Jane": ["2026-01-14"],  # Eats 1 day
                    },
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/meal-plan/validate", json=valid_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["errors"]) == 0

    def test_validate_meal_plan_with_eating_date_not_in_cooking(self, api_client):
        """Test validation error when eating date is not in cooking dates."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10", "2026-01-12"],  # 2 cooking dates
                    "eating_dates_per_person": {
                        "John": [
                            "2026-01-10",
                            "2026-01-11",  # Not in cooking dates!
                            "2026-01-12",
                        ]
                    },
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
            "language": "english",  # Request English errors for easier testing
        }

        response = api_client.post("/api/meal-plan/validate", json=invalid_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        # Check that error mentions eating date not in cooking dates
        assert "2026-01-11" in str(data["errors"])
        assert "not in cooking dates" in str(data["errors"])

    def test_validate_meal_plan_with_meal_prep(self, api_client):
        """Test validation passes for meal prep (1 cooking date, multiple eating dates on future days)."""
        valid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10"],  # Cook once
                    "eating_dates_per_person": {
                        "John": ["2026-01-10", "2026-01-11", "2026-01-12"],  # Eat over 3 days
                        "Jane": ["2026-01-10", "2026-01-11"],  # Eat over 2 days
                    },
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/meal-plan/validate", json=valid_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["errors"]) == 0

    def test_validate_meal_plan_with_meal_prep_eating_before_cooking(self, api_client):
        """Test validation error for meal prep when eating date is before cooking date."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10"],  # Cook on 10th
                    "eating_dates_per_person": {
                        "John": ["2026-01-09", "2026-01-10", "2026-01-11"],  # Eating on 9th (before cooking!)
                    },
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
            "language": "english",  # Request English errors for easier testing
        }

        response = api_client.post("/api/meal-plan/validate", json=invalid_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        # Check that error mentions eating before cooking
        assert "2026-01-09" in str(data["errors"])
        assert "before cooking date" in str(data["errors"])
