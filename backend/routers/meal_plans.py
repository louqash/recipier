"""
Meal plan management endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
from recipier.localization import Localizer

router = APIRouter()


class ScheduledMealRequest(BaseModel):
    id: str  # Unique instance ID (sm_{timestamp})
    meal_id: str
    cooking_dates: List[str]
    eating_dates_per_person: Dict[str, List[str]]
    meal_type: str
    assigned_cook: str
    prep_assigned_to: Optional[str] = None


class ShoppingTripRequest(BaseModel):
    shopping_date: str
    scheduled_meal_ids: List[str]


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

    # Get language from request or default to polish
    language = getattr(meal_plan, 'language', 'polish')
    loc = Localizer(language)

    for idx, meal in enumerate(meal_plan.scheduled_meals):
        eating_dates = meal.eating_dates_per_person
        first_cooking = min(meal.cooking_dates) if meal.cooking_dates else None
        meal_label = f"Meal {idx + 1}"

        # Each person must have eating dates
        if not eating_dates:
            errors.append(f"{meal_label}: {loc.t('error_no_eating_dates')}")

        for person, dates in eating_dates.items():
            # At least 1 eating date
            if len(dates) == 0:
                errors.append(f"{meal_label}: {loc.t('error_person_no_eating_dates', person=person)}")

            # Eating dates >= first cooking date
            for eating_date in dates:
                if first_cooking and eating_date < first_cooking:
                    errors.append(
                        f"{meal_label}: {loc.t('error_eating_before_cooking', person=person, eating_date=eating_date, cooking_date=first_cooking)}"
                    )

            # For multiple cooking dates: portions divisible by sessions
            if len(meal.cooking_dates) > 1:
                if len(dates) % len(meal.cooking_dates) != 0:
                    errors.append(
                        f"{meal_label}: {loc.t('error_eating_dates_not_divisible', person=person, num_eating=len(dates), num_cooking=len(meal.cooking_dates))}"
                    )

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
