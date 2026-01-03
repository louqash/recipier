"""
Configuration for meal planning task creator.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import json
import os


@dataclass
class TaskConfig:
    """Configuration for task creation and formatting."""

    # Shopping categories and their display order
    shopping_categories: List[str] = field(default_factory=lambda: [
        'produce',
        'meat',
        'dairy',
        'pantry',
        'frozen',
        'bakery',
        'beverages',
        'other'
    ])

    # Task formatting
    use_emojis: bool = True
    use_category_labels: bool = True  # Add category as label to subtasks
    ingredient_format: str = "{quantity}{unit} {name}"

    # Task priorities (1=urgent, 2=high, 3=normal, 4=low)
    shopping_priority: int = 2
    prep_priority: int = 2
    cooking_priority: int = 3

    # Todoist project settings
    project_name: str = "Meal Planning"
    use_sections: bool = True
    shopping_section_name: str = "Shopping"
    prep_section_name: str = "Prep"
    cooking_section_name: str = "Cooking"

    @classmethod
    def from_file(cls, config_path: str) -> 'TaskConfig':
        """Load configuration from a JSON file."""
        if not os.path.exists(config_path):
            return cls()

        with open(config_path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
