"""
Core meal planning logic - independent of any task management system.
Can be used by CLI, MCP server, or web interface.
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from recipier.config import TaskConfig
from recipier.localization import get_localizer, Localizer


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
        self.config: TaskConfig = config or TaskConfig()
        self.config.validate()  # Ensure config is valid
        self.loc: Localizer = get_localizer(self.config.language)

    def load_meals_database(self, file_path: str) -> Dict[str, Any]:
        """Load meals database JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        if 'meals' not in data:
            raise ValueError("Meals database must contain 'meals' key")

        return data

    def load_meal_plan(self, plan_path: str, meals_db_path: str) -> Dict[str, Any]:
        """Load meal plan and expand with meals database."""
        # Load meal plan
        with open(plan_path, 'r') as f:
            meal_plan = json.load(f)

        if 'scheduled_meals' not in meal_plan or 'shopping_trips' not in meal_plan:
            raise ValueError("Meal plan must contain 'scheduled_meals' and 'shopping_trips'")

        # Load meals database
        meals_db = self.load_meals_database(meals_db_path)

        # Expand and return
        return self.expand_meal_plan(meal_plan, meals_db)

    def expand_meal_plan(self, meal_plan: Dict[str, Any], meals_db: Dict[str, Any]) -> Dict[str, Any]:
        """Expand meal plan by merging with meals database."""
        # Create lookup for meals database
        meals_lookup = {meal['meal_id']: meal for meal in meals_db['meals']}

        expanded_meals = []

        for scheduled in meal_plan['scheduled_meals']:
            meal_id = scheduled['meal_id']

            if meal_id not in meals_lookup:
                raise ValueError(f"Meal '{meal_id}' not found in database")

            recipe = meals_lookup[meal_id]
            servings = scheduled['servings_per_person']

            # Calculate ingredients based on servings
            total_ingredients = []
            for base_ing in recipe['ingredients']:
                # Calculate per person and total
                total_qty = 0
                per_person_data = {}

                for person, num_servings in servings.items():
                    if num_servings > 0:
                        # Map user to diet profile (fallback to user name for backward compatibility)
                        diet_profile = self.config.diet_profiles.get(person, person)

                        # Check for ingredient-level override first, then fall back to meal-level base_servings
                        if 'base_servings_override' in base_ing and diet_profile in base_ing['base_servings_override']:
                            base_serving_size = base_ing['base_servings_override'][diet_profile]
                        else:
                            base_serving_size = recipe.get('base_servings', {}).get(diet_profile, 1.0)
                        person_qty = round(base_ing['quantity'] * base_serving_size * num_servings)
                        total_qty += person_qty
                        per_person_data[person] = {
                            'quantity': person_qty,
                            'unit': base_ing['unit'],
                            'portions': num_servings
                        }

                ingredient = {
                    'name': base_ing['name'],
                    'quantity': round(total_qty),
                    'unit': base_ing['unit'],
                    'category': base_ing['category'],
                    'per_person': per_person_data
                }

                if 'notes' in base_ing:
                    ingredient['notes'] = base_ing['notes']

                total_ingredients.append(ingredient)

            # Build expanded meal
            expanded_meal = {
                'id': scheduled['id'],  # Unique instance ID
                'meal_id': meal_id,
                'name': recipe['name'],
                'cooking_dates': scheduled['cooking_dates'],
                'meal_type': scheduled['meal_type'],
                'assigned_cook': scheduled['assigned_cook'],
                'ingredients': total_ingredients
            }

            if 'notes' in recipe:
                expanded_meal['notes'] = recipe['notes']

            # Handle prep tasks
            if 'prep_tasks' in recipe:
                prep_tasks = []
                for prep in recipe['prep_tasks']:
                    prep_task = prep.copy()
                    prep_task['assigned_to'] = scheduled.get('prep_assigned_to', scheduled['assigned_cook'])
                    prep_tasks.append(prep_task)
                expanded_meal['prep_tasks'] = prep_tasks

            expanded_meals.append(expanded_meal)

        return {
            'meals': expanded_meals,
            'shopping_trips': meal_plan['shopping_trips']
        }

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
                        ingredient_lines.append(f"- {quantity}{unit} {ing['name']}")

            # Create subtask for this person
            if ingredient_lines:
                description = '\n'.join(ingredient_lines)
                subtask = Task(
                    title=self.loc.t("portion_for_person", person=person),
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
        # Build lookup by scheduled meal instance ID
        meals_by_id = {meal['id']: meal for meal in meal_plan['meals']}

        for trip in meal_plan['shopping_trips']:
            # Collect ingredients and meal names with counts
            all_ingredients = []
            meal_name_counts = {}  # meal_name -> total count (instances + cooking dates)

            for scheduled_meal_id in trip['scheduled_meal_ids']:
                if scheduled_meal_id in meals_by_id:
                    meal = meals_by_id[scheduled_meal_id]
                    meal_name = meal['name']

                    # Count cooking sessions (number of cooking dates)
                    num_cooking_sessions = len(meal.get('cooking_dates', []))

                    # Add to count (each scheduled meal contributes its cooking sessions)
                    meal_name_counts[meal_name] = meal_name_counts.get(meal_name, 0) + num_cooking_sessions
                    all_ingredients.extend(meal['ingredients'])

            # Format meal names with multipliers (x2, x3, etc.)
            formatted_meals = []
            for meal_name, count in meal_name_counts.items():
                if count > 1:
                    formatted_meals.append(f"{meal_name} x{count}")
                else:
                    formatted_meals.append(meal_name)

            # Create task title
            emoji = "🛒 " if self.config.use_emojis else ""
            task_title = self.loc.t("shopping_task_title", emoji=emoji, meals=', '.join(formatted_meals))

            # Simple description
            description = self.loc.t("shopping_task_description")

            # Create subtasks ordered by category
            subtasks = self.create_ingredient_subtasks(all_ingredients)

            task = Task(
                title=task_title,
                description=description,
                due_date=trip['shopping_date'],
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
            # Get and sort cooking dates
            cooking_dates = sorted(meal.get('cooking_dates', []))
            if not cooking_dates:
                continue

            # Create prep tasks for each cooking session
            for cooking_date_str in cooking_dates:
                cooking_date = datetime.strptime(cooking_date_str, '%Y-%m-%d')

                for prep in meal['prep_tasks']:
                    emoji = "🥘 " if self.config.use_emojis else ""
                    task_title = self.loc.t("prep_task_title", emoji=emoji, meal=meal_name)

                    # Calculate prep date
                    prep_date = cooking_date - timedelta(days=prep['days_before'])
                    prep_date_str = prep_date.strftime('%Y-%m-%d')

                    assigned_to = prep['assigned_to']
                    description = self.loc.t("prep_task_description", description=prep['description'], date=cooking_date_str)

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

    def divide_ingredients(self, ingredients: List[Dict[str, Any]], divisor: int) -> List[Dict[str, Any]]:
        """Divide ingredient quantities by divisor for multiple cooking sessions."""
        divided = []
        for ing in ingredients:
            ing_copy = ing.copy()
            if 'per_person' in ing_copy:
                per_person_copy = {}
                for person, data in ing_copy['per_person'].items():
                    per_person_copy[person] = {
                        'quantity': round(data['quantity'] / divisor),
                        'unit': data['unit'],
                        'portions': data.get('portions', 1) / divisor
                    }
                ing_copy['per_person'] = per_person_copy
            divided.append(ing_copy)
        return divided

    def create_cooking_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate cooking tasks from meal plan."""
        tasks = []

        for meal in meal_plan['meals']:
            # Get and sort cooking dates
            cooking_dates = sorted(meal.get('cooking_dates', []))
            num_cooking_sessions = len(cooking_dates)
            is_meal_prep = num_cooking_sessions == 1

            # Extract portions info from ingredients (once, outside loop)
            portions_by_person = {}
            for ing in meal['ingredients']:
                if 'per_person' in ing:
                    for person, data in ing['per_person'].items():
                        if 'portions' in data:
                            if person not in portions_by_person:
                                portions_by_person[person] = data['portions']

            # Validate: for multiple cooking sessions, portions should match number of dates
            if not is_meal_prep:
                for person, total_portions in portions_by_person.items():
                    assert total_portions == num_cooking_sessions, \
                        f"Meal '{meal['name']}': {person} has {total_portions} portions but {num_cooking_sessions} cooking dates. These must match."

            # Create a cooking task for each date
            for idx, cooking_date in enumerate(cooking_dates):
                emoji = "👨‍🍳 " if self.config.use_emojis else ""
                task_title = self.loc.t("cooking_task_title", emoji=emoji, meal=meal['name'])
                if not is_meal_prep:
                    task_title += f" ({cooking_date})"

                # Build description
                meal_type_translated = self.loc.get_meal_type_translation(meal['meal_type'])
                description_lines = [
                    self.loc.t("cooking_task_description_line1", meal_type=meal_type_translated, date=cooking_date),
                ]

                # Add portions info
                if portions_by_person:
                    portions_info = []
                    for person in sorted(portions_by_person.keys()):
                        total_portions = portions_by_person[person]
                        portions_this_session = total_portions if is_meal_prep else 1
                        portion_word = self.loc.t("portion_singular") if portions_this_session == 1 else self.loc.t("portion_plural")
                        portions_info.append(f"{person}: {portions_this_session} {portion_word}")
                    description_lines.append(self.loc.t("cooking_task_description_portions", portions=', '.join(portions_info)))

                if not is_meal_prep:
                    description_lines.append(self.loc.t("cooking_task_description_session", current=idx + 1, total=num_cooking_sessions))

                if meal.get('notes'):
                    description_lines.append(f"\n{meal['notes']}")

                description = '\n'.join(description_lines)

                # Create per-person portion subtasks with adjusted quantities
                if is_meal_prep:
                    subtasks = self.create_person_portion_subtasks(meal['ingredients'])
                else:
                    adjusted_ingredients = self.divide_ingredients(meal['ingredients'], num_cooking_sessions)
                    subtasks = self.create_person_portion_subtasks(adjusted_ingredients)

                task = Task(
                    title=task_title,
                    description=description,
                    due_date=cooking_date,
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
