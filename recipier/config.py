"""
Configuration for meal planning task creator.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TaskConfig:
    """Configuration for task creation and formatting."""

    # Shopping categories and their display order
    shopping_categories: List[str] = field(
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
    use_category_labels: bool = True  # Add category as label to subtasks
    ingredient_format: str = "{quantity}{unit} {name}"
    language: str = "polish"  # "polish" or "english"

    # Task priorities (1=urgent, 2=high, 3=normal, 4=low)
    shopping_priority: int = 2
    prep_priority: int = 2
    cooking_priority: int = 3
    eating_priority: int = 3

    # Todoist project settings
    project_name: str = "Meal Planning"
    user_mapping: dict[str, str] = field(default_factory=lambda: {})
    diet_profiles: dict[str, str] = field(
        default_factory=lambda: {}
    )  # Maps user names to diet profiles (e.g., {"John": "high_calorie", "Jane": "low_calorie"})
    use_sections: bool = True
    shopping_section_name: str = "Shopping"
    prep_section_name: str = "Prep"
    cooking_section_name: str = "Cooking"
    eating_section_name: str = "Serving"

    def validate(self) -> None:
        """Validate configuration."""
        # Ensure all users in user_mapping have a diet profile assigned
        if self.user_mapping:
            users_without_diet = [user for user in self.user_mapping.keys() if user not in self.diet_profiles]
            if users_without_diet:
                raise ValueError(
                    f"All users in user_mapping must have a diet profile assigned. "
                    f"Missing diet profiles for: {', '.join(users_without_diet)}"
                )

    @classmethod
    def from_file(cls, config_path: str) -> "TaskConfig":
        """Load configuration from a JSON file."""
        if not os.path.exists(config_path):
            return cls()

        with open(config_path, "r") as f:
            data = json.load(f)
        config = cls(**data)
        config.validate()  # Validate after loading
        return config

    def to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        with open(config_path, "w") as f:
            json.dump(self.__dict__, f, indent=2)
