"""
Todoist adapter for meal planning tasks.
This adapter takes Task objects and creates them in Todoist.
"""

from typing import List, Optional

from todoist_api_python.api import TodoistAPI

from recipier.config import TaskConfig
from recipier.localization import Localizer
from recipier.meal_planner import MealPlanner, Task


class TodoistAdapter:
    """Adapter for creating tasks in Todoist."""

    def __init__(self, api_token: str, config: TaskConfig = None):
        """
        Initialize Todoist adapter.

        Args:
            api_token: Todoist API token
            config: Task configuration
        """
        self.api = TodoistAPI(api_token)
        self.config = config or TaskConfig()
        self.localizer = Localizer(language=self.config.language)
        self.project_id: Optional[str] = None
        self.sections: dict[str, str] = {}  # task_type -> section_id

    def get_or_create_project(self) -> str:
        """Get existing project ID or create a new project."""
        try:
            # get_projects() returns a ResultsPaginator
            projects_paginator = self.api.get_projects()

            # Convert to list to iterate
            projects = list(projects_paginator)

            # Flatten if nested (ResultsPaginator returns list of lists)
            if projects and isinstance(projects[0], list):
                projects = [p for sublist in projects for p in sublist]

            for project in projects:
                if project.name == self.config.todoist.project_name:
                    self.project_id = project.id
                    print(f"✓ Using existing project: {self.config.todoist.project_name}")
                    return project.id
        except Exception as e:
            print(f"Warning: Error fetching projects: {e}")

        # Create new project if not found
        print(f"Creating new project: {self.config.todoist.project_name}")
        project = self.api.add_project(name=self.config.todoist.project_name)
        self.project_id = project.id
        print(f"✓ Created new project: {self.config.todoist.project_name}")
        return project.id

    def get_user_ids(self) -> None:
        self.user_ids = {}
        try:
            collaborators = list(self.api.get_collaborators(project_id="6fgJjvvgQX92XJcf"))[0]
            for user in collaborators:
                for key, name in self.config.todoist.user_mapping.items():
                    if user.name == name:
                        self.user_ids[key] = user.id
        except Exception as e:
            print(f"Warning: Could not fetch user ids: {e}")

    def get_or_create_sections(self) -> None:
        """Get or create sections for organizing tasks."""
        if not self.config.todoist.use_sections:
            return

        # Get existing sections (returns ResultsPaginator)
        try:
            sections_paginator = self.api.get_sections(project_id=self.project_id)
            sections = list(sections_paginator)

            # Flatten if needed (same as projects)
            if sections and isinstance(sections[0], list):
                sections = [s for sublist in sections for s in sublist]

            section_map = {s.name: s.id for s in sections}
        except Exception as e:
            print(f"Warning: Could not fetch sections: {e}")
            section_map = {}

        # Map task types to localized section names
        section_names = {
            "shopping": self.localizer.get_section_name("shopping"),
            "prep": self.localizer.get_section_name("prep"),
            "cooking": self.localizer.get_section_name("cooking"),
            "eating": self.localizer.get_section_name("eating"),
        }

        # Create or get section IDs
        for task_type, section_name in section_names.items():
            if section_name in section_map:
                self.sections[task_type] = section_map[section_name]
            else:
                section = self.api.add_section(name=section_name, project_id=self.project_id)
                self.sections[task_type] = section.id

    def create_task_in_todoist(self, task: Task, parent_id: Optional[str] = None) -> str:
        """
        Create a single task in Todoist.

        Args:
            task: Task object to create
            parent_id: Optional parent task ID for subtasks

        Returns:
            Created task ID
        """
        # Prepare task parameters
        task_params = {
            "content": task.title,
            "project_id": self.project_id,
            "priority": task.priority,
        }

        # Add description if not empty
        if task.description:
            task_params["description"] = task.description

        # Add due date if present
        if task.due_date:
            task_params["due_string"] = task.due_date

        # Add parent if this is a subtask
        if parent_id:
            task_params["parent_id"] = parent_id
        # Otherwise add section if configured and not a subtask
        elif self.config.todoist.use_sections and task.task_type in self.sections:
            task_params["section_id"] = self.sections[task.task_type]

        # Add labels if present (task-specific labels + task type labels from config)
        labels = list(task.labels) if task.labels else []

        # Add task type labels from config if not a subtask
        if not parent_id and task.task_type:
            if task.task_type == "shopping" and self.config.todoist.shopping_labels:
                labels.extend(self.config.todoist.shopping_labels)
            elif task.task_type == "prep" and self.config.todoist.prep_labels:
                labels.extend(self.config.todoist.prep_labels)
            elif task.task_type == "cooking" and self.config.todoist.cooking_labels:
                labels.extend(self.config.todoist.cooking_labels)
            elif task.task_type == "eating" and self.config.todoist.eating_labels:
                labels.extend(self.config.todoist.eating_labels)

        if labels:
            task_params["labels"] = labels

        # Assign task to a user
        if task.assigned_to and task.assigned_to in self.user_ids:
            task_params["assignee_id"] = self.user_ids[task.assigned_to]

        # Create the task
        created_task = self.api.add_task(**task_params)
        return created_task.id

    def create_tasks(self, tasks: List[Task]) -> None:
        """
        Create all tasks in Todoist, including subtasks.

        Args:
            tasks: List of Task objects to create
        """
        # Ensure project exists
        self.get_or_create_project()

        # Fetch user id
        self.get_user_ids()

        # Create sections if enabled
        self.get_or_create_sections()

        for task in tasks:
            # Create parent task
            parent_id = self.create_task_in_todoist(task)

            # Create subtasks
            for subtask in task.subtasks:
                self.create_task_in_todoist(subtask, parent_id=parent_id)

    def create_from_meal_plan(self, meal_plan_data: dict, meals_db: dict) -> None:
        """
        Create tasks from a meal plan dictionary.

        Args:
            meal_plan_data: Meal plan data as dictionary
            meals_db: Meals database dictionary
        """
        planner = MealPlanner(config=self.config, meals_db=meals_db)
        expanded_plan = planner.expand_meal_plan(meal_plan_data)
        tasks = planner.generate_all_tasks(expanded_plan)
        self.create_tasks(tasks)
