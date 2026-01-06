"""
Todoist task generation endpoints
"""

import json
import os
import sys
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.routers.meals import MEALS_DB_PATH
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


class TaskGenerationRequest(BaseModel):
    meal_plan: MealPlanRequest
    todoist_token: str
    config: Optional[Dict] = None


class TaskGenerationResponse(BaseModel):
    success: bool
    tasks_created: int
    message: str


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

        if not todoist_token:
            raise HTTPException(status_code=400, detail="Todoist API token not provided and not set in environment")
        # Load configuration
        if request.config:
            config = TaskConfig(**request.config)
        else:
            # Try to load my_config.json if it exists
            config_path = os.path.join(os.getcwd(), "my_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                config = TaskConfig(**config_data)
            else:
                config = TaskConfig()

        # Load meals database
        if not os.path.exists(MEALS_DB_PATH):
            raise HTTPException(status_code=500, detail=f"Meals database not found at {MEALS_DB_PATH}")

        with open(MEALS_DB_PATH, "r", encoding="utf-8") as f:
            meals_db = json.load(f)

        # Initialize meal planner with config and meals database
        planner = MealPlanner(config, meals_db)

        # Validate and expand meal plan
        meal_plan_data = request.meal_plan.model_dump()

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

            for person, dates in eating_dates.items():
                if not dates:
                    validation_errors.append(f"{meal_label}: {person} has no eating dates")
                    continue

                for eating_date in dates:
                    if eating_date < first_cooking:
                        validation_errors.append(
                            f"{meal_label}: {person} eating date {eating_date} is before cooking date {first_cooking}"
                        )

        if validation_errors:
            raise HTTPException(status_code=422, detail={"validation_errors": validation_errors})

        expanded_plan = planner.expand_meal_plan(meal_plan_data)

        # Generate tasks from expanded meal plan
        all_tasks = planner.generate_all_tasks(expanded_plan)

        if not all_tasks:
            return TaskGenerationResponse(success=True, tasks_created=0, message="No tasks to create")

        # Initialize Todoist adapter with resolved token
        adapter = TodoistAdapter(todoist_token, config)

        # Create tasks in Todoist
        created_tasks = adapter.create_tasks(all_tasks)

        # Handle case where create_tasks returns None
        task_count = len(created_tasks) if created_tasks else len(all_tasks)

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
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate tasks: {str(e)}")
