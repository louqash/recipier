"""
API tests for meals endpoints.
"""

import pytest


@pytest.mark.api
class TestMealsAPI:
    """Tests for /api/meals endpoints."""

    def test_get_all_meals(self, api_client):
        """Test GET /api/meals returns all meals."""
        response = api_client.get("/api/meals")

        assert response.status_code == 200
        data = response.json()

        assert "meals" in data
        assert isinstance(data["meals"], list)
        assert len(data["meals"]) == 2  # From sample database

    def test_get_meals_with_search(self, api_client):
        """Test GET /api/meals with search parameter."""
        response = api_client.get("/api/meals?search=spaghetti")

        assert response.status_code == 200
        data = response.json()

        assert len(data["meals"]) >= 1
        # Check that spaghetti is in the results
        meal_names = [m["name"].lower() for m in data["meals"]]
        assert any("spaghetti" in name for name in meal_names)

    def test_get_meals_search_case_insensitive(self, api_client):
        """Test search is case-insensitive."""
        response1 = api_client.get("/api/meals?search=SPAGHETTI")
        response2 = api_client.get("/api/meals?search=spaghetti")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Should return same results
        assert len(data1["meals"]) == len(data2["meals"])

    def test_get_meals_no_match(self, api_client):
        """Test search with no matching meals."""
        response = api_client.get("/api/meals?search=nonexistent_meal_xyz")

        assert response.status_code == 200
        data = response.json()

        assert len(data["meals"]) == 0

    def test_get_specific_meal(self, api_client):
        """Test GET /api/meals/{meal_id}."""
        response = api_client.get("/api/meals/test_spaghetti")

        assert response.status_code == 200
        data = response.json()

        assert data["meal_id"] == "test_spaghetti"
        assert data["name"] == "Test Spaghetti Carbonara"
        assert "ingredients" in data
        assert "base_servings" in data

    def test_get_nonexistent_meal(self, api_client):
        """Test GET /api/meals/{meal_id} for non-existent meal."""
        response = api_client.get("/api/meals/nonexistent_meal")

        assert response.status_code == 404

    def test_get_meal_calories(self, api_client):
        """Test GET /api/meals/ingredient-details."""
        response = api_client.get("/api/meals/ingredient-details")

        assert response.status_code == 200
        data = response.json()

        assert "ingredient_details" in data
        assert isinstance(data["ingredient_details"], dict)
        assert "spaghetti" in data["ingredient_details"]
        assert data["ingredient_details"]["spaghetti"]["calories_per_100g"] == 371

    def test_meals_have_required_fields(self, api_client):
        """Test that meals have all required fields."""
        response = api_client.get("/api/meals")
        data = response.json()

        for meal in data["meals"]:
            assert "meal_id" in meal
            assert "name" in meal
            assert "ingredients" in meal
            assert "base_servings" in meal
            assert isinstance(meal["ingredients"], list)
            assert isinstance(meal["base_servings"], dict)

    def test_ingredients_have_required_fields(self, api_client):
        """Test that ingredients have all required fields."""
        response = api_client.get("/api/meals/test_spaghetti")
        meal = response.json()

        for ingredient in meal["ingredients"]:
            assert "name" in ingredient
            assert "quantity" in ingredient
            assert "unit" in ingredient
            assert "category" in ingredient

    def test_base_servings_structure(self, api_client):
        """Test base_servings have correct structure."""
        response = api_client.get("/api/meals/test_spaghetti")
        meal = response.json()

        base_servings = meal["base_servings"]
        assert "high_calorie" in base_servings
        assert "low_calorie" in base_servings
        assert isinstance(base_servings["high_calorie"], (int, float))
        assert isinstance(base_servings["low_calorie"], (int, float))

    def test_get_meals_database_not_found(self, api_client, monkeypatch):
        """Test error when meals database file doesn't exist."""
        import sys

        # Clear cached imports
        for module in list(sys.modules.keys()):
            if module.startswith("backend"):
                del sys.modules[module]

        monkeypatch.setattr("backend.routers.meals.MEALS_DB_PATH", "/nonexistent/path.json")

        from fastapi.testclient import TestClient

        from backend.main import app

        client = TestClient(app)

        response = client.get("/api/meals/")

        assert response.status_code == 500
        assert "not found" in response.json()["detail"].lower()

    def test_get_meals_invalid_json(self, api_client, tmp_path, monkeypatch):
        """Test error when meals database has invalid JSON."""
        import sys

        # Clear cached imports
        for module in list(sys.modules.keys()):
            if module.startswith("backend"):
                del sys.modules[module]

        # Create invalid JSON file
        invalid_db = tmp_path / "invalid.json"
        with open(invalid_db, "w") as f:
            f.write("{invalid json")

        monkeypatch.setattr("backend.routers.meals.MEALS_DB_PATH", str(invalid_db))

        from fastapi.testclient import TestClient

        from backend.main import app

        client = TestClient(app)

        response = client.get("/api/meals/")

        assert response.status_code == 500
        assert "parsing" in response.json()["detail"].lower()

    def test_get_ingredient_calories_missing(self, api_client, tmp_path, monkeypatch):
        """Test error when ingredient_details not in database."""
        import json
        import sys

        # Clear cached imports
        for module in list(sys.modules.keys()):
            if module.startswith("backend"):
                del sys.modules[module]

        # Create database without ingredient_details
        db_path = tmp_path / "no_details.json"
        with open(db_path, "w") as f:
            json.dump({"meals": []}, f)

        monkeypatch.setattr("backend.routers.meals.MEALS_DB_PATH", str(db_path))

        from fastapi.testclient import TestClient

        from backend.main import app

        client = TestClient(app)

        response = client.get("/api/meals/ingredient-details")

        assert response.status_code == 500
        assert "ingredient_details not found" in response.json()["detail"]
