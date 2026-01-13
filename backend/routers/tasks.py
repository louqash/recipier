"""
Todoist task generation endpoints
"""

import json
import logging
import os
import sys
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.routers.meals import MEALS_DB_PATH, validate_people_in_meal_plan
from backend.config_loader import get_config
from recipier.config import TaskConfig
from recipier.meal_planner import MealPlanner
from recipier.todoist_adapter import TodoistAdapter

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
    shopping_date: str  # Renamed from 'date'
    scheduled_meal_ids: List[str]  # Renamed from 'meal_ids'


class MealPlanRequest(BaseModel):
    scheduled_meals: List[ScheduledMealRequest]
    shopping_trips: List[ShoppingTripRequest] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "scheduled_meals": [
                        {
                            "id": "sm_1768215797284",
                            "meal_id": "pinsa_pomidorowa_mozzarella",
                            "cooking_dates": ["2026-01-15"],
                            "eating_dates_per_person": {
                                "John": ["2026-01-15", "2026-01-16"],
                                "Jane": ["2026-01-15"]
                            },
                            "meal_type": "dinner",
                            "assigned_cook": "John"
                        }
                    ],
                    "shopping_trips": [
                        {
                            "shopping_date": "2026-01-14",
                            "scheduled_meal_ids": ["sm_1768215797284"]
                        }
                    ]
                }
            ]
        }
    }


class TaskGenerationRequest(BaseModel):
    meal_plan: MealPlanRequest
    todoist_token: str
    enable_ingredient_rounding: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "meal_plan": {
                        "scheduled_meals": [
                            {
                                "id": "sm_1768215797284",
                                "meal_id": "pinsa_pomidorowa_mozzarella",
                                "cooking_dates": ["2026-01-15"],
                                "eating_dates_per_person": {
                                    "John": ["2026-01-15", "2026-01-16"],
                                    "Jane": ["2026-01-15"]
                                },
                                "meal_type": "dinner",
                                "assigned_cook": "John"
                            }
                        ],
                        "shopping_trips": [
                            {
                                "shopping_date": "2026-01-14",
                                "scheduled_meal_ids": ["sm_1768215797284"]
                            }
                        ]
                    },
                    "todoist_token": "your_todoist_api_token_here",
                    "enable_ingredient_rounding": True
                }
            ]
        }
    }


class TaskGenerationResponse(BaseModel):
    success: bool
    tasks_created: int
    message: str


class MealInfoItem(BaseModel):
    meal_name: str
    current_portions: int
    suggested_additional_portions: int


class RoundingWarningItem(BaseModel):
    ingredient_name: str
    original_quantity: float
    rounded_quantity: float
    percent_change: float
    meals: List[MealInfoItem] = []
    combined_increase: int = 0
    unit_size: float = 0


class RoundingWarningsResponse(BaseModel):
    warnings: List[RoundingWarningItem]


