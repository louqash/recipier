#!/usr/bin/env python3
"""
Interactive CLI tool for generating meal plans.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

import questionary
from questionary import Choice

from meal_planner import MealPlanner
from todoist_adapter import TodoistAdapter
from config import TaskConfig
from localization import get_localizer, Localizer


def validate_date(date_str: str) -> bool:
    """Validate date string in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def load_meals_database(db_path: str = "meals_database.json") -> Dict[str, Any]:
    """Load the meals database."""
    with open(db_path, 'r') as f:
        return json.load(f)


def select_meal(meals_db: Dict[str, Any], loc: Localizer) -> Dict[str, Any]:
    """Let user select a meal from the database with scrollable list."""
    meal_choices = [
        Choice(
            title=meal['name'],
            value=meal['meal_id']
        )
        for meal in meals_db['meals']
    ]

    meal_id = questionary.select(
        loc.t("select_meal"),
        choices=meal_choices,
        use_shortcuts=True,
        use_arrow_keys=True,
        style=questionary.Style([('answer', 'fg:green bold')])
    ).ask()

    # Find the meal by meal_id
    for meal in meals_db['meals']:
        if meal['meal_id'] == meal_id:
            return meal

    return None


def get_cooking_dates(loc: Localizer) -> List[str]:
    """Get cooking dates from user."""
    is_meal_prep = questionary.confirm(
        loc.t("is_meal_prep"),
        default=False
    ).ask()

    if is_meal_prep is None:
        return None

    if is_meal_prep:
        date_str = questionary.text(
            loc.t("cooking_date"),
            validate=lambda x: validate_date(x) or loc.t("invalid_date_format")
        ).ask()
        if date_str is None:
            return None
        return [date_str]
    else:
        dates = []
        num_dates = questionary.text(
            loc.t("how_many_cooking_dates"),
            validate=lambda x: x.isdigit() and int(x) > 0
        ).ask()

        if num_dates is None:
            return None

        for i in range(int(num_dates)):
            date_str = questionary.text(
                loc.t("cooking_date_number", number=i+1),
                validate=lambda x: validate_date(x) or loc.t("invalid_date_format")
            ).ask()
            if date_str is None:
                return None
            dates.append(date_str)

        return sorted(dates)


def get_servings_per_person(cooking_dates: List[str], loc: Localizer) -> Dict[str, int]:
    """Get servings per person."""
    servings = {}
    default_portions = str(len(cooking_dates))

    lukasz_servings = questionary.text(
        loc.t("servings_lukasz"),
        default=default_portions,
        validate=lambda x: x.isdigit() and int(x) >= 0
    ).ask()
    if lukasz_servings is None:
        return None
    servings['Lukasz'] = int(lukasz_servings)

    gaba_servings = questionary.text(
        loc.t("servings_gaba"),
        default=default_portions,
        validate=lambda x: x.isdigit() and int(x) >= 0
    ).ask()
    if gaba_servings is None:
        return None
    servings['Gaba'] = int(gaba_servings)

    return servings


def get_meal_type(loc: Localizer) -> str:
    """Get meal type."""
    return questionary.select(
        loc.t("meal_type_question"),
        choices=[
            Choice(loc.t("meal_type_breakfast"), "breakfast"),
            Choice(loc.t("meal_type_second_breakfast"), "second_breakfast"),
            Choice(loc.t("meal_type_dinner"), "dinner"),
            Choice(loc.t("meal_type_supper"), "supper")
        ]
    ).ask()


def get_assigned_cook(loc: Localizer) -> str:
    """Get assigned cook."""
    return questionary.select(
        loc.t("who_cooks"),
        choices=["Lukasz", "Gaba", "both"]
    ).ask()


def get_prep_assignee(assigned_cook: str, loc: Localizer) -> str:
    """Get prep assignee."""
    same_as_cook = questionary.confirm(
        loc.t("prep_same_as_cook", cook=assigned_cook),
        default=True
    ).ask()

    if same_as_cook:
        return assigned_cook

    return questionary.select(
        loc.t("who_does_prep"),
        choices=["Lukasz", "Gaba", "both"]
    ).ask()


def collect_meal_data(meals_db: Dict[str, Any], loc: Localizer) -> Dict[str, Any]:
    """Collect data for one meal."""
    print("\n" + "="*50)

    # Select meal
    meal = select_meal(meals_db, loc)
    if not meal:
        return None

    print(loc.t("selected_meal", name=meal['name']))

    # Get cooking dates
    cooking_dates = get_cooking_dates(loc)
    if cooking_dates is None:
        return None

    # Get servings
    servings = get_servings_per_person(cooking_dates, loc)
    if servings is None:
        return None

    # Get meal type
    meal_type = get_meal_type(loc)
    if meal_type is None:
        return None

    # Get assigned cook
    assigned_cook = get_assigned_cook(loc)
    if assigned_cook is None:
        return None

    # Check if meal has prep tasks
    has_prep = 'prep_tasks' in meal and len(meal.get('prep_tasks', [])) > 0
    prep_assigned_to = None

    if has_prep:
        print(loc.t("meal_has_prep_tasks", count=len(meal['prep_tasks'])))
        prep_assigned_to = get_prep_assignee(assigned_cook, loc)
        if prep_assigned_to is None:
            return None

    meal_data = {
        "meal_id": meal['meal_id'],
        "cooking_dates": cooking_dates,
        "meal_type": meal_type,
        "assigned_cook": assigned_cook,
        "servings_per_person": servings
    }

    if prep_assigned_to and prep_assigned_to != assigned_cook:
        meal_data["prep_assigned_to"] = prep_assigned_to

    return meal_data


