"""
Integration tests for end-to-end workflows.
"""

import json

import pytest


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests."""

    def test_full_meal_plan_to_tasks_workflow(
        self, tmp_path, sample_meals_database, sample_meal_plan, sample_config, mocker
    ):
        """Test complete workflow from meal plan to Todoist tasks."""
        # Clear cached recipier modules to ensure clean imports
        import sys

        for module in list(sys.modules.keys()):
            if module.startswith("recipier"):
                del sys.modules[module]

        # Setup: Create temporary files
        meals_db_path = tmp_path / "meals.json"
        meal_plan_path = tmp_path / "plan.json"
        config_path = tmp_path / "config.json"

        with open(meals_db_path, "w") as f:
            json.dump(sample_meals_database, f)

        with open(meal_plan_path, "w") as f:
            json.dump(sample_meal_plan, f)

        with open(config_path, "w") as f:
            json.dump(sample_config.model_dump(), f)

        # Mock Todoist API
        mock_api = mocker.patch("todoist_api_python.api.TodoistAPI")
        mock_instance = mock_api.return_value

        # Create mock objects with attributes (not dicts)
        from unittest.mock import MagicMock

        mock_project = MagicMock()
        mock_project.id = "project_123"
        mock_project.name = "Test Meal Planning"

        mock_sections = []
        for section_id, section_name in [
            ("section_shopping", "Shopping"),
            ("section_prep", "Prep"),
            ("section_cooking", "Cooking"),
            ("section_serving", "Serving"),
        ]:
            mock_section = MagicMock()
            mock_section.id = section_id
            mock_section.name = section_name
            mock_section.project_id = "project_123"
            mock_sections.append(mock_section)

        mock_task = MagicMock()
        mock_task.id = "task_123"

        # Mock API methods
        mock_instance.get_projects.return_value = [mock_project]
        mock_instance.get_sections.return_value = mock_sections
        mock_instance.add_task.return_value = mock_task
        mock_instance.add_project.return_value = mock_project

        # Execute: Load and process meal plan
        from recipier.config import TaskConfig
        from recipier.meal_planner import MealPlanner
        from recipier.todoist_adapter import TodoistAdapter

        config = TaskConfig.from_file(str(config_path))

        with open(meals_db_path, "r") as f:
            meals_db = json.load(f)

        with open(meal_plan_path, "r") as f:
            meal_plan = json.load(f)

        # Create planner and generate tasks
        planner = MealPlanner(config, meals_db)
        # generate_all_tasks handles expansion internally
        tasks = planner.generate_all_tasks(meal_plan)

        # Verify: Tasks were generated
        assert len(tasks) > 0

        # Verify: Task types
        task_types = {task.task_type for task in tasks}
        assert "shopping" in task_types
        assert "cooking" in task_types

        # Execute: Create tasks in Todoist
        adapter = TodoistAdapter("fake_token", config)
        adapter.create_tasks(tasks)

        # Verify: Todoist API was called
        assert mock_instance.add_task.called
        assert mock_instance.add_task.call_count >= len(tasks)

    def test_meal_plan_validation_workflow(self, api_client, sample_meal_plan):
        """Test meal plan validation workflow."""
        # Valid plan
        response = api_client.post("/api/meal-plan/validate", json=sample_meal_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["errors"]) == 0

        # Invalid plan - eating before cooking
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

        response = api_client.post("/api/meal-plan/validate", json=invalid_plan)

        # Should still return 200 but with errors
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_quantity_calculation_workflow(self, sample_meals_database, sample_config):
        """Test ingredient quantity calculation workflow."""
        from recipier.meal_planner import MealPlanner

        # Create meal plan with specific quantities
        meal_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06"],
                    "eating_dates_per_person": {
                        "John": ["2026-01-06", "2026-01-07"],  # 2 portions
                        "Jane": ["2026-01-06"],  # 1 portion
                    },
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(meal_plan)

        # Verify calculations
        meal = expanded["meals"][0]
        spaghetti = next(i for i in meal["ingredients"] if i["name"] == "spaghetti")

        # John: 100g × 1.67 × 2 = 334g
        john_qty = spaghetti["per_person"]["John"]["quantity"]
        assert john_qty == pytest.approx(334, abs=1)

        # Jane: 100g × 1.0 × 1 = 100g
        jane_qty = spaghetti["per_person"]["Jane"]["quantity"]
        assert jane_qty == pytest.approx(100, abs=1)

        # Total should be sum
        assert spaghetti["quantity"] == pytest.approx(434, abs=1)

    def test_multi_cooking_date_workflow(self, sample_meals_database, sample_config):
        """Test workflow with multiple cooking dates."""
        from recipier.meal_planner import MealPlanner

        meal_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06", "2026-01-08", "2026-01-10"],
                    "eating_dates_per_person": {"John": ["2026-01-06", "2026-01-08", "2026-01-10"]},
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(meal_plan)

        # Should create 3 cooking tasks
        cooking_tasks = planner.create_cooking_tasks(expanded)
        assert len(cooking_tasks) == 3

        # Each should have session information
        for i, task in enumerate(cooking_tasks, 1):
            assert f"session {i} of 3" in task.description.lower() or f"sesja {i} z 3" in task.description.lower()

    def test_shopping_trip_with_multiple_meals(self, sample_meals_database, sample_config):
        """Test shopping trip combining multiple meals."""
        from recipier.meal_planner import MealPlanner

        meal_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06"],
                    "eating_dates_per_person": {"John": ["2026-01-06"]},
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                },
                {
                    "id": "sm_2",
                    "meal_id": "test_salad",
                    "cooking_dates": ["2026-01-07"],
                    "eating_dates_per_person": {"John": ["2026-01-07"]},
                    "meal_type": "lunch",
                    "assigned_cook": "John",
                },
            ],
            "shopping_trips": [{"shopping_date": "2026-01-05", "scheduled_meal_ids": ["sm_1", "sm_2"]}],
        }

        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(meal_plan)

        shopping_tasks = planner.create_shopping_tasks(expanded)

        assert len(shopping_tasks) == 1
        task = shopping_tasks[0]

        # Should combine ingredients from both meals
        subtask_names = [st.title for st in task.subtasks]

        # Check for ingredients from both meals
        assert any("spaghetti" in name.lower() for name in subtask_names)
        assert any("lettuce" in name.lower() for name in subtask_names)
