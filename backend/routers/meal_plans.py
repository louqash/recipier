"""
Meal plan management endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

router = APIRouter()


class ScheduledMealRequest(BaseModel):
    meal_id: str
    meal_name: str
    cooking_dates: List[str]
    servings_per_person: Dict[str, int]
    meal_type: str
    assigned_cook: str
    prep_assigned_to: Optional[str] = None


class ShoppingTripRequest(BaseModel):
    date: str
    meal_ids: List[str]


class MealPlanRequest(BaseModel):
    scheduled_meals: List[ScheduledMealRequest]
    shopping_trips: List[ShoppingTripRequest] = []


class SaveResponse(BaseModel):
    success: bool
    file_path: str
    message: str


@router.post("/validate")
async def validate_meal_plan(meal_plan: MealPlanRequest):
    """
    Validate a meal plan without saving
    """
    errors = []

    for idx, meal in enumerate(meal_plan.scheduled_meals):
        num_dates = len(meal.cooking_dates)

        # Validate cooking dates
        if num_dates == 0:
            errors.append(f"Meal {idx + 1} ({meal.meal_name}): At least one cooking date required")

        # For multiple cooking dates, portions must match
        if num_dates > 1:
            for person, portions in meal.servings_per_person.items():
                if portions != num_dates:
                    errors.append(
                        f"Meal {idx + 1} ({meal.meal_name}): "
                        f"For {num_dates} cooking dates, {person} must have {num_dates} portions (has {portions})"
                    )

        # Validate servings are non-negative
        for person, portions in meal.servings_per_person.items():
            if portions < 0:
                errors.append(f"Meal {idx + 1} ({meal.meal_name}): {person} servings cannot be negative")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


@router.post("/save", response_model=SaveResponse)
async def save_meal_plan(meal_plan: MealPlanRequest):
    """
    Save meal plan to JSON file
    Filename is based on earliest cooking date (YYYY-MM-DD.json)
    """
    try:
        # Validate first
        validation = await validate_meal_plan(meal_plan)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"message": "Meal plan validation failed", "errors": validation["errors"]}
            )

        # Find earliest cooking date
        all_dates = []
        for meal in meal_plan.scheduled_meals:
            all_dates.extend(meal.cooking_dates)

        if not all_dates:
            raise HTTPException(status_code=400, detail="No cooking dates found in meal plan")

        earliest_date = min(all_dates)

        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)

        # Create file path
        file_path = os.path.join(data_dir, f"{earliest_date}.json")

        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(meal_plan.model_dump(), f, indent=2, ensure_ascii=False)

        return SaveResponse(
            success=True,
            file_path=file_path,
            message=f"Meal plan saved successfully to {earliest_date}.json"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save meal plan: {str(e)}")


@router.get("/load/{date}")
async def load_meal_plan(date: str):
    """
    Load a meal plan from file by date (YYYY-MM-DD)
    """
    try:
        file_path = os.path.join(os.getcwd(), "data", f"{date}.json")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Meal plan for {date} not found")

        with open(file_path, 'r', encoding='utf-8') as f:
            meal_plan = json.load(f)

        return meal_plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load meal plan: {str(e)}")