@router.post("/check-warnings", response_model=RoundingWarningsResponse)
async def check_rounding_warnings(request: MealPlanRequest):
    """
    Check for ingredient rounding warnings without generating tasks.
    Returns warnings if any ingredient will be significantly rounded (>50% change).
    """
    try:
        # Load meals database
        if not os.path.exists(MEALS_DB_PATH):
            raise HTTPException(status_code=500, detail=f"Meals database not found at {MEALS_DB_PATH}")

        with open(MEALS_DB_PATH, "r", encoding="utf-8") as f:
            meals_db = json.load(f)

        # Get cached config (includes diet_profiles)
        config = get_config()

        # Convert request to meal plan format
        meal_plan_data = request.model_dump()

        # Validate that all people exist in config
        validate_people_in_meal_plan(meal_plan_data, config.diet_profiles)

        # Initialize meal planner with config
        planner = MealPlanner(config, meals_db)

        # Check for warnings
        warnings = planner.check_rounding_warnings(meal_plan_data)

        logger.info(f"Checked rounding warnings: found {len(warnings)} warnings")
        return RoundingWarningsResponse(warnings=warnings)

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=TaskGenerationResponse)
async def generate_tasks(request: TaskGenerationRequest):
    """
    Generate Todoist tasks from meal plan
    Uses existing meal_planner.py and todoist_adapter.py

    Token priority:
    1. Environment variable TODOIST_API_TOKEN (if set)
    2. Token from request (from frontend sessionStorage)
    """
    try:
        # Use ENV token if available (takes priority for security)
        env_token = os.getenv("TODOIST_API_TOKEN")
        todoist_token = env_token if env_token else request.todoist_token

        # Validate token is provided and non-empty
        if not todoist_token or todoist_token.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Todoist API token is required. Set TODOIST_API_TOKEN environment variable or provide token in request."
            )

        # Get cached config (includes diet_profiles)
        config = get_config()

        # Override enable_ingredient_rounding if provided in request
        if request.enable_ingredient_rounding is not None:
            # Create a copy of config to avoid modifying the singleton
            config = config.model_copy(update={"enable_ingredient_rounding": request.enable_ingredient_rounding})

        # Load meals database
        if not os.path.exists(MEALS_DB_PATH):
            raise HTTPException(status_code=500, detail=f"Meals database not found at {MEALS_DB_PATH}")

        with open(MEALS_DB_PATH, "r", encoding="utf-8") as f:
            meals_db = json.load(f)

        # Validate and expand meal plan
        meal_plan_data = request.meal_plan.model_dump()

        # Validate that all people exist in config
        validate_people_in_meal_plan(meal_plan_data, config.diet_profiles)

        # Initialize meal planner with config and meals database
        planner = MealPlanner(config, meals_db)

        # Validate eating dates vs cooking dates
        validation_errors = []
        for idx, meal in enumerate(meal_plan_data.get("scheduled_meals", [])):
            meal_label = f"Meal {idx + 1}"
            eating_dates = meal.get("eating_dates_per_person", {})
            cooking_dates = meal.get("cooking_dates", [])

            if not cooking_dates:
                validation_errors.append(f"{meal_label}: No cooking dates specified")
                continue

            first_cooking = min(cooking_dates)
            cooking_dates_set = set(cooking_dates)
            is_meal_prep = len(cooking_dates) == 1  # Meal prep: cook once for multiple days

            for person, dates in eating_dates.items():
                if not dates:
                    validation_errors.append(f"{meal_label}: {person} has no eating dates")
                    continue

                # Validation depends on meal prep vs multiple cooking dates
                for eating_date in dates:
                    if is_meal_prep:
                        # Meal prep: eating dates must be >= cooking date (can eat leftovers on future days)
                        if eating_date < first_cooking:
                            validation_errors.append(
                                f"{meal_label}: {person} eating date {eating_date} is before cooking date {first_cooking}"
                            )
                    else:
                        # Multiple cooking dates: eating dates must be in cooking dates
                        if eating_date not in cooking_dates_set:
                            validation_errors.append(
                                f"{meal_label}: {person} eating date {eating_date} is not in cooking dates {sorted(cooking_dates_set)}"
                            )

        if validation_errors:
            raise HTTPException(status_code=422, detail={"validation_errors": validation_errors})

        # Generate tasks from meal plan (expansion happens internally)
        all_tasks = planner.generate_all_tasks(meal_plan_data)

        if not all_tasks:
            logger.info("No tasks to create for meal plan")
            return TaskGenerationResponse(success=True, tasks_created=0, message="No tasks to create")

        # Initialize Todoist adapter with resolved token
        adapter = TodoistAdapter(todoist_token, config)

        # Create tasks in Todoist
        logger.info(f"Creating {len(all_tasks)} tasks in Todoist")
        created_tasks = adapter.create_tasks(all_tasks)

        # Handle case where create_tasks returns None
        task_count = len(created_tasks) if created_tasks else len(all_tasks)

        logger.info(f"Successfully created {task_count} tasks in Todoist")
        return TaskGenerationResponse(
            success=True,
            tasks_created=task_count,
            message=f"Successfully created {task_count} tasks in Todoist",
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Validation errors or meal not found
        logger.error(f"Validation error during task generation: {e}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to generate tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate tasks: {str(e)}")
