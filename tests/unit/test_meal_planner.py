"""
Unit tests for meal planner module.
"""

import pytest

from recipier.meal_planner import MealPlanner, Task


@pytest.mark.unit
class TestMealPlanner:
    """Tests for MealPlanner class."""

    def test_initialization(self, sample_config, sample_meals_database):
        """Test MealPlanner initialization."""
        planner = MealPlanner(sample_config, sample_meals_database)

        assert planner.config == sample_config
        assert planner.meals_db == sample_meals_database
        assert planner.ingredient_calories == sample_meals_database["ingredient_calories"]

    def test_load_meal_plan(self, temp_meals_database, temp_meal_plan, sample_config):
        """Test loading and expanding meal plan from files."""
        planner = MealPlanner(sample_config)
        expanded = planner.load_meal_plan(str(temp_meal_plan), str(temp_meals_database))

        assert "meals" in expanded
        assert "shopping_trips" in expanded
        assert len(expanded["meals"]) == 2

    def test_expand_meal_plan_quantity_calculation(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test ingredient quantity calculations."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        # First meal: Spaghetti
        # John: 2 eating dates, high_calorie (1.67x)
        # Jane: 1 eating date, low_calorie (1.0x)
        meal = expanded["meals"][0]
        spaghetti_ingredient = next(i for i in meal["ingredients"] if i["name"] == "spaghetti")

        # Total quantity should be:
        # John: 100g × 1.67 × 2 = 334g
        # Jane: 100g × 1.0 × 1 = 100g
        # Total: 434g
        assert spaghetti_ingredient["quantity"] == pytest.approx(434, abs=1)

    def test_calculate_meal_calories(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test calorie calculation for meals."""
        planner = MealPlanner(sample_config, sample_meals_database)

        # Expand meal plan to get per_person data
        expanded = planner.expand_meal_plan(sample_meal_plan)
        expanded_meal = expanded["meals"][0]  # Spaghetti with per_person breakdown

        # Calculate calories (uses self.ingredient_calories)
        calories = planner.calculate_meal_calories(expanded_meal)

        assert "high_calorie" in calories
        assert "low_calorie" in calories
        assert calories["high_calorie"] > calories["low_calorie"]

    def test_create_shopping_tasks(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test shopping task generation."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_shopping_tasks(expanded)

        assert len(tasks) == 1  # One shopping trip
        task = tasks[0]

        assert task.task_type == "shopping"
        assert task.due_date == "2026-01-05"
        assert len(task.subtasks) > 0  # Should have ingredient subtasks

    def test_create_cooking_tasks(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test cooking task generation."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_cooking_tasks(expanded)

        # First meal has 1 cooking date, second has 2
        assert len(tasks) == 3

        # Check first cooking task
        task = tasks[0]
        assert task.task_type == "cooking"
        assert task.assigned_to == "John"
        assert "dinner" in task.description.lower()

    def test_create_eating_tasks(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test eating/serving task generation."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_eating_tasks(expanded)

        # First meal: John eats on 2026-01-07 (not cooking date)
        # Second meal: All eating dates are cooking dates
        assert len(tasks) >= 1

        # Check that eating tasks are only for non-cooking dates
        for task in tasks:
            assert task.task_type == "eating"

    def test_create_prep_tasks(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test prep task generation."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_prep_tasks(expanded)

        # Second meal (salad) has prep tasks
        assert len(tasks) > 0

        task = tasks[0]
        assert task.task_type == "prep"
        assert "lettuce" in task.description.lower() or "chop" in task.description.lower()

    def test_generate_all_tasks(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test generating all task types."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        all_tasks = planner.generate_all_tasks(expanded)

        # Should have shopping, prep, cooking, and eating tasks
        task_types = {task.task_type for task in all_tasks}
        assert "shopping" in task_types
        assert "cooking" in task_types

        # Verify total count
        assert len(all_tasks) > 0

    def test_per_person_ingredient_breakdown(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test per-person ingredient breakdown."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        meal = expanded["meals"][0]
        spaghetti = next(i for i in meal["ingredients"] if i["name"] == "spaghetti")

        assert "per_person" in spaghetti
        assert "John" in spaghetti["per_person"]
        assert "Jane" in spaghetti["per_person"]

        # John should have more than Jane (2 portions vs 1)
        john_qty = spaghetti["per_person"]["John"]["quantity"]
        jane_qty = spaghetti["per_person"]["Jane"]["quantity"]
        assert john_qty > jane_qty

    def test_ingredient_category_grouping(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test ingredients are grouped by category."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_shopping_tasks(expanded)
        task = tasks[0]

        # Subtasks should maintain category order
        categories_in_order = []
        for subtask in task.subtasks:
            if subtask.labels:
                categories_in_order.append(subtask.labels[0])

        # Check that categories follow config order
        config_categories = sample_config.shopping_categories
        for i in range(len(categories_in_order) - 1):
            cat1_idx = config_categories.index(categories_in_order[i])
            cat2_idx = config_categories.index(categories_in_order[i + 1])
            assert cat1_idx <= cat2_idx

    def test_meal_prep_vs_separate_cooking(self, sample_meals_database, sample_config):
        """Test meal prep (1 cooking date) vs separate cooking (multiple dates)."""
        planner = MealPlanner(sample_config, sample_meals_database)

        # Meal prep: 1 cooking date, multiple eating dates
        meal_prep_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06"],
                    "eating_dates_per_person": {"John": ["2026-01-06", "2026-01-07", "2026-01-08"]},
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        expanded = planner.expand_meal_plan(meal_prep_plan)
        cooking_tasks = planner.create_cooking_tasks(expanded)

        assert len(cooking_tasks) == 1  # Only 1 cooking task

        # Separate cooking: multiple cooking dates
        separate_plan = {
            "scheduled_meals": [
                {
                    "id": "sm_2",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06", "2026-01-07", "2026-01-08"],
                    "eating_dates_per_person": {"John": ["2026-01-06", "2026-01-07", "2026-01-08"]},
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        expanded2 = planner.expand_meal_plan(separate_plan)
        cooking_tasks2 = planner.create_cooking_tasks(expanded2)

        assert len(cooking_tasks2) == 3  # 3 cooking tasks

    def test_shopping_task_title_localized(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test shopping task title uses localization."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_shopping_tasks(expanded)
        task = tasks[0]

        # Should use localized title format (Polish or English depending on config)
        assert "Zakupy na:" in task.title or "Shopping for:" in task.title
        # Should include meal names
        assert any(meal_name in task.title for meal_name in ["Spaghetti", "Salad", "Caesar"])

    def test_shopping_task_diet_breakdown(self, sample_meals_database, sample_meal_plan, sample_config):
        """Test shopping task shows diet breakdown instead of total portions."""
        planner = MealPlanner(sample_config, sample_meals_database)
        expanded = planner.expand_meal_plan(sample_meal_plan)

        tasks = planner.create_shopping_tasks(expanded)
        task = tasks[0]

        # Description should show diet breakdown format like "• Meal: 2 high_calorie, 1 low_calorie"
        # Should NOT show total count format like "• Meal x3"
        assert "high_calorie" in task.description or "low_calorie" in task.description
        # Should not have the old "x2" or "x3" format
        assert " x2" not in task.description and " x3" not in task.description

    def test_cooking_task_eating_today_note(self, sample_meals_database, sample_config):
        """Test cooking task shows 'eating today' note when someone eats on cooking day."""
        planner = MealPlanner(sample_config, sample_meals_database)

        # Person eats on cooking day
        plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06"],
                    "eating_dates_per_person": {"John": ["2026-01-06", "2026-01-07"]},  # Eats on cooking day
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        expanded = planner.expand_meal_plan(plan)
        tasks = planner.create_cooking_tasks(expanded)
        task = tasks[0]

        # Should have "eating today" note
        assert "Jedzenie dzisiaj:" in task.description or "Eating today:" in task.description
        assert "John" in task.description

    def test_cooking_task_meal_prep_note(self, sample_meals_database, sample_config):
        """Test cooking task shows meal prep note when nobody eats on cooking day."""
        planner = MealPlanner(sample_config, sample_meals_database)

        # Nobody eats on cooking day (meal prep scenario)
        plan = {
            "scheduled_meals": [
                {
                    "id": "sm_1",
                    "meal_id": "test_spaghetti",
                    "cooking_dates": ["2026-01-06"],
                    "eating_dates_per_person": {"John": ["2026-01-07", "2026-01-08"]},  # Eats AFTER cooking day
                    "meal_type": "dinner",
                    "assigned_cook": "John",
                }
            ],
            "shopping_trips": [],
        }

        expanded = planner.expand_meal_plan(plan)
        tasks = planner.create_cooking_tasks(expanded)
        task = tasks[0]

        # Should have meal prep note
        assert ("Meal prep" in task.description and "podanie w innych dniach" in task.description) or (
            "Meal prep" in task.description and "serving on other days" in task.description
        )


@pytest.mark.unit
class TestTaskDataclass:
    """Tests for Task dataclass."""

    def test_task_creation(self):
        """Test creating a Task instance."""
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date="2026-01-06",
            priority=2,
            assigned_to="John",
            meal_id="test_meal",
            task_type="shopping",
        )

        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.due_date == "2026-01-06"
        assert task.priority == 2
        assert task.assigned_to == "John"
        assert task.task_type == "shopping"

    def test_task_with_subtasks(self):
        """Test Task with subtasks."""
        subtask1 = Task(
            title="Subtask 1",
            description="",
            due_date="",
            priority=3,
            assigned_to="",
            meal_id="",
            task_type="shopping",
        )

        subtask2 = Task(
            title="Subtask 2",
            description="",
            due_date="",
            priority=3,
            assigned_to="",
            meal_id="",
            task_type="shopping",
        )

        parent_task = Task(
            title="Parent Task",
            description="Parent Description",
            due_date="2026-01-06",
            priority=2,
            assigned_to="John",
            meal_id="test_meal",
            task_type="shopping",
            subtasks=[subtask1, subtask2],
        )

        assert len(parent_task.subtasks) == 2
        assert parent_task.subtasks[0].title == "Subtask 1"
        assert parent_task.subtasks[1].title == "Subtask 2"

    def test_task_with_labels(self):
        """Test Task with labels."""
        task = Task(
            title="Test Task",
            description="",
            due_date="2026-01-06",
            priority=2,
            assigned_to="John",
            meal_id="test_meal",
            task_type="shopping",
            labels=["produce", "urgent"],
        )

        assert len(task.labels) == 2
        assert "produce" in task.labels
        assert "urgent" in task.labels
