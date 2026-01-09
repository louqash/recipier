"""Meals database endpoints."""

import json
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.models.schemas import Meal, MealsDatabase

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
