"""
Core meal planning logic - independent of any task management system.
Can be used by CLI, MCP server, or web interface.
"""

import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from recipier.config import TaskConfig
from recipier.localization import Localizer, get_localizer
from recipier.rounding_warnings import generate_rounding_warning


@dataclass
class Task:
    """Represents a task to be created."""

    title: str
    description: str
    priority: int
    assigned_to: str
    due_date: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    subtasks: List["Task"] = field(default_factory=list)
    meal_id: Optional[str] = None
    task_type: str = "other"  # shopping, prep, cooking


class MealPlanner:
    """Core meal planning logic."""

    def __init__(self, config: TaskConfig = None, meals_db: Dict[str, Any] = None):
        """Initialize with optional configuration and meals database."""
        self.config: TaskConfig = config or TaskConfig()
        self.loc: Localizer = get_localizer(self.config.language)
        self.meals_db: Dict[str, Any] = meals_db or {}

        # Load ingredient details
        self.ingredient_details = meals_db.get("ingredient_details", {}) if meals_db else {}

        # Extract calories for easy access
        self.ingredient_calories = {
            name: details["calories_per_100g"] for name, details in self.ingredient_details.items()
        }

    def load_meals_database(self, file_path: str) -> Dict[str, Any]:
        """Load meals database JSON file and store it."""
        with open(file_path, "r") as f:
            data = json.load(f)

        if "meals" not in data:
            raise ValueError("Meals database must contain 'meals' key")

        # Store the database and extract calories
        self.meals_db = data
        self.ingredient_calories = data.get("ingredient_calories", {})

        return data

    def load_meal_plan(self, plan_path: str, meals_db_path: str) -> Dict[str, Any]:
        """Load meal plan and expand with meals database."""
        # Load meal plan
        with open(plan_path, "r") as f:
            meal_plan = json.load(f)

        if "scheduled_meals" not in meal_plan or "shopping_trips" not in meal_plan:
            raise ValueError("Meal plan must contain 'scheduled_meals' and 'shopping_trips'")

        # Load meals database (stores in self.meals_db)
        self.load_meals_database(meals_db_path)

        # Expand and return
        return self.expand_meal_plan(meal_plan)

    def expand_meal_plan(self, meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Expand meal plan by merging with stored meals database."""
        if not self.meals_db or "meals" not in self.meals_db:
            raise ValueError("Meals database not loaded. Call load_meals_database() or pass meals_db to __init__()")

        # Create lookup for meals database
        meals_lookup = {meal["meal_id"]: meal for meal in self.meals_db["meals"]}

        expanded_meals = []

        for scheduled in meal_plan["scheduled_meals"]:
            meal_id = scheduled["meal_id"]

            if meal_id not in meals_lookup:
                raise ValueError(f"Meal '{meal_id}' not found in database")

            recipe = meals_lookup[meal_id]
            # Convert eating dates to servings (number of eating dates = number of portions)
            eating_dates = scheduled["eating_dates_per_person"]
            servings = {person: len(dates) for person, dates in eating_dates.items()}

            # Calculate ingredients based on servings
            total_ingredients = []
            for base_ing in recipe["ingredients"]:
                # Calculate per person and total
                total_qty = 0
                per_person_data = {}

                for person, num_servings in servings.items():
                    if num_servings > 0:
                        # Map user to diet profile
                        diet_profile = self.config.diet_profiles[person]

                        # Use meal-level base_servings
                        base_serving_size = recipe.get("base_servings", {}).get(diet_profile, 1.0)
                        person_qty = round(base_ing["quantity"] * base_serving_size * num_servings)
                        total_qty += person_qty
                        per_person_data[person] = {
                            "quantity": person_qty,
                            "unit": base_ing["unit"],
                            "portions": num_servings,
                        }

                ingredient = {
                    "name": base_ing["name"],
                    "quantity": round(total_qty),
                    "unit": base_ing["unit"],
                    "category": base_ing["category"],
                    "per_person": per_person_data,
                }

                if "notes" in base_ing:
                    ingredient["notes"] = base_ing["notes"]

                total_ingredients.append(ingredient)

            # Build expanded meal
            expanded_meal = {
                "id": scheduled["id"],  # Unique instance ID
                "meal_id": meal_id,
                "name": recipe["name"],
                "cooking_dates": scheduled["cooking_dates"],
                "meal_type": scheduled["meal_type"],
                "assigned_cook": scheduled["assigned_cook"],
                "eating_dates_per_person": scheduled["eating_dates_per_person"],
                "ingredients": total_ingredients,
            }

            if "notes" in recipe:
                expanded_meal["notes"] = recipe["notes"]

            # Include cooking steps if available
            if "steps" in recipe:
                expanded_meal["steps"] = recipe["steps"]

            # Include suggested seasonings if available
            if "suggested_seasonings" in recipe:
                expanded_meal["suggested_seasonings"] = recipe["suggested_seasonings"]

            # Handle prep tasks
            if "prep_tasks" in recipe:
                prep_tasks = []
                for prep in recipe["prep_tasks"]:
                    prep_task = prep.copy()
                    prep_task["assigned_to"] = scheduled.get("prep_assigned_to", scheduled["assigned_cook"])
                    prep_tasks.append(prep_task)
                expanded_meal["prep_tasks"] = prep_tasks

            expanded_meals.append(expanded_meal)

        return {"meals": expanded_meals, "shopping_trips": meal_plan["shopping_trips"]}

    def parse_meal_plan(self, data: str | Dict[str, Any]) -> Dict[str, Any]:
        """Parse meal plan from JSON string or dict."""
        if isinstance(data, str):
            data = json.loads(data)

        if "meals" not in data or "shopping_trips" not in data:
            raise ValueError("JSON must contain 'meals' and 'shopping_trips' keys")

        return data

    def convert_ingredient_for_display(self, ingredient_name: str, quantity: float, unit: str) -> tuple:
        """
        Convert ingredient quantity to display format.
        For ingredients like eggs, converts grams to pieces.

        Returns:
            tuple: (converted_quantity, display_unit)
        """
        details = self.ingredient_details.get(ingredient_name)

        # Check if ingredient has display_unit conversion (like eggs -> szt.)
        if details and details.get("display_unit") and details.get("grams_per_unit") and unit == "g":
            converted_qty = round(quantity / details["grams_per_unit"])
            return (converted_qty, details["display_unit"])

        # Return original quantity and unit
        return (quantity, unit)

    def format_ingredient_title(self, ingredient: Dict[str, Any]) -> str:
        """Format ingredient title (with notes if present)."""
        # Handle seasonings without quantities (just name + notes)
        if not ingredient["quantity"] and not ingredient["unit"]:
            title = ingredient["name"]
        else:
            # Convert to display format if needed (e.g., eggs: grams -> pieces)
            display_qty, display_unit = self.convert_ingredient_for_display(
                ingredient["name"], ingredient["quantity"], ingredient["unit"]
            )

            title = self.config.ingredient_format.format(
                quantity=display_qty, unit=display_unit, name=ingredient["name"]
            )

        # Add notes to title if present
        if ingredient.get("notes"):
            title += f" ({ingredient['notes']})"

        return title

    def group_ingredients_by_category(self, ingredients: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group ingredients by category in configured order."""
        by_category = defaultdict(list)

        for ing in ingredients:
            category = ing.get("category", "other")
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
            sorted_ingredients = sorted(by_category[category], key=lambda x: x["name"])

            for ing in sorted_ingredients:
                title = self.format_ingredient_title(ing)
                # Use localized category label
                labels = [self.loc.get_category_label(category)] if self.config.use_ingredient_category_labels else []

                subtask = Task(
                    title=title,
                    description="",  # Notes are in the title
                    priority=4,  # Low priority for subtasks
                    assigned_to="",  # Inherited from parent
                    labels=labels,
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
        if not meal or "ingredients" not in meal or not self.ingredient_calories:
            return {}

        # Collect all people from per_person data and map to diet profiles
        people = set()
        for ing in meal["ingredients"]:
            if "per_person" in ing:
                people.update(ing["per_person"].keys())

        if not people:
            return {}

        # Map people to their diet profiles
        profile_totals = {}
        for person in people:
            profile = self.config.diet_profiles.get(person, person)
            if profile not in profile_totals:
                profile_totals[profile] = 0.0

        # Calculate calories for each ingredient
        for ing in meal["ingredients"]:
            ingredient_name = ing["name"]
            calories_per_100g = self.ingredient_calories.get(ingredient_name, 0)

            if "per_person" not in ing:
                continue

            # Add calories for each person (mapped to their profile)
            for person in people:
                if person in ing["per_person"]:
                    profile = self.config.diet_profiles.get(person, person)
                    quantity = ing["per_person"][person]["quantity"]
                    # Calculate calories: (quantity / 100) * calories_per_100g
                    calories = (quantity / 100.0) * calories_per_100g
                    profile_totals[profile] += calories

        # Round all totals to integers
        return {profile: round(total) for profile, total in profile_totals.items()}

    def calculate_meal_nutrition(self, meal: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        Calculate total nutrition (calories, fat, protein, carbs) for a meal for all diet profiles.

        Args:
            meal: Expanded meal object with ingredients containing per_person data

        Returns:
            Dictionary with profile names as keys and nutrition dicts as values
            e.g., {
                "high_calorie": {"calories": 2850, "fat": 95.0, "protein": 180.0, "carbs": 280.0},
                "low_calorie": {"calories": 1700, "fat": 57.0, "protein": 107.0, "carbs": 167.0}
            }
        """
        if not meal or "ingredients" not in meal or not self.ingredient_details:
            return {}

        # Collect all people from per_person data and map to diet profiles
        people = set()
        for ing in meal["ingredients"]:
            if "per_person" in ing:
                people.update(ing["per_person"].keys())

        if not people:
            return {}

        # Initialize nutrition totals for each profile
        profile_nutrition = {}
        for person in people:
            profile = self.config.diet_profiles.get(person, person)
            if profile not in profile_nutrition:
                profile_nutrition[profile] = {
                    "calories": 0.0,
                    "fat": 0.0,
                    "protein": 0.0,
                    "carbs": 0.0,
                }

        # Calculate nutrition for each ingredient
        for ing in meal["ingredients"]:
            ingredient_name = ing["name"]
            details = self.ingredient_details.get(ingredient_name, {})

            # Get nutrition values per 100g (default to 0 if not present)
            calories_per_100g = details.get("calories_per_100g", 0)
            fat_per_100g = details.get("fat_per_100g", 0)
            protein_per_100g = details.get("protein_per_100g", 0)
            carbs_per_100g = details.get("carbs_per_100g", 0)

            if "per_person" not in ing:
                continue

            # Add nutrition for each person (mapped to their profile)
            for person in people:
                if person in ing["per_person"]:
                    profile = self.config.diet_profiles.get(person, person)
                    quantity = ing["per_person"][person]["quantity"]

                    # Calculate nutrition: (quantity / 100) * nutrition_per_100g
                    profile_nutrition[profile]["calories"] += (quantity / 100.0) * calories_per_100g
                    profile_nutrition[profile]["fat"] += (quantity / 100.0) * fat_per_100g
                    profile_nutrition[profile]["protein"] += (quantity / 100.0) * protein_per_100g
                    profile_nutrition[profile]["carbs"] += (quantity / 100.0) * carbs_per_100g

        # Round all nutrition values
        for profile in profile_nutrition:
            profile_nutrition[profile] = {
                "calories": round(profile_nutrition[profile]["calories"]),
                "fat": round(profile_nutrition[profile]["fat"], 1),
                "protein": round(profile_nutrition[profile]["protein"], 1),
                "carbs": round(profile_nutrition[profile]["carbs"], 1),
            }

        return profile_nutrition

    def calculate_meal_plan_nutrition(
        self, meal_plan: Dict[str, Any], apply_rounding: bool = True
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Calculate nutrition for entire meal plan with optional rounding applied.

        This method:
        1. Expands the meal plan (populates per_person data)
        2. Applies rounding logic if enabled (updates per_person quantities)
        3. Calculates nutrition for each scheduled meal using rounded quantities

        Args:
            meal_plan: Meal plan with scheduled_meals
            apply_rounding: If True, apply ingredient rounding before calculating nutrition

        Returns:
            Dictionary mapping scheduled_meal_id -> profile -> nutrition dict
            e.g., {
                "sm_1234567890": {
                    "high_calorie": {"calories": 2850, "fat": 95.0, "protein": 180.0, "carbs": 280.0},
                    "low_calorie": {"calories": 1700, "fat": 57.0, "protein": 107.0, "carbs": 167.0}
                }
            }
        """
        # Step 1: Expand meal plan to populate per_person data
        expanded_plan = self.expand_meal_plan(meal_plan)

        # Step 2: Apply rounding if enabled
        if apply_rounding and self.config.enable_ingredient_rounding:
            self.round_and_distribute_ingredients(expanded_plan)

        # Step 3: Calculate nutrition for each scheduled meal
        nutrition_by_meal = {}

        for meal in expanded_plan.get("meals", []):
            meal_id = meal.get("id")
            if meal_id:
                nutrition_by_meal[meal_id] = self.calculate_meal_nutrition(meal)

        return nutrition_by_meal

    def create_person_portion_subtasks(self, ingredients: List[Dict[str, Any]]) -> List[Task]:
        """Create per-person portion subtasks for cooking tasks, organized by ingredient."""
        subtasks = []

        # Group ingredients by category for ordered processing
        by_category = self.group_ingredients_by_category(ingredients)

        # Process ingredients in category order, creating a subtask for each ingredient-person combination
        for category in self.config.shopping_categories:
            if category not in by_category:
                continue

            sorted_ingredients = sorted(by_category[category], key=lambda x: x["name"])

            for ing in sorted_ingredients:
                # Check if there's per_person data
                if "per_person" not in ing:
                    continue

                # Create a subtask for each person for this ingredient
                for person in sorted(ing["per_person"].keys()):
                    person_portion = ing["per_person"][person]
                    quantity = person_portion["quantity"]
                    unit = person_portion["unit"]

                    # Convert to display format if needed (e.g., eggs: grams -> pieces)
                    display_qty, display_unit = self.convert_ingredient_for_display(ing["name"], quantity, unit)

                    # Create subtask: "2 szt. Jajka" or "240g Ryż" with person as label
                    subtask = Task(
                        title=f"{display_qty}{display_unit} {ing['name']}",
                        description="",
                        priority=4,
                        assigned_to="",
                        labels=[person],  # Add person as label for filtering
                    )
                    subtasks.append(subtask)

        return subtasks

    def aggregate_ingredients_across_trips(
        self, meal_plan: Dict[str, Any]
    ) -> tuple[Dict[str, Dict[str, Any]], Dict[str, List[tuple[int, float]]]]:
        """
        Aggregate ingredients across entire meal plan.

        Returns:
            - aggregated: Dict[ingredient_name, {total_qty, unit, category, per_person_totals, notes}]
            - trip_needs: Dict[ingredient_name, List[(trip_index, quantity_needed)]]
        """
        aggregated = {}
        trip_needs = defaultdict(list)
        meals_by_id = {meal["id"]: meal for meal in meal_plan["meals"]}

        # If no shopping trips, treat all meals as one virtual trip
        shopping_trips = meal_plan.get("shopping_trips", [])
        if not shopping_trips:
            # Create a virtual trip with all scheduled meals
            all_meal_ids = [meal["id"] for meal in meal_plan["meals"]]
            shopping_trips = [{"scheduled_meal_ids": all_meal_ids}]

        for trip_index, trip in enumerate(shopping_trips):
            # Collect ingredients for this trip
            trip_ingredients = defaultdict(
                lambda: {
                    "quantity": 0,
                    "unit": None,
                    "category": None,
                    "per_person": defaultdict(lambda: {"quantity": 0, "unit": None, "portions": 0}),
                    "notes": None,
                }
            )

            for scheduled_meal_id in trip["scheduled_meal_ids"]:
                meal = meals_by_id.get(scheduled_meal_id)
                if not meal:
                    continue

                for ing in meal["ingredients"]:
                    name = ing["name"]
                    trip_ingredients[name]["quantity"] += ing["quantity"]
                    trip_ingredients[name]["unit"] = ing["unit"]
                    trip_ingredients[name]["category"] = ing["category"]
                    trip_ingredients[name]["notes"] = ing.get("notes")

                    # Aggregate per_person data
                    for person, person_data in ing.get("per_person", {}).items():
                        trip_ingredients[name]["per_person"][person]["quantity"] += person_data["quantity"]
                        trip_ingredients[name]["per_person"][person]["unit"] = person_data["unit"]
                        trip_ingredients[name]["per_person"][person]["portions"] += person_data["portions"]

            # Store trip needs and add to totals
            for name, data in trip_ingredients.items():
                trip_needs[name].append((trip_index, data["quantity"]))

                if name not in aggregated:
                    aggregated[name] = {
                        "total_qty": 0,
                        "unit": data["unit"],
                        "category": data["category"],
                        "per_person_totals": defaultdict(lambda: {"quantity": 0, "unit": None, "portions": 0}),
                        "notes": data["notes"],
                    }

                aggregated[name]["total_qty"] += data["quantity"]

                # Aggregate per_person across all trips
                for person, person_data in data["per_person"].items():
                    aggregated[name]["per_person_totals"][person]["quantity"] += person_data["quantity"]
                    aggregated[name]["per_person_totals"][person]["unit"] = person_data["unit"]
                    aggregated[name]["per_person_totals"][person]["portions"] += person_data["portions"]

        return aggregated, dict(trip_needs)

    def distribute_rounded_quantity_across_trips(
        self, rounded_total: float, unit_size: float, trip_needs: List[tuple[int, float]]
    ) -> List[float]:
        """
        Distribute rounded total across shopping trips using whole units.
        Strategy: Track cumulative leftovers, buy units only when needed.
        Last trip adjusts to match rounded total exactly.

        Args:
            rounded_total: Total rounded quantity (already a multiple of unit_size)
            unit_size: Size of one unit
            trip_needs: List of (trip_index, quantity_needed)

        Returns:
            List of quantities per trip (all multiples of unit_size)
        """
        if not trip_needs:
            return []

        # Sort by trip index
        trip_needs_sorted = sorted(trip_needs, key=lambda x: x[0])
        num_trips = len(trip_needs_sorted)
        total_units = int(round(rounded_total / unit_size))

        allocated_units = []
        leftover = 0.0  # Track leftover from previous trips (in quantity, not units)

        for i in range(num_trips - 1):
            _, need = trip_needs_sorted[i]
            available = leftover

            if available >= need:
                # Have enough from leftovers, buy nothing
                allocated_units.append(0)
                leftover = available - need
            else:
                # Need more, calculate deficit and buy enough units
                deficit = need - available
                units_to_buy = math.ceil(deficit / unit_size)
                allocated_units.append(units_to_buy)
                bought = units_to_buy * unit_size
                leftover = available + bought - need

        # Last trip: adjust to match total exactly
        last_trip_units = total_units - sum(allocated_units)
        allocated_units.append(last_trip_units)

        # Convert back to quantities
        return [units * unit_size for units in allocated_units]

    def compensate_calories_per_profile(
        self,
        aggregated: Dict[str, Dict[str, Any]],
        calorie_delta_per_profile: Dict[str, float],
        meal_plan: Dict[str, Any],
    ) -> None:
        """
        Compensate calorie changes by adjusting only adjustable ingredients.
        Modifies aggregated dict in-place and updates meal plan ingredients proportionally.

        Args:
            aggregated: Aggregated ingredients with per_person_totals
            calorie_delta_per_profile: Calories to remove per diet profile (positive = reduce)
            meal_plan: Meal plan to update with adjusted quantities
        """
        # Find adjustable ingredients
        adjustable_ingredients = []
        adjustable_calories_per_profile = defaultdict(float)

        for ing_name, ing_data in aggregated.items():
            details = self.ingredient_details.get(ing_name, {})
            if details.get("adjustable", True) and not details.get("unit_size"):
                adjustable_ingredients.append(ing_name)

                # Calculate current calories for each profile
                calories_per_100 = details.get("calories_per_100g", 0)
                for person, person_data in ing_data["per_person_totals"].items():
                    diet_profile = self.config.diet_profiles.get(person, person)
                    calories = (person_data["quantity"] / 100) * calories_per_100
                    adjustable_calories_per_profile[diet_profile] += calories

        if not adjustable_ingredients:
            # No adjustable ingredients, cannot compensate
            return

        # Calculate adjustment factors per profile
        adjustment_factors = {}
        for profile, delta in calorie_delta_per_profile.items():
            if adjustable_calories_per_profile[profile] > 0:
                # Factor = (current - delta) / current
                adjustment_factors[profile] = (
                    adjustable_calories_per_profile[profile] - delta
                ) / adjustable_calories_per_profile[profile]
            else:
                adjustment_factors[profile] = 1.0

        # Apply adjustments to aggregated per_person_totals
        for ing_name in adjustable_ingredients:
            ing_data = aggregated[ing_name]
            for person, person_data in ing_data["per_person_totals"].items():
                diet_profile = self.config.diet_profiles.get(person, person)
                factor = adjustment_factors.get(diet_profile, 1.0)
                person_data["quantity"] = round(person_data["quantity"] * factor)

            # Recalculate total
            ing_data["total_qty"] = sum(
                person_data["quantity"] for person_data in ing_data["per_person_totals"].values()
            )

        # Apply adjustments proportionally to meal plan ingredients
        meals_by_id = {meal["id"]: meal for meal in meal_plan["meals"]}

        # Get all meals either from shopping trips or directly
        if meal_plan.get("shopping_trips"):
            meals_to_process = [
                meals_by_id[scheduled_meal_id]
                for trip in meal_plan["shopping_trips"]
                for scheduled_meal_id in trip["scheduled_meal_ids"]
                if scheduled_meal_id in meals_by_id
            ]
        else:
            meals_to_process = meal_plan["meals"]

        for meal in meals_to_process:
            for ing in meal["ingredients"]:
                if ing["name"] in adjustable_ingredients:
                    # Adjust per_person quantities
                    for person, person_data in ing.get("per_person", {}).items():
                        diet_profile = self.config.diet_profiles.get(person, person)
                        factor = adjustment_factors.get(diet_profile, 1.0)
                        person_data["quantity"] = round(person_data["quantity"] * factor)

                    # Recalculate total
                    ing["quantity"] = sum(person_data["quantity"] for person_data in ing.get("per_person", {}).values())

    def round_and_distribute_ingredients(self, meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Round ingredients at meal plan level, then distribute across shopping trips.

        Returns: RoundingResult-like dict with ingredients_per_trip, warnings, and calorie_adjustments
        """
        # Phase 1: Aggregate ingredients across all shopping trips (or all meals if no trips)
        aggregated, trip_needs = self.aggregate_ingredients_across_trips(meal_plan)

        warnings = []
        calorie_delta_per_profile = defaultdict(float)

        # Phase 2: Round quantities with unit_size and track calorie changes
        # Only perform rounding if enabled in config
        if self.config.enable_ingredient_rounding:
            for ing_name, ing_data in aggregated.items():
                details = self.ingredient_details.get(ing_name, {})
                unit_size = details.get("unit_size")

                if unit_size:
                    original_total = ing_data["total_qty"]
                    # Round to nearest multiple, enforce minimum 1 unit
                    rounded_total = max(unit_size, round(original_total / unit_size) * unit_size)

                    # Generate warning if needed
                    warning = generate_rounding_warning(ing_name, original_total, rounded_total, unit_size, meal_plan)
                    if warning:
                        warnings.append(warning)

                    # Calculate calorie delta per profile
                    calories_per_100 = details.get("calories_per_100g", 0)
                    delta_qty = rounded_total - original_total

                    for person, person_data in ing_data["per_person_totals"].items():
                        diet_profile = self.config.diet_profiles.get(person, person)
                        # Proportional delta for this person
                        person_ratio = person_data["quantity"] / original_total if original_total > 0 else 0
                        person_delta_qty = delta_qty * person_ratio
                        person_delta_cal = (person_delta_qty / 100) * calories_per_100
                        calorie_delta_per_profile[diet_profile] += person_delta_cal

                    # Update aggregated total
                    ing_data["total_qty"] = rounded_total

                    # Phase 3: Apply rounded quantities to meal plan
                    # If no shopping trips, update all meals proportionally
                    # If shopping trips exist, distribute across trips
                    meals_by_id = {meal["id"]: meal for meal in meal_plan["meals"]}
                    has_shopping_trips = bool(meal_plan.get("shopping_trips"))

                    if has_shopping_trips and ing_name in trip_needs:
                        # Distribute across shopping trips
                        distributed_quantities = self.distribute_rounded_quantity_across_trips(
                            rounded_total, unit_size, trip_needs[ing_name]
                        )

                        # Store distribution for later use
                        ing_data["distributed_quantities"] = distributed_quantities

                        # Apply distributed quantities to meal plan
                        sorted_trip_needs = sorted(trip_needs[ing_name], key=lambda x: x[0])
                        for (trip_index, _), dist_qty in zip(sorted_trip_needs, distributed_quantities):
                            trip = meal_plan["shopping_trips"][trip_index]

                            for scheduled_meal_id in trip["scheduled_meal_ids"]:
                                meal = meals_by_id.get(scheduled_meal_id)
                                if not meal:
                                    continue

                                # Find the ingredient in the meal and update its quantity
                                for ing in meal["ingredients"]:
                                    if ing["name"] == ing_name:
                                        # Calculate this meal's share of the distributed quantity
                                        meal_original_qty = ing["quantity"]
                                        trip_original_total = sum(
                                            meals_by_id[mid]["ingredients"][j]["quantity"]
                                            for mid in trip["scheduled_meal_ids"]
                                            if mid in meals_by_id
                                            for j, ing_item in enumerate(meals_by_id[mid]["ingredients"])
                                            if ing_item["name"] == ing_name
                                        )

                                        if trip_original_total > 0:
                                            ratio = meal_original_qty / trip_original_total
                                            meal_new_qty = round(dist_qty * ratio)

                                            # Update total quantity
                                            ing["quantity"] = meal_new_qty

                                            # Update per_person quantities proportionally
                                            if "per_person" in ing:
                                                for person, person_data in ing["per_person"].items():
                                                    person_ratio = (
                                                        person_data["quantity"] / meal_original_qty
                                                        if meal_original_qty > 0
                                                        else 0
                                                    )
                                                    person_data["quantity"] = round(meal_new_qty * person_ratio)
                    else:
                        # No shopping trips - update all meals proportionally
                        for meal in meal_plan["meals"]:
                            for ing in meal["ingredients"]:
                                if ing["name"] == ing_name:
                                    meal_original_qty = ing["quantity"]
                                    if original_total > 0:
                                        ratio = meal_original_qty / original_total
                                        meal_new_qty = round(rounded_total * ratio)

                                        # Update total quantity
                                        ing["quantity"] = meal_new_qty

                                        # Update per_person quantities proportionally
                                        if "per_person" in ing:
                                            for person, person_data in ing["per_person"].items():
                                                person_ratio = (
                                                    person_data["quantity"] / meal_original_qty
                                                    if meal_original_qty > 0
                                                    else 0
                                                )
                                                person_data["quantity"] = round(meal_new_qty * person_ratio)

            # Phase 4: Compensate calories by adjusting adjustable ingredients
            if any(abs(delta) > 0.1 for delta in calorie_delta_per_profile.values()):
                self.compensate_calories_per_profile(aggregated, calorie_delta_per_profile, meal_plan)
                # Recalculate aggregated after compensation
                aggregated, trip_needs = self.aggregate_ingredients_across_trips(meal_plan)

        # Phase 5: Build ingredients_per_trip from meal plan (now with adjusted quantities)
        meals_by_id = {meal["id"]: meal for meal in meal_plan["meals"]}
        ingredients_per_trip = []

        for trip in meal_plan["shopping_trips"]:
            trip_ingredients = defaultdict(
                lambda: {
                    "quantity": 0,
                    "unit": None,
                    "category": None,
                    "per_person": defaultdict(lambda: {"quantity": 0, "unit": None, "portions": 0}),
                    "notes": None,
                }
            )

            for scheduled_meal_id in trip["scheduled_meal_ids"]:
                meal = meals_by_id.get(scheduled_meal_id)
                if not meal:
                    continue

                for ing in meal["ingredients"]:
                    name = ing["name"]
                    trip_ingredients[name]["quantity"] += ing["quantity"]
                    trip_ingredients[name]["unit"] = ing["unit"]
                    trip_ingredients[name]["category"] = ing["category"]
                    trip_ingredients[name]["notes"] = ing.get("notes")

                    for person, person_data in ing.get("per_person", {}).items():
                        trip_ingredients[name]["per_person"][person]["quantity"] += person_data["quantity"]
                        trip_ingredients[name]["per_person"][person]["unit"] = person_data["unit"]
                        trip_ingredients[name]["per_person"][person]["portions"] += person_data["portions"]

            # Convert to list format
            trip_ing_list = []
            for name, data in trip_ingredients.items():
                trip_ing_list.append(
                    {
                        "name": name,
                        "quantity": data["quantity"],
                        "unit": data["unit"],
                        "category": data["category"],
                        "per_person": dict(data["per_person"]),
                        "notes": data["notes"],
                    }
                )

            ingredients_per_trip.append(trip_ing_list)

        return {
            "ingredients_per_trip": ingredients_per_trip,
            "warnings": warnings,
            "calorie_adjustments": dict(calorie_delta_per_profile),
        }

    def create_shopping_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate shopping tasks from meal plan with ingredient rounding."""
        tasks = []

        # NEW: Round ingredients at meal plan level and get per-trip distributions
        rounding_result = self.round_and_distribute_ingredients(meal_plan)

        # Build lookup by scheduled meal instance ID
        meals_by_id = {meal["id"]: meal for meal in meal_plan["meals"]}

        for trip_index, trip in enumerate(meal_plan["shopping_trips"]):
            # Get pre-calculated rounded ingredients for this trip
            all_ingredients = rounding_result["ingredients_per_trip"][trip_index]

            # Collect meal info
            meal_name_counts = {}  # meal_name -> {diet_profile: count}
            all_eating_dates = []  # Collect all eating dates for date range
            all_seasonings = set()  # Collect unique seasonings

            for scheduled_meal_id in trip["scheduled_meal_ids"]:
                if scheduled_meal_id in meals_by_id:
                    meal = meals_by_id[scheduled_meal_id]
                    meal_name = meal["name"]

                    # Count portions by diet type
                    if meal_name not in meal_name_counts:
                        meal_name_counts[meal_name] = {}

                    eating_dates_per_person = meal.get("eating_dates_per_person", {})
                    for person, eating_dates in eating_dates_per_person.items():
                        # Map person to their diet profile
                        diet_profile = self.config.diet_profiles.get(person, person)
                        portions = len(eating_dates)
                        meal_name_counts[meal_name][diet_profile] = (
                            meal_name_counts[meal_name].get(diet_profile, 0) + portions
                        )
                        all_eating_dates.extend(eating_dates)

                    # Collect seasonings from this meal
                    if "suggested_seasonings" in meal and meal["suggested_seasonings"]:
                        # Parse comma-separated seasonings and clean whitespace
                        seasonings = [s.strip() for s in meal["suggested_seasonings"].split(",")]
                        all_seasonings.update(seasonings)

            # Add seasonings as pseudo-ingredients to the shopping list
            for seasoning in sorted(all_seasonings):
                seasoning_item = {
                    "name": seasoning,
                    "quantity": "",  # No quantity for seasonings
                    "unit": "",
                    "category": "spices",
                    "notes": self.loc.t("seasoning_note"),
                }
                all_ingredients.append(seasoning_item)

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
                due_date=trip["shopping_date"],
                priority=self.config.shopping_priority,
                assigned_to="",  # No assignment - can be set manually in Todoist
                subtasks=subtasks,
                task_type="shopping",
            )
            tasks.append(task)

        return tasks

    def create_prep_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate prep tasks from meal plan."""
        tasks = []

        for meal in meal_plan["meals"]:
            if "prep_tasks" not in meal or not meal["prep_tasks"]:
                continue

            meal_name = meal["name"]
            # Get and sort cooking dates
            cooking_dates = sorted(meal.get("cooking_dates", []))
            if not cooking_dates:
                continue

            num_cooking_sessions = len(cooking_dates)
            is_meal_prep = num_cooking_sessions == 1

            # Create prep tasks for each cooking session
            for cooking_date_str in cooking_dates:
                cooking_date = datetime.strptime(cooking_date_str, "%Y-%m-%d")

                for prep in meal["prep_tasks"]:
                    emoji = "🥘 " if self.config.use_emojis else ""
                    task_title = self.loc.t("prep_task_title", emoji=emoji, meal=meal_name)

                    # Calculate prep date
                    prep_date = cooking_date - timedelta(days=prep["days_before"])
                    prep_date_str = prep_date.strftime("%Y-%m-%d")

                    assigned_to = prep["assigned_to"]
                    description = self.loc.t(
                        "prep_task_description",
                        description=prep["description"],
                        date=cooking_date_str,
                    )

                    # Create per-person portion subtasks with ingredient quantities
                    # For prep tasks, always show full quantities (prep is done once for all portions)
                    subtasks = self.create_person_portion_subtasks(meal["ingredients"])

                    task = Task(
                        title=task_title,
                        description=description,
                        due_date=prep_date_str,
                        priority=self.config.prep_priority,
                        assigned_to=assigned_to,
                        meal_id=meal["meal_id"],
                        task_type="prep",
                        subtasks=subtasks,
                    )
                    tasks.append(task)

        return tasks

    def divide_ingredients(self, ingredients: List[Dict[str, Any]], divisor: int) -> List[Dict[str, Any]]:
        """Divide ingredient quantities by divisor for multiple cooking sessions."""
        divided = []
        for ing in ingredients:
            ing_copy = ing.copy()
            if "per_person" in ing_copy:
                per_person_copy = {}
                for person, data in ing_copy["per_person"].items():
                    per_person_copy[person] = {
                        "quantity": round(data["quantity"] / divisor),
                        "unit": data["unit"],
                        "portions": data.get("portions", 1) / divisor,
                    }
                ing_copy["per_person"] = per_person_copy
            divided.append(ing_copy)
        return divided

    def filter_ingredients_for_people(
        self, ingredients: List[Dict[str, Any]], people_eating: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter ingredients to only include specific people.
        Used when cooking for a subset of people on a specific cooking date.

        Args:
            ingredients: Full ingredient list with per_person data
            people_eating: List of people eating on this cooking date

        Returns:
            Filtered ingredients with only the specified people's quantities
        """
        people_set = set(people_eating)
        filtered = []

        for ing in ingredients:
            ing_copy = ing.copy()
            if "per_person" in ing_copy:
                # Filter per_person to only include people eating today
                filtered_per_person = {
                    person: data for person, data in ing_copy["per_person"].items() if person in people_set
                }

                if filtered_per_person:
                    ing_copy["per_person"] = filtered_per_person
                    # Recalculate total quantity for this subset
                    ing_copy["quantity"] = sum(data["quantity"] for data in filtered_per_person.values())
                    filtered.append(ing_copy)
            elif people_eating:
                # If no per_person data, include the ingredient as-is
                filtered.append(ing_copy)

        return filtered

    def create_cooking_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate cooking tasks from meal plan."""
        tasks = []

        for meal in meal_plan["meals"]:
            # Get and sort cooking dates
            cooking_dates = sorted(meal.get("cooking_dates", []))
            num_cooking_sessions = len(cooking_dates)
            is_meal_prep = num_cooking_sessions == 1

            # Extract portions info from ingredients (once, outside loop)
            portions_by_person = {}
            for ing in meal["ingredients"]:
                if "per_person" in ing:
                    for person, data in ing["per_person"].items():
                        if "portions" in data:
                            if person not in portions_by_person:
                                portions_by_person[person] = data["portions"]

            # Create a cooking task for each date
            for idx, cooking_date in enumerate(cooking_dates):
                emoji = "👨‍🍳 " if self.config.use_emojis else ""
                task_title = self.loc.t("cooking_task_title", emoji=emoji, meal=meal["name"])
                if not is_meal_prep:
                    task_title += f" ({cooking_date})"

                # Build description
                meal_type_translated = self.loc.get_meal_type_translation(meal["meal_type"])
                # Check if anyone eats on this cooking date (move this up before descriptions)
                eating_dates_per_person = meal.get("eating_dates_per_person", {})
                people_eating_today = []
                for person, dates in eating_dates_per_person.items():
                    if cooking_date in dates:
                        people_eating_today.append(person)

                description_lines = [
                    self.loc.t(
                        "cooking_task_description_line1",
                        meal_type=meal_type_translated,
                        date=cooking_date,
                    ),
                ]

                # Add portions info (only for people eating today)
                if is_meal_prep:
                    # For meal prep, show all portions
                    if portions_by_person:
                        portions_info = []
                        for person in sorted(portions_by_person.keys()):
                            total_portions = portions_by_person[person]
                            portion_word = (
                                self.loc.t("portion_singular") if total_portions == 1 else self.loc.t("portion_plural")
                            )
                            portions_info.append(f"{person}: {total_portions} {portion_word}")
                        description_lines.append(
                            self.loc.t("cooking_task_description_portions", portions=", ".join(portions_info))
                        )
                else:
                    # For multiple cooking dates, show only people eating today
                    if people_eating_today:
                        portions_info = []
                        for person in sorted(people_eating_today):
                            # Each person gets 1 portion on their eating date
                            portion_word = self.loc.t("portion_singular")
                            portions_info.append(f"{person}: 1 {portion_word}")
                        description_lines.append(
                            self.loc.t("cooking_task_description_portions", portions=", ".join(portions_info))
                        )

                # Calculate and add per-portion calorie info
                meal_calories = self.calculate_meal_calories(meal)

                # Show calories only for people eating today (or all for meal prep)
                people_for_calories = sorted(portions_by_person.keys()) if is_meal_prep else sorted(people_eating_today)

                if meal_calories and people_for_calories:
                    calories_info = []
                    for person in people_for_calories:
                        # Map person to their diet profile
                        diet_profile = self.config.diet_profiles.get(person, person)

                        if diet_profile in meal_calories:
                            total_calories = meal_calories[diet_profile]

                            # Calculate per-portion calories
                            if is_meal_prep:
                                # For meal prep: divide by total portions for this person
                                total_portions = portions_by_person.get(person, 1)
                                calories_per_portion = (
                                    total_calories // total_portions if total_portions > 0 else total_calories
                                )
                            else:
                                # For multiple sessions: show calories for 1 portion (their eating on this date)
                                # Total calories represent all portions, need to divide by person's total eating dates
                                person_eating_dates = eating_dates_per_person.get(person, [])
                                num_person_portions = len(person_eating_dates)
                                calories_per_portion = (
                                    total_calories // num_person_portions if num_person_portions > 0 else total_calories
                                )

                            calories_info.append(f"{person}: ~{calories_per_portion} kcal/portion")

                    if calories_info:
                        description_lines.append(
                            self.loc.t(
                                "cooking_task_description_calories",
                                calories=", ".join(calories_info),
                            )
                        )

                if not is_meal_prep:
                    description_lines.append(
                        self.loc.t(
                            "cooking_task_description_session",
                            current=idx + 1,
                            total=num_cooking_sessions,
                        )
                    )

                # Add eating info (already calculated people_eating_today at top)
                if people_eating_today:
                    people_str = ", ".join(sorted(people_eating_today))
                    description_lines.append(self.loc.t("cooking_task_eating_today", people=people_str))
                else:
                    # Nobody eats on cooking day - note for meal prep
                    description_lines.append(self.loc.t("cooking_task_meal_prep_note"))

                if meal.get("notes"):
                    description_lines.append(f"\n{meal['notes']}")

                # Add cooking steps if available
                if meal.get("steps"):
                    description_lines.append("\n" + self.loc.t("cooking_steps_header"))
                    for i, step in enumerate(meal["steps"], 1):
                        description_lines.append(f"{i}. {step}")

                # Add suggested seasonings if available
                if meal.get("suggested_seasonings"):
                    description_lines.append(
                        f"\n{self.loc.t('suggested_seasonings_label')}: {meal['suggested_seasonings']}"
                    )

                description = "\n".join(description_lines)

                # Create per-person portion subtasks with adjusted quantities
                if is_meal_prep:
                    subtasks = self.create_person_portion_subtasks(meal["ingredients"])
                else:
                    # Filter ingredients to only include people eating on this specific cooking date
                    filtered_ingredients = self.filter_ingredients_for_people(meal["ingredients"], people_eating_today)
                    subtasks = self.create_person_portion_subtasks(filtered_ingredients)

                task = Task(
                    title=task_title,
                    description=description,
                    due_date=cooking_date,
                    priority=self.config.cooking_priority,
                    assigned_to=meal["assigned_cook"],
                    subtasks=subtasks,
                    meal_id=meal["meal_id"],
                    task_type="cooking",
                )
                tasks.append(task)

        return tasks

    def create_eating_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate eating tasks ONLY for dates where no cooking happens."""
        from collections import defaultdict

        tasks = []

        for meal in meal_plan["meals"]:
            meal_name = meal["name"]
            cooking_dates_set = set(meal.get("cooking_dates", []))
            eating_dates_per_person = meal.get("eating_dates_per_person", {})
            meal_calories = self.calculate_meal_calories(meal)
            assigned_cook = meal.get("assigned_cook", "")

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

                # Build description with multiple parts
                description_lines = []

                # Description with people and calories
                people_str = ", ".join(sorted(people))
                description_lines.append(self.loc.t("eating_task_description", meal=meal_name, people=people_str))

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
                        cal_info = ", ".join(f"{p}: ~{c} kcal" for p, c in calories_per_portion.items())
                        description_lines.append(cal_info)

                # Add cooking steps if available
                if meal.get("steps"):
                    description_lines.append("\n" + self.loc.t("cooking_steps_header"))
                    for i, step in enumerate(meal["steps"], 1):
                        description_lines.append(f"{i}. {step}")

                # Add suggested seasonings if available
                if meal.get("suggested_seasonings"):
                    description_lines.append(
                        f"\n{self.loc.t('suggested_seasonings_label')}: {meal['suggested_seasonings']}"
                    )

                description = "\n".join(description_lines)

                task = Task(
                    title=task_title,
                    description=description,
                    due_date=date,
                    priority=self.config.eating_priority,
                    assigned_to=assigned_cook,
                    meal_id=meal["meal_id"],
                    task_type="eating",
                )
                tasks.append(task)

        return tasks

    def check_rounding_warnings(self, meal_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for rounding warnings without generating tasks.

        Returns list of warning dictionaries with ingredient_name, original_quantity,
        rounded_quantity, percent_change, and suggested_portions.
        """
        expanded = self.expand_meal_plan(meal_plan)
        rounding_result = self.round_and_distribute_ingredients(expanded)
        return rounding_result["warnings"]

    def generate_all_tasks(self, meal_plan: Dict[str, Any]) -> List[Task]:
        """Generate all tasks from a meal plan with ingredient rounding."""
        # Expand and round ingredients once for all task types
        expanded_plan = self.expand_meal_plan(meal_plan)

        tasks = []
        tasks.extend(self.create_shopping_tasks(expanded_plan))
        tasks.extend(self.create_prep_tasks(expanded_plan))
        tasks.extend(self.create_cooking_tasks(expanded_plan))
        tasks.extend(self.create_eating_tasks(expanded_plan))
        return tasks
