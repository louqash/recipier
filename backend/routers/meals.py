"""Meals database endpoints."""

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query

from backend.config_loader import get_config
from backend.models.schemas import Meal, MealPlan, MealsDatabase
from recipier.meal_planner import MealPlanner

logger = logging.getLogger(__name__)
router = APIRouter()

# Path to meals database (can be overridden in tests)
MEALS_DB_PATH = os.path.join(os.path.dirname(__file__), "../..", "meals_database.json")


def get_meals_db_path() -> str:
    """Get the meals database path (allows for test overrides)."""
    return MEALS_DB_PATH


def load_meals_database() -> dict:
    """Load meals database from JSON file."""
    try:
        with open(MEALS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="meals_database.json file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing meals_database.json: {str(e)}")


def validate_people_in_meal_plan(meal_plan_dict: dict, diet_profiles: dict) -> None:
    """
    Validate that all people in the meal plan exist in the config.

    Raises HTTPException 422 if any person is not found in diet_profiles.
    """
    available_people = set(diet_profiles.keys())
    unknown_people = set()

    for meal in meal_plan_dict.get("scheduled_meals", []):
        eating_dates_per_person = meal.get("eating_dates_per_person", {})
        for person in eating_dates_per_person.keys():
            if person not in available_people:
                unknown_people.add(person)

    if unknown_people:
        unknown_list = ", ".join(sorted(unknown_people))
        available_list = ", ".join(sorted(available_people))
        raise HTTPException(
            status_code=422, detail=f"Unknown people in meal plan: {unknown_list}. Available people: {available_list}"
        )


@router.get("")
@router.get("/")
async def get_meals(
    search: Optional[str] = Query(None, description="Filter by meal name or ingredient (case-insensitive)"),
    language: Optional[str] = Query("polish", description="Language for future translations"),
):
    """
    Load entire meals database with optional filtering/search.

    - **search**: Filter meals by name or ingredient name (case-insensitive substring match)
    - **language**: Language preference (currently not used, for future)
    """
    db = load_meals_database()
    meals = db.get("meals", [])

    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        filtered_meals = []

        for meal in meals:
            # Check if search matches meal name
            if search_lower in meal["name"].lower():
                filtered_meals.append(meal)
                continue

            # Check if search matches any ingredient name
            ingredients = meal.get("ingredients", [])
            if any(search_lower in ing["name"].lower() for ing in ingredients):
                filtered_meals.append(meal)

        meals = filtered_meals

    return {"meals": meals, "total_count": len(meals)}


@router.get("/ingredient-details")
async def get_ingredient_details():
    """
    Get ingredient details for rounding and calorie calculations.

    Returns dictionary mapping ingredient names to detail objects.
    """
    db = load_meals_database()
    ingredient_details = db.get("ingredient_details", {})

    if not ingredient_details:
        raise HTTPException(status_code=500, detail="ingredient_details not found in meals database")

    return {"ingredient_details": ingredient_details}


@router.get("/{meal_id}")
async def get_meal_by_id(meal_id: str):
    """
    Get single meal details by meal_id.

    - **meal_id**: Unique meal identifier
    """
    db = load_meals_database()
    meals = db.get("meals", [])

    # Find meal by ID
    meal = next((m for m in meals if m["meal_id"] == meal_id), None)

    if not meal:
        raise HTTPException(status_code=404, detail=f"Meal '{meal_id}' not found in database")

    return meal


@router.post("/calculate-nutrition")
async def calculate_meal_plan_nutrition(meal_plan: MealPlan):
    """
    Calculate nutrition values with rounding applied for entire meal plan.

    Backend reads diet_profiles from my_config.json automatically.

    Returns nutrition for each scheduled meal and profile:
    ```json
    {
      "sm_1234567890": {
        "high_calorie": {"calories": 2850, "fat": 95.0, "protein": 180.0, "carbs": 280.0},
        "low_calorie": {"calories": 1700, "fat": 57.0, "protein": 107.0, "carbs": 167.0}
      }
    }
    ```

    - **meal_plan**: Meal plan object with scheduled_meals array
    """
    try:
        # Load meals database from file
        meals_database = load_meals_database()

        # Get cached config (includes diet_profiles)
        config = get_config()

        # Convert Pydantic model to dict for meal planner
        meal_plan_dict = meal_plan.model_dump()

        # Validate that all people exist in config
        validate_people_in_meal_plan(meal_plan_dict, config.diet_profiles)

        planner = MealPlanner(config, meals_db=meals_database)

        # Calculate nutrition with rounding applied
        num_meals = len(meal_plan_dict.get("scheduled_meals", []))
        logger.info(f"Calculating nutrition for {num_meals} scheduled meals")
        nutrition_data = planner.calculate_meal_plan_nutrition(meal_plan_dict, apply_rounding=True)

        logger.info(f"Successfully calculated nutrition for {len(nutrition_data)} meals")
        return nutrition_data

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except KeyError as e:
        logger.error(f"Missing required field in meal plan: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Missing required field in meal plan: {str(e)}")
    except ValueError as e:
        logger.error(f"Invalid meal plan data: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid meal plan data: {str(e)}")
    except Exception as e:
        logger.exception(f"Error calculating nutrition: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating nutrition: {str(e)}")
