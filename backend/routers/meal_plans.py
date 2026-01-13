"""
Meal plan management endpoints
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config_loader import get_config
from backend.routers.meals import load_meals_database
from recipier.localization import Localizer

logger = logging.getLogger(__name__)
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
    language: Optional[str] = "polish"  # "polish" or "english"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "scheduled_meals": [
                        {
                            "id": "sm_1768215797284",
                            "meal_id": "pinsa_pomidorowa_mozzarella",
                            "cooking_dates": ["2026-01-15"],
                            "eating_dates_per_person": {"John": ["2026-01-15", "2026-01-16"], "Jane": ["2026-01-15"]},
                            "meal_type": "dinner",
                            "assigned_cook": "John",
                        }
                    ],
                    "shopping_trips": [{"shopping_date": "2026-01-14", "scheduled_meal_ids": ["sm_1768215797284"]}],
                }
            ]
        }
    }


@router.post("/validate")
async def validate_meal_plan(meal_plan: MealPlanRequest):
    """
    Validate a meal plan without saving.

    Checks:
    - Meal IDs exist in database
    - Each person has eating dates
    - For meal prep (1 cooking date): eating dates >= cooking date
    - For multiple cooking dates: eating dates must be in cooking dates
    - Scheduled meal IDs in shopping trips are valid
    """
    errors = []

    # Get language from request
    loc = Localizer(meal_plan.language)

    # Load meals database to validate meal_ids
    try:
        meals_db = load_meals_database()
        available_meal_ids = {meal["meal_id"] for meal in meals_db.get("meals", [])}
    except Exception as e:
        logger.error(f"Failed to load meals database during validation: {e}", exc_info=True)
        errors.append(f"Failed to load meals database: {str(e)}")
        return {"valid": False, "errors": errors}

    # Get config to validate people
    try:
        config = get_config()
        available_people = set(config.diet_profiles.keys())
    except Exception as e:
        logger.error(f"Failed to load config during validation: {e}", exc_info=True)
        errors.append(f"Failed to load config: {str(e)}")
        return {"valid": False, "errors": errors}

    # Check for unknown people in meal plan
    unknown_people = set()
    for meal in meal_plan.scheduled_meals:
        for person in meal.eating_dates_per_person.keys():
            if person not in available_people:
                unknown_people.add(person)

    if unknown_people:
        unknown_list = ", ".join(sorted(unknown_people))
        available_list = ", ".join(sorted(available_people))
        errors.append(loc.t("error_unknown_people", unknown_list=unknown_list, available_list=available_list))

    # Collect all scheduled meal IDs for shopping trip validation
    scheduled_meal_ids = {meal.id for meal in meal_plan.scheduled_meals}

    for idx, meal in enumerate(meal_plan.scheduled_meals):
        eating_dates = meal.eating_dates_per_person
        first_cooking = min(meal.cooking_dates) if meal.cooking_dates else None
        meal_label = f"Meal {idx + 1} ({meal.meal_id})"

        # Check if meal_id exists in database
        if meal.meal_id not in available_meal_ids:
            errors.append(f"{meal_label}: {loc.t('error_meal_not_found', meal_id=meal.meal_id)}")

        # Check cooking dates exist
        if not meal.cooking_dates or len(meal.cooking_dates) == 0:
            errors.append(f"{meal_label}: {loc.t('error_no_cooking_dates')}")

        # Each person must have eating dates
        if not eating_dates:
            errors.append(f"{meal_label}: {loc.t('error_no_eating_dates')}")

        # Create set of cooking dates for validation
        cooking_dates_set = set(meal.cooking_dates)
        is_meal_prep = len(meal.cooking_dates) == 1  # Meal prep: cook once for multiple days

        for person, dates in eating_dates.items():
            # At least 1 eating date
            if len(dates) == 0:
                errors.append(f"{meal_label}: {loc.t('error_person_no_eating_dates', person=person)}")

            # Validation depends on meal prep vs multiple cooking dates
            for eating_date in dates:
                if is_meal_prep:
                    # Meal prep: eating dates must be >= cooking date (can eat leftovers on future days)
                    if eating_date < first_cooking:
                        errors.append(
                            f"{meal_label}: {loc.t('error_eating_before_cooking', person=person, eating_date=eating_date, cooking_date=first_cooking)}"
                        )
                else:
                    # Multiple cooking dates: eating dates must be in cooking dates
                    if eating_date not in cooking_dates_set:
                        cooking_dates_str = ", ".join(sorted(cooking_dates_set))
                        errors.append(
                            f"{meal_label}: {loc.t('error_eating_date_not_in_cooking', person=person, eating_date=eating_date, cooking_dates=cooking_dates_str)}"
                        )

    # Validate shopping trips
    for idx, trip in enumerate(meal_plan.shopping_trips):
        trip_label = f"Shopping trip {idx + 1} ({trip.shopping_date})"

        # Check if shopping date is valid format
        try:
            datetime.strptime(trip.shopping_date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"{trip_label}: {loc.t('error_invalid_date_format')}")

        # Check if scheduled meal IDs exist
        for scheduled_meal_id in trip.scheduled_meal_ids:
            if scheduled_meal_id not in scheduled_meal_ids:
                errors.append(
                    f"{trip_label}: {loc.t('error_scheduled_meal_not_found', scheduled_meal_id=scheduled_meal_id)}"
                )

    return {"valid": len(errors) == 0, "errors": errors}
