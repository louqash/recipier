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

    def test_validate_meal_plan_with_non_divisible_portions(self, api_client):
        """Test validation error when eating dates not divisible by cooking sessions."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10", "2026-01-12"],  # 2 cooking dates
                    "eating_dates_per_person": {
                        "John": [
                            "2026-01-10",
                            "2026-01-11",
                            "2026-01-12",
                        ]  # 3 eating dates (not divisible by 2)
                    },
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

    def test_save_meal_plan_with_invalid_dates(self, api_client):
        """Test saving meal plan with invalid dates fails validation."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-10"],
                    "eating_dates_per_person": {"John": ["2026-01-05"]},  # Before cooking
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/meal-plan/save", json=invalid_plan)

        assert response.status_code == 400
        data = response.json()
        assert "validation failed" in data["detail"]["message"].lower()

    def test_save_meal_plan_with_no_cooking_dates(self, api_client):
        """Test saving meal plan with no cooking dates."""
        invalid_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": [],  # No cooking dates
                    "eating_dates_per_person": {"John": ["2026-01-10"]},
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        response = api_client.post("/api/meal-plan/save", json=invalid_plan)

        assert response.status_code == 400
        assert "no cooking dates" in response.json()["detail"].lower()

    def test_load_meal_plan_not_found(self, api_client):
        """Test loading non-existent meal plan."""
        response = api_client.get("/api/meal-plan/load/2099-12-31")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
