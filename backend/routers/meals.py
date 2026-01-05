"""Meals database endpoints."""
import json
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.models.schemas import MealsDatabase, Meal

router = APIRouter()

# Path to meals database
MEALS_DB_PATH = os.path.join(os.path.dirname(__file__), "../..", "meals_database.json")


def load_meals_database() -> dict:
    """Load meals database from JSON file."""
    try:
        with open(MEALS_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="meals_database.json file not found"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing meals_database.json: {str(e)}"
        )


@router.get("/")
async def get_meals(
    search: Optional[str] = Query(None, description="Filter by meal name (case-insensitive)"),
    language: Optional[str] = Query("polish", description="Language for future translations")
):
    """
    Load entire meals database with optional filtering/search.

    - **search**: Filter meals by name (case-insensitive substring match)
    - **language**: Language preference (currently not used, for future)
    """
    db = load_meals_database()
    meals = db.get('meals', [])

    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        meals = [m for m in meals if search_lower in m['name'].lower()]

    return {
        "meals": meals,
        "total_count": len(meals)
    }


@router.get("/calories")
async def get_ingredient_calories():
    """
    Get ingredient calories dictionary for on-the-fly calorie calculations.

    Returns a dictionary mapping ingredient names to calories per 100g.
    """
    db = load_meals_database()
    ingredient_calories = db.get('ingredient_calories', {})

    if not ingredient_calories:
        raise HTTPException(
            status_code=500,
            detail="ingredient_calories not found in meals database"
        )

    return {
        "ingredient_calories": ingredient_calories
    }


@router.get("/{meal_id}")
async def get_meal_by_id(meal_id: str):
    """
    Get single meal details by meal_id.

    - **meal_id**: Unique meal identifier
    """
    db = load_meals_database()
    meals = db.get('meals', [])

    # Find meal by ID
    meal = next((m for m in meals if m['meal_id'] == meal_id), None)

    if not meal:
        raise HTTPException(
            status_code=404,
            detail=f"Meal '{meal_id}' not found in database"
        )

    return meal
