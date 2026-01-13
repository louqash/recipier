"""
Configuration for meal planning task creator.
"""

import json
import os
from typing import Dict, List

from pydantic import BaseModel, Field, model_validator


class TodoistConfig(BaseModel):
    """Todoist-specific configuration."""

    # Project settings
    project_name: str = "Meal Planning"
    use_sections: bool = True

    # User mapping (internal name -> Todoist username)
    # The internal names should match the keys in TaskConfig.diet_profiles
    user_mapping: Dict[str, str] = Field(default_factory=dict)

    # Task type labels - these labels will be applied to all tasks of each type
    shopping_labels: List[str] = Field(default_factory=list)  # Labels for all shopping tasks
    prep_labels: List[str] = Field(default_factory=list)  # Labels for all prep tasks
    cooking_labels: List[str] = Field(default_factory=list)  # Labels for all cooking tasks
    serving_labels: List[str] = Field(default_factory=list)  # Labels for all serving tasks


class TaskConfig(BaseModel):
    """Configuration for task creation and formatting."""

    # Shopping categories and their display order
    shopping_categories: List[str] = Field(
        default_factory=lambda: [
            "produce",
            "meat",
            "dairy",
            "pantry",
            "frozen",
            "bakery",
            "beverages",
            "spices",
            "other",
        ]
    )

    # Task formatting
    use_emojis: bool = True
    ingredient_format: str = "{quantity}{unit} {name}"
    language: str = "polish"  # "polish" or "english"
    use_ingredient_category_labels: bool = (
        True  # Add ingredient category (produce, meat, etc.) as label to shopping subtasks
    )
    enable_ingredient_rounding: bool = True  # Round ingredients to package/unit sizes

    # Task priorities (1=urgent, 2=high, 3=normal, 4=low)
    shopping_priority: int = 2
    prep_priority: int = 2
    cooking_priority: int = 3
    serving_priority: int = 3

    # User diet profiles - defines users and their dietary needs
    # Maps user names to diet profiles (e.g., {"John": "high_calorie", "Jane": "low_calorie"})
    diet_profiles: Dict[str, str] = Field(default_factory=dict)

    # Todoist-specific configuration
    todoist: TodoistConfig = Field(default_factory=TodoistConfig)

    @model_validator(mode="after")
    def validate_user_mappings(self) -> "TaskConfig":
        """Validate that all users in diet_profiles have a Todoist user mapping."""
        if self.diet_profiles and self.todoist.user_mapping:
            users_without_mapping = [
                user for user in self.diet_profiles.keys() if user not in self.todoist.user_mapping
            ]
            if users_without_mapping:
                raise ValueError(
                    f"All users in diet_profiles must have a Todoist user mapping. "
                    f"Missing Todoist mappings for: {', '.join(users_without_mapping)}"
                )
        return self

    @classmethod
    def from_file(cls, config_path: str) -> "TaskConfig":
        """Load configuration from a JSON file."""
        if not os.path.exists(config_path):
            return cls()

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            # Return default config if file is invalid
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to load config from {config_path}: {e}. Using defaults.")
            return cls()

    def to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        with open(config_path, "w") as f:
            f.write(self.model_dump_json(indent=2))
