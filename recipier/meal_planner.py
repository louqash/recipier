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

    def __init__(self, config: TaskConfig = None, meals_db: Dict[str, Any] = None):
        """Initialize with optional configuration and meals database."""
        self.config: TaskConfig = config or TaskConfig()
        self.config.validate()  # Ensure config is valid
        self.loc: Localizer = get_localizer(self.config.language)
        self.meals_db: Dict[str, Any] = meals_db or {}
        self.ingredient_calories: Dict[str, float] = meals_db.get('ingredient_calories', {}) if meals_db else {}

    def load_meals_database(self, file_path: str) -> Dict[str, Any]:
        """Load meals database JSON file and store it."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        if 'meals' not in data:
            raise ValueError("Meals database must contain 'meals' key")

        # Store the database and extract calories
        self.meals_db = data
        self.ingredient_calories = data.get('ingredient_calories', {})

        return data

    def load_meal_plan(self, plan_path: str, meals_db_path: str) -> Dict[str, Any]:
        """Load meal plan and expand with meals database."""
        # Load meal plan
        with open(plan_path, 'r') as f:
            meal_plan = json.load(f)

        if 'scheduled_meals' not in meal_plan or 'shopping_trips' not in meal_plan:
            raise ValueError("Meal plan must contain 'scheduled_meals' and 'shopping_trips'")

        # Load meals database (stores in self.meals_db)
        self.load_meals_database(meals_db_path)

        # Expand and return
        return self.expand_meal_plan(meal_plan)

    def expand_meal_plan(self, meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Expand meal plan by merging with stored meals database."""
        if not self.meals_db or 'meals' not in self.meals_db:
            raise ValueError("Meals database not loaded. Call load_meals_database() or pass meals_db to __init__()")

        # Create lookup for meals database
        meals_lookup = {meal['meal_id']: meal for meal in self.meals_db['meals']}

        expanded_meals = []

        for scheduled in meal_plan['scheduled_meals']:
            meal_id = scheduled['meal_id']

            if meal_id not in meals_lookup:
                raise ValueError(f"Meal '{meal_id}' not found in database")

            recipe = meals_lookup[meal_id]
            # Convert eating dates to servings (number of eating dates = number of portions)
            eating_dates = scheduled['eating_dates_per_person']
            servings = {person: len(dates) for person, dates in eating_dates.items()}

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
                'eating_dates_per_person': scheduled['eating_dates_per_person'],
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

    def calculate_meal_calories(self, meal: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate total calories for a meal for all diet profiles.

        Args:
            meal: Expanded meal object with ingredients containing per_person data

        Returns:
            Dictionary with profile names as keys and calorie counts as values
            e.g., {"high_calorie": 2850, "low_calorie": 1700}
        """
        if not meal or 'ingredients' not in meal or not self.ingredient_calories:
            return {}

        # Collect all people from per_person data and map to diet profiles
        people = set()
        for ing in meal['ingredients']:
            if 'per_person' in ing:
                people.update(ing['per_person'].keys())

        if not people:
            return {}

        # Map people to their diet profiles
        profile_totals = {}
        for person in people:
            profile = self.config.diet_profiles.get(person, person)
            if profile not in profile_totals:
                profile_totals[profile] = 0.0

        # Calculate calories for each ingredient
        for ing in meal['ingredients']:
            ingredient_name = ing['name']
            calories_per_100g = self.ingredient_calories.get(ingredient_name, 0)

            if 'per_person' not in ing:
                continue

            # Add calories for each person (mapped to their profile)
            for person in people:
                if person in ing['per_person']:
                    profile = self.config.diet_profiles.get(person, person)
                    quantity = ing['per_person'][person]['quantity']
                    # Calculate calories: (quantity / 100) * calories_per_100g
                    calories = (quantity / 100.0) * calories_per_100g
                    profile_totals[profile] += calories

        # Round all totals to integers
        return {profile: round(total) for profile, total in profile_totals.items()}

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
            # Collect ingredients and meal info
            all_ingredients = []
            meal_name_counts = {}  # meal_name -> {diet_profile: count}
            all_eating_dates = []  # Collect all eating dates for date range

            for scheduled_meal_id in trip['scheduled_meal_ids']:
                if scheduled_meal_id in meals_by_id:
                    meal = meals_by_id[scheduled_meal_id]
                    meal_name = meal['name']

                    # Count portions by diet type
                    if meal_name not in meal_name_counts:
                        meal_name_counts[meal_name] = {}

                    eating_dates_per_person = meal.get('eating_dates_per_person', {})
                    for person, eating_dates in eating_dates_per_person.items():
                        # Map person to their diet profile
                        diet_profile = self.config.diet_profiles.get(person, person)
                        portions = len(eating_dates)
                        meal_name_counts[meal_name][diet_profile] = meal_name_counts[meal_name].get(diet_profile, 0) + portions
                        all_eating_dates.extend(eating_dates)

                    all_ingredients.extend(meal['ingredients'])

            # Calculate eating date range
            date_range_str = ""
            if all_eating_dates:
                sorted_dates = sorted(all_eating_dates)
                first_date = sorted_dates[0]
                last_date = sorted_dates[-1]
                if first_date == last_date:
                    date_range_str = f" ({first_date})"
                else:
                    date_range_str = f" ({first_date} - {last_date})"

            # Create task title with localization
            emoji = "🛒 " if self.config.use_emojis else ""
            # Build meals string for title
            meals_str = ", ".join(sorted(meal_name_counts.keys()))
            task_title = self.loc.t("shopping_task_title", emoji=emoji, meals=meals_str + date_range_str)

            # Create description with meals showing diet breakdown
            meal_lines = []
            for meal_name in sorted(meal_name_counts.keys()):
                diet_counts = meal_name_counts[meal_name]
                # Format: "• Meal Name: 3 high_calorie, 2 low_calorie"
                diet_parts = [f"{count} {diet}" for diet, count in sorted(diet_counts.items())]
                meal_lines.append(f"• {meal_name}: {', '.join(diet_parts)}")

            description = "\n".join(meal_lines) if meal_lines else self.loc.t("shopping_task_description")

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

                # Calculate and add per-portion calorie info
                meal_calories = self.calculate_meal_calories(meal)

                if meal_calories and portions_by_person:
                    calories_info = []
                    for person in sorted(portions_by_person.keys()):
                        # Map person to their diet profile
                        diet_profile = self.config.diet_profiles.get(person, person)

                        if diet_profile in meal_calories:
                            total_calories = meal_calories[diet_profile]

                            # Calculate per-portion calories
                            if is_meal_prep:
                                # For meal prep: divide by total portions for this person
                                total_portions = portions_by_person[person]
                                calories_per_portion = total_calories // total_portions if total_portions > 0 else total_calories
                            else:
                                # For multiple sessions: divide by number of sessions (1 portion per session)
                                calories_per_portion = total_calories // num_cooking_sessions

                            calories_info.append(f"{person}: ~{calories_per_portion} kcal/portion")

                    if calories_info:
                        description_lines.append(self.loc.t("cooking_task_description_calories", calories=', '.join(calories_info)))

                if not is_meal_prep:
                    description_lines.append(self.loc.t("cooking_task_description_session", current=idx + 1, total=num_cooking_sessions))

                # Check if anyone eats on this cooking date
                eating_dates_per_person = meal.get('eating_dates_per_person', {})
                people_eating_today = []
                for person, dates in eating_dates_per_person.items():
                    if cooking_date in dates:
                        people_eating_today.append(person)

                if people_eating_today:
                    people_str = ', '.join(sorted(people_eating_today))
                    description_lines.append(self.loc.t("cooking_task_eating_today", people=people_str))
                else:
                    # Nobody eats on cooking day - note for meal prep
                    description_lines.append(self.loc.t("cooking_task_meal_prep_note"))

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

    def create_eating_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate eating tasks ONLY for dates where no cooking happens."""
        from collections import defaultdict
        tasks = []

        for meal in meal_plan['meals']:
            meal_name = meal['name']
            cooking_dates_set = set(meal.get('cooking_dates', []))
            eating_dates_per_person = meal.get('eating_dates_per_person', {})
            meal_calories = self.calculate_meal_calories(meal)
            assigned_cook = meal.get('assigned_cook', '')

            # Group eating dates by date (track who eats when)
            dates_to_people = defaultdict(list)
            for person, dates in eating_dates_per_person.items():
                for date in dates:
                    # ONLY create eating task if NOT a cooking date
                    if date not in cooking_dates_set:
                        dates_to_people[date].append(person)

            # Create task for each non-cooking eating date
            for date, people in dates_to_people.items():
                emoji = "🍽️ " if self.config.use_emojis else ""
                task_title = self.loc.t("eating_task_title", emoji=emoji, meal=meal_name)

                # Description with people and calories
                people_str = ', '.join(sorted(people))
                description = self.loc.t("eating_task_description", meal=meal_name, people=people_str)

                # Add per-portion calories
                if meal_calories:
                    calories_per_portion = {}
                    for person in people:
                        # meal_calories has person names as keys (from per_person data)
                        if person in meal_calories:
                            total_cals = meal_calories[person]
                            num_eating_dates = len(eating_dates_per_person[person])
                            calories_per_portion[person] = total_cals // num_eating_dates

                    if calories_per_portion:
                        cal_info = ', '.join(f"{p}: ~{c} kcal" for p, c in calories_per_portion.items())
                        description += f"\n{cal_info}"

                task = Task(
                    title=task_title,
                    description=description,
                    due_date=date,
                    priority=self.config.eating_priority,
                    assigned_to=assigned_cook,
                    meal_id=meal['meal_id'],
                    task_type="eating"
                )
                tasks.append(task)

        return tasks

    def generate_all_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate all tasks from a meal plan."""
        tasks = []
        tasks.extend(self.create_shopping_tasks(meal_plan))
        tasks.extend(self.create_prep_tasks(meal_plan))
        tasks.extend(self.create_cooking_tasks(meal_plan))
        tasks.extend(self.create_eating_tasks(meal_plan))
        return tasks
