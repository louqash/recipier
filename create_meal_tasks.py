#!/usr/bin/env python3
"""
Meal Planning to Todoist Task Creator - CLI

This script reads a meal plan JSON file and creates tasks in Todoist.

Usage:
    python create_meal_tasks.py meal_plan.json [--config config.json]

Environment:
    TODOIST_API_TOKEN: Your Todoist API token (required)
"""

import sys
import os
import argparse

from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter
from config import TaskConfig


def main():
    parser = argparse.ArgumentParser(
        description='Create Todoist tasks from a meal plan JSON file'
    )
    parser.add_argument(
        'meal_plan',
        help='Path to meal plan JSON file'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration JSON file (optional)',
        default=None
    )

    args = parser.parse_args()

    # Get API token from environment
    api_token = os.getenv('TODOIST_API_TOKEN')
    if not api_token:
        print("✗ Error: TODOIST_API_TOKEN environment variable not set")
        print("\nGet your API token from: https://todoist.com/app/settings/integrations/developer")
        print("Then set it with: export TODOIST_API_TOKEN='your_token_here'")
        sys.exit(1)

    print("🍳 Meal Planning Task Creator")
    print("=" * 50)

    # Load configuration
    if args.config:
        print(f"Loading configuration from: {args.config}")
        config = TaskConfig.from_file(args.config)
    else:
        print("Using default configuration")
        config = TaskConfig()

    # Load meal plan
    print(f"Loading meal plan from: {args.meal_plan}")
    planner = MealPlanner(config=config)

    try:
        meal_plan = planner.load_meal_plan(args.meal_plan)
        print(f"✓ Loaded {len(meal_plan['meals'])} meals and {len(meal_plan['shopping_trips'])} shopping trips")
    except Exception as e:
        print(f"✗ Error loading meal plan: {e}")
        sys.exit(1)

    # Generate tasks
    print("\n📝 Generating tasks...")
    tasks = planner.generate_all_tasks(meal_plan)

    shopping_tasks = [t for t in tasks if t.task_type == 'shopping']
    prep_tasks = [t for t in tasks if t.task_type == 'prep']
    cooking_tasks = [t for t in tasks if t.task_type == 'cooking']

    print(f"  - {len(shopping_tasks)} shopping tasks")
    print(f"  - {len(prep_tasks)} prep tasks")
    print(f"  - {len(cooking_tasks)} cooking tasks")

    # Create tasks in Todoist
    print("\n🚀 Creating tasks in Todoist...")
    adapter = TodoistAdapter(api_token, config=config)

    try:
        adapter.create_tasks(tasks)
        print(f"\n✅ Successfully created {len(tasks)} tasks in Todoist!")
        print(f"   Project: {config.project_name}")
    except Exception as e:
        import traceback
        print(f"\n✗ Error creating tasks in Todoist: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