def collect_shopping_trip(scheduled_meals: List[Dict[str, Any]], loc: Localizer) -> Dict[str, Any]:
    """Collect data for one shopping trip."""
    print("\n" + "="*50)

    # Show available meals
    meal_choices = [
        Choice(
            title=f"{meal['meal_id']} - {meal['cooking_dates'][0]}",
            value=meal['meal_id']
        )
        for meal in scheduled_meals
    ]

    selected_meal_ids = questionary.checkbox(
        loc.t("select_meals_for_shopping"),
        choices=meal_choices
    ).ask()

    if selected_meal_ids is None or not selected_meal_ids:
        return None

    # Get shopping date
    shopping_date = questionary.text(
        loc.t("shopping_date"),
        validate=lambda x: validate_date(x) or loc.t("invalid_date_format")
    ).ask()

    if shopping_date is None:
        return None

    return {
        "date": shopping_date,
        "meal_ids": selected_meal_ids
    }


def generate_filename(scheduled_meals: List[Dict[str, Any]]) -> str:
    """Generate filename based on earliest cooking date."""
    all_dates = []
    for meal in scheduled_meals:
        all_dates.extend(meal['cooking_dates'])

    if not all_dates:
        return f"meal_plan_{datetime.now().strftime('%Y-%m-%d')}.json"

    earliest_date = min(all_dates)
    return f"{earliest_date}.json"


def save_meal_plan(meal_plan: Dict[str, Any], output_dir: str = "data") -> str:
    """Save meal plan to JSON file."""
    os.makedirs(output_dir, exist_ok=True)

    filename = generate_filename(meal_plan['scheduled_meals'])
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(meal_plan, f, indent=2, ensure_ascii=False)

    return filepath


def main():
    """Main function."""
    # Initialize localization
    config = TaskConfig()
    loc = get_localizer(config.language)

    print(loc.t("app_title"))
    print("=" * 50)

    # Load meals database
    try:
        meals_db = load_meals_database()
        print(loc.t("meals_loaded", count=len(meals_db['meals'])))
    except FileNotFoundError:
        print(loc.t("error_database_not_found"))
        return
    except Exception as e:
        print(loc.t("error_loading_database", error=e))
        return

    # Collect meals
    num_meals = questionary.text(
        loc.t("how_many_meals"),
        validate=lambda x: x.isdigit() and int(x) > 0
    ).ask()

    if num_meals is None:
        print(loc.t("cancelled"))
        return

    scheduled_meals = []
    for i in range(int(num_meals)):
        print(loc.t("meal_number", current=i+1, total=num_meals))
        meal_data = collect_meal_data(meals_db, loc)
        if meal_data:
            scheduled_meals.append(meal_data)
        else:
            print(loc.t("cancelled_or_skipped"))

    if not scheduled_meals:
        print(loc.t("no_meals_added"))
        return

    # Collect shopping trips
    print("\n" + "="*50)
    num_trips = questionary.text(
        loc.t("how_many_shopping_trips"),
        default="1",
        validate=lambda x: x.isdigit() and int(x) > 0
    ).ask()

    if num_trips is None:
        print(loc.t("no_shopping_trips_warning"))
        num_trips = "0"

    shopping_trips = []
    for i in range(int(num_trips)):
        print(loc.t("shopping_trip_number", current=i+1, total=num_trips))
        trip_data = collect_shopping_trip(scheduled_meals, loc)
        if trip_data:
            shopping_trips.append(trip_data)
        else:
            print(loc.t("cancelled_or_skipped_shopping"))

    if not shopping_trips:
        print(loc.t("no_shopping_trips_added"))

    # Create meal plan
    meal_plan = {
        "scheduled_meals": scheduled_meals,
        "shopping_trips": shopping_trips
    }

    # Save to file
    try:
        filepath = save_meal_plan(meal_plan)
        print(loc.t("plan_saved", filepath=filepath))
    except Exception as e:
        print(loc.t("error_saving_file", error=e))
        return

    # Show summary
    print("\n" + "="*50)
    print(loc.t("summary_title"))
    print("="*50)
    print(loc.t("summary_meals", count=len(scheduled_meals)))
    print(loc.t("summary_shopping_trips", count=len(shopping_trips)))
    print(loc.t("summary_file", filepath=filepath))

    # Ask about Todoist
    add_to_todoist = questionary.confirm(
        loc.t("add_to_todoist_question"),
        default=False
    ).ask()

    if add_to_todoist is None:
        print(loc.t("done"))
        return

    if add_to_todoist:
        print(loc.t("creating_todoist_tasks"))

        # Get API token
        api_token = os.getenv('TODOIST_API_TOKEN')
        if not api_token:
            print(loc.t("error_no_api_token"))
            print(loc.t("error_api_token_instructions"))
            return

        try:
            # Load and expand meal plan
            planner = MealPlanner(config=config)

            expanded_plan = planner.expand_meal_plan(meal_plan, meals_db)

            # Generate tasks
            tasks = planner.generate_all_tasks(expanded_plan)

            # Create in Todoist
            adapter = TodoistAdapter(api_token, config=config)
            adapter.create_tasks(tasks)

            print(loc.t("tasks_created", count=len(tasks)))

        except Exception as e:
            import traceback
            print(loc.t("error_creating_tasks", error=e))
            print(loc.t("full_traceback"))
            traceback.print_exc()

    print(loc.t("done"))


if __name__ == "__main__":
    main()
