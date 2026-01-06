"""Pydantic models for request/response validation."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# Meals Database Models
class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str
    category: str
    notes: Optional[str] = None
    base_servings_override: Optional[Dict[str, float]] = None


class PrepTask(BaseModel):
    description: str
    days_before: int
    assigned_to: Optional[str] = None


class Meal(BaseModel):
    meal_id: str
    name: str
    base_servings: Dict[str, float]
    ingredients: List[Ingredient]
    prep_tasks: Optional[List[PrepTask]] = None
    notes: Optional[str] = None


class MealsDatabase(BaseModel):
    meals: List[Meal]


# Meal Plan Models
class ScheduledMeal(BaseModel):
    id: str  # Unique instance ID (sm_{timestamp})
    meal_id: str  # Reference to recipe in database
    cooking_dates: List[str] = Field(..., min_length=1)
    meal_type: str  # breakfast, second_breakfast, dinner, supper
    assigned_cook: str  # User name from config, or "both"
    eating_dates_per_person: Dict[str, List[str]]  # Dates when each person eats (1 date = 1 portion)
    prep_assigned_to: Optional[str] = None


class ShoppingTrip(BaseModel):
    shopping_date: str
    scheduled_meal_ids: List[str]  # References scheduled meal instance IDs


class MealPlan(BaseModel):
    scheduled_meals: List[ScheduledMeal]
    shopping_trips: List[ShoppingTrip]


# Validation Response
class ValidationError(BaseModel):
    field: str
    message: str


class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


# Expanded Meal Plan Models
class PerPersonData(BaseModel):
    quantity: float
    unit: str
    portions: int


class ExpandedIngredient(BaseModel):
    name: str
    quantity: float
    unit: str
    category: str
    per_person: Dict[str, PerPersonData]
    notes: Optional[str] = None


class ExpandedMeal(BaseModel):
    id: str  # Unique instance ID
    meal_id: str  # Recipe reference
    name: str
    cooking_dates: List[str]
    meal_type: str
    assigned_cook: str
    ingredients: List[ExpandedIngredient]
    prep_tasks: Optional[List[PrepTask]] = None
    notes: Optional[str] = None


class ExpandedMealPlan(BaseModel):
    meals: List[ExpandedMeal]
    shopping_trips: List[ShoppingTrip]


# Task Generation Models
class TaskConfig(BaseModel):
    language: str = "polish"
    use_emojis: bool = True
    shopping_priority: int = 2
    prep_priority: int = 2
    cooking_priority: int = 3
    user_mapping: Dict[str, str] = {}


class TaskGenerationRequest(BaseModel):
    meal_plan: MealPlan
    config: TaskConfig
    todoist_token: str


class TaskSummary(BaseModel):
    task_type: str
    title: str
    todoist_id: Optional[str] = None


class TaskGenerationResponse(BaseModel):
    success: bool
    tasks_created: int
    tasks: List[TaskSummary]


# Save Meal Plan Response
class SaveResponse(BaseModel):
    success: bool
    filepath: str
    filename: str
