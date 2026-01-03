"""
Core meal planning logic - independent of any task management system.
Can be used by CLI, MCP server, or web interface.
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from config import TaskConfig


@dataclass
class Task:
    """Represents a task to be created."""
    title: str
    description: str
    priority: int
    assigned_to: str
    due_date: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)
    meal_id: Optional[str] = None
    task_type: str = "other"  # shopping, prep, cooking


class MealPlanner:
    """Core meal planning logic."""

    def __init__(self, config: TaskConfig = None):
        """Initialize with optional configuration."""
        self.config = config or TaskConfig()

    def load_meal_plan(self, file_path: str) -> Dict[str, Any]:
        """Load and validate meal plan JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        if 'meals' not in data or 'shopping_trips' not in data:
            raise ValueError("JSON must contain 'meals' and 'shopping_trips' keys")

        return data

    def parse_meal_plan(self, data: str | Dict[str, Any]) -> Dict[str, Any]:
        """Parse meal plan from JSON string or dict."""
        if isinstance(data, str):
            data = json.loads(data)

        if 'meals' not in data or 'shopping_trips' not in data:
            raise ValueError("JSON must contain 'meals' and 'shopping_trips' keys")

        return data

    def format_ingredient_title(self, ingredient: Dict[str, Any]) -> str:
        """Format ingredient title (with notes if present)."""
        title = self.config.ingredient_format.format(
            quantity=ingredient['quantity'],
            unit=ingredient['unit'],
            name=ingredient['name']
        )

        # Add notes to title if present
        if ingredient.get('notes'):
            title += f" ({ingredient['notes']})"

        return title

    def group_ingredients_by_category(self, ingredients: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group ingredients by category in configured order."""
        by_category = defaultdict(list)

        for ing in ingredients:
            category = ing.get('category', 'other')
            by_category[category].append(ing)

        return by_category

    def create_ingredient_subtasks(self, ingredients: List[Dict[str, Any]]) -> List[Task]:
        """Create subtasks for ingredients, ordered by category."""
        subtasks = []
        by_category = self.group_ingredients_by_category(ingredients)

        # Process in category order
        for category in self.config.shopping_categories:
            if category not in by_category:
                continue

            # Sort ingredients within category by name
            sorted_ingredients = sorted(by_category[category], key=lambda x: x['name'])

            for ing in sorted_ingredients:
                title = self.format_ingredient_title(ing)
                labels = [category] if self.config.use_category_labels else []

                subtask = Task(
                    title=title,
                    description='',  # Notes are in the title
                    priority=4,  # Low priority for subtasks
                    assigned_to='',  # Inherited from parent
                    labels=labels
                )
                subtasks.append(subtask)

        return subtasks

    def create_person_portion_subtasks(self, ingredients: List[Dict[str, Any]]) -> List[Task]:
        """Create per-person portion subtasks for cooking tasks."""
        subtasks = []

        # Determine which people have portions (from per_person data)
        people_with_portions = set()
        for ing in ingredients:
            if 'per_person' in ing:
                people_with_portions.update(ing['per_person'].keys())

        # Only create subtasks for people who have portions
        for person in sorted(people_with_portions):  # Sort for consistent order
            # Build ingredient list for this person
            ingredient_lines = []
            by_category = self.group_ingredients_by_category(ingredients)

            for category in self.config.shopping_categories:
                if category not in by_category:
                    continue

                sorted_ingredients = sorted(by_category[category], key=lambda x: x['name'])

                for ing in sorted_ingredients:
                    # Check if there's a per_person breakdown
                    if 'per_person' in ing and person in ing['per_person']:
                        person_portion = ing['per_person'][person]
                        quantity = person_portion['quantity']
                        unit = person_portion['unit']
                        ingredient_lines.append(f"- [ ] {quantity}{unit} {ing['name']}")

            # Create subtask for this person
            if ingredient_lines:
                description = '\n'.join(ingredient_lines)
                subtask = Task(
                    title=f"Portion for {person}",
                    description=description,
                    priority=4,
                    assigned_to='',
                    labels=[]
                )
                subtasks.append(subtask)

        return subtasks

    def create_shopping_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate shopping tasks from meal plan."""
        tasks = []
        meals_by_id = {meal['meal_id']: meal for meal in meal_plan['meals']}

        for trip in meal_plan['shopping_trips']:
            # Collect ingredients and meal names
            all_ingredients = []
            meal_names = []

            for meal_id in trip['meal_ids']:
                if meal_id in meals_by_id:
                    meal = meals_by_id[meal_id]
                    meal_names.append(meal['name'])
                    all_ingredients.extend(meal['ingredients'])

            # Create task title
            emoji = "🛒 " if self.config.use_emojis else ""
            task_title = f"{emoji}Shopping for: {', '.join(meal_names)}"

            # Simple description
            description = "Shopping list"

            # Create subtasks ordered by category
            subtasks = self.create_ingredient_subtasks(all_ingredients)

            task = Task(
                title=task_title,
                description=description,
                due_date=trip['date'],
                priority=self.config.shopping_priority,
                assigned_to='',  # No assignment - can be set manually in Todoist
                subtasks=subtasks,
                task_type="shopping"
            )
            tasks.append(task)

        return tasks

    def create_prep_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate prep tasks from meal plan."""
        tasks = []

        for meal in meal_plan['meals']:
            if 'prep_tasks' not in meal or not meal['prep_tasks']:
                continue

            meal_name = meal['name']
            meal_date = datetime.strptime(meal['date'], '%Y-%m-%d')

            for prep in meal['prep_tasks']:
                emoji = "🥘 " if self.config.use_emojis else ""
                task_title = f"{emoji}Prep for {meal_name}: {prep['description']}"

                # Calculate due date
                prep_date = meal_date - timedelta(days=prep['days_before'])
                prep_date_str = prep_date.strftime('%Y-%m-%d')

                assigned_to = prep['assigned_to']
                description = f"Preparation for {meal_name}\nCooking date: {meal['date']}\nAssigned to: {assigned_to}"

                task = Task(
                    title=task_title,
                    description=description,
                    due_date=prep_date_str,
                    priority=self.config.prep_priority,
                    assigned_to=assigned_to,
                    meal_id=meal['meal_id'],
                    task_type="prep"
                )
                tasks.append(task)

        return tasks

    def create_cooking_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate cooking tasks from meal plan."""
        tasks = []

        for meal in meal_plan['meals']:
            emoji = "👨‍🍳 " if self.config.use_emojis else ""
            task_title = f"{emoji}Cook: {meal['name']}"

            # Build description
            description_lines = [
                f"**{meal['meal_type'].capitalize()}** for {meal['date']}",
                f"Assigned to: {meal['assigned_cook']}",
            ]

            # Extract portions info from ingredients
            portions_by_person = {}
            for ing in meal['ingredients']:
                if 'per_person' in ing:
                    for person, data in ing['per_person'].items():
                        if 'portions' in data:
                            # Take the first portions value we find for each person
                            if person not in portions_by_person:
                                portions_by_person[person] = data['portions']

            if portions_by_person:
                portions_info = []
                for person in sorted(portions_by_person.keys()):
                    count = portions_by_person[person]
                    portions_info.append(f"{person}: {count} portion{'s' if count > 1 else ''}")
                description_lines.append(f"Portions: {', '.join(portions_info)}")

            if meal.get('notes'):
                description_lines.append(f"\n{meal['notes']}")

            description = '\n'.join(description_lines)

            # Create per-person portion subtasks
            subtasks = self.create_person_portion_subtasks(meal['ingredients'])

            task = Task(
                title=task_title,
                description=description,
                due_date=meal['date'],
                priority=self.config.cooking_priority,
                assigned_to=meal['assigned_cook'],
                subtasks=subtasks,
                meal_id=meal['meal_id'],
                task_type="cooking"
            )
            tasks.append(task)

        return tasks

    def generate_all_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate all tasks from a meal plan."""
        tasks = []
        tasks.extend(self.create_shopping_tasks(meal_plan))
        tasks.extend(self.create_prep_tasks(meal_plan))
        tasks.extend(self.create_cooking_tasks(meal_plan))
        return tasks
