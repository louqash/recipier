#!/usr/bin/env python3
"""
Interactive CLI tool for generating meal plans.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import questionary
from questionary import Choice

from recipier.config import TaskConfig
from recipier.localization import Localizer, get_localizer
from recipier.meal_planner import MealPlanner
from recipier.todoist_adapter import TodoistAdapter


def validate_date(date_str: str) -> bool:
    """Validate date string in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def load_meals_database(db_path: str = "meals_database.json") -> Dict[str, Any]:
    """Load the meals database."""
    with open(db_path, "r") as f:
        return json.load(f)


def select_meal(meals_db: Dict[str, Any], loc: Localizer) -> Dict[str, Any]:
    """Let user select a meal from the database with scrollable list."""
    meal_choices = [Choice(title=meal["name"], value=meal["meal_id"]) for meal in meals_db["meals"]]

    meal_id = questionary.select(
        loc.t("select_meal"),
        choices=meal_choices,
        use_shortcuts=True,
        use_arrow_keys=True,
        style=questionary.Style([("answer", "fg:green bold")]),
    ).ask()

    # Find the meal by meal_id
    for meal in meals_db["meals"]:
        if meal["meal_id"] == meal_id:
            return meal

    return None


def get_cooking_dates(loc: Localizer) -> List[str]:
    """Get cooking dates from user."""
    is_meal_prep = questionary.confirm(loc.t("is_meal_prep"), default=False).ask()

    if is_meal_prep is None:
        return None

    if is_meal_prep:
        date_str = questionary.text(
            loc.t("cooking_date"),
            validate=lambda x: validate_date(x) or loc.t("invalid_date_format"),
        ).ask()
        if date_str is None:
            return None
        return [date_str]
    else:
        dates = []
        num_dates = questionary.text(
            loc.t("how_many_cooking_dates"), validate=lambda x: x.isdigit() and int(x) > 0
        ).ask()

        if num_dates is None:
            return None

        for i in range(int(num_dates)):
            date_str = questionary.text(
                loc.t("cooking_date_number", number=i + 1),
                validate=lambda x: validate_date(x) or loc.t("invalid_date_format"),
            ).ask()
            if date_str is None:
                return None
            dates.append(date_str)

        return sorted(dates)


def get_eating_dates_per_person(cooking_dates: List[str], config: TaskConfig, loc: Localizer) -> Dict[str, List[str]]:
    """Get eating dates per person from config users."""
    eating_dates = {}

    # Get users from config
    users = list(config.diet_profiles.keys())

    if not users:
        print("⚠️  No users found in config. Using default user.")
        users = ["User"]

    # Default: people eat on first cooking date
    first_cooking_date = cooking_dates[0] if cooking_dates else None
    previous_user_dates = None

    for user_idx, user in enumerate(users):
        print(f"\n{user}'s eating dates:")

        # Ask if they want to copy from previous user
        if previous_user_dates and user_idx > 0:
            copy_dates = questionary.confirm(
                f"Use same dates as previous person? ({', '.join(previous_user_dates)})",
                default=True,
            ).ask()

            if copy_dates is None:  # User cancelled
                return None

            if copy_dates:
                eating_dates[user] = previous_user_dates.copy()
                continue

        user_dates = []

        # Ask for number of eating dates
        num_dates_str = questionary.text(
            f"How many times will {user} eat this meal?",
            default=str(len(cooking_dates)),
            validate=lambda x: x.isdigit() and int(x) > 0,
        ).ask()

        if num_dates_str is None:  # User cancelled
            return None

        num_dates = int(num_dates_str)

        # Collect eating dates with auto-increment
        for i in range(num_dates):
            # Smart default: first date uses cooking date, subsequent dates increment
            if i == 0:
                default_date = cooking_dates[0] if cooking_dates else first_cooking_date
            else:
                # Increment from previous eating date
                from datetime import datetime, timedelta

                prev_date = datetime.strptime(user_dates[i - 1], "%Y-%m-%d")
                next_date = prev_date + timedelta(days=1)
                default_date = next_date.strftime("%Y-%m-%d")

            date_str = questionary.text(
                f"  Eating date {i+1}/{num_dates} (YYYY-MM-DD):",
                default=default_date,
                validate=validate_date,
            ).ask()

            if date_str is None:  # User cancelled
                return None

            user_dates.append(date_str)

        eating_dates[user] = sorted(user_dates)
        previous_user_dates = eating_dates[user]

    return eating_dates


def get_meal_type(loc: Localizer) -> str:
    """Get meal type."""
    return questionary.select(
        loc.t("meal_type_question"),
        choices=[
            Choice(loc.t("meal_type_breakfast"), "breakfast"),
            Choice(loc.t("meal_type_second_breakfast"), "second_breakfast"),
            Choice(loc.t("meal_type_dinner"), "dinner"),
            Choice(loc.t("meal_type_supper"), "supper"),
        ],
    ).ask()


def get_assigned_cook(config: TaskConfig, loc: Localizer) -> str:
    """Get assigned cook from config users."""
    users = list(config.diet_profiles.keys())
    choices = users + ["both"]

    return questionary.select(loc.t("who_cooks"), choices=choices).ask()


def get_prep_assignee(assigned_cook: str, config: TaskConfig, loc: Localizer) -> str:
    """Get prep assignee from config users."""
    same_as_cook = questionary.confirm(loc.t("prep_same_as_cook", cook=assigned_cook), default=True).ask()

    if same_as_cook:
        return assigned_cook

    users = list(config.diet_profiles.keys())
    choices = users + ["both"]

    return questionary.select(loc.t("who_does_prep"), choices=choices).ask()


def collect_meal_data(meals_db: Dict[str, Any], config: TaskConfig, loc: Localizer) -> Dict[str, Any]:
    """Collect data for one meal."""
    print("\n" + "=" * 50)

    # Select meal
    meal = select_meal(meals_db, loc)
    if not meal:
        return None

    print(loc.t("selected_meal", name=meal["name"]))

    # Get cooking dates
    cooking_dates = get_cooking_dates(loc)
    if cooking_dates is None:
        return None

    # Get eating dates
    eating_dates = get_eating_dates_per_person(cooking_dates, config, loc)
    if eating_dates is None:
        return None

    # Get meal type
    meal_type = get_meal_type(loc)
    if meal_type is None:
        return None

    # Get assigned cook
    assigned_cook = get_assigned_cook(config, loc)
    if assigned_cook is None:
        return None

    # Check if meal has prep tasks
    has_prep = "prep_tasks" in meal and len(meal.get("prep_tasks", [])) > 0
    prep_assigned_to = None

    if has_prep:
        print(loc.t("meal_has_prep_tasks", count=len(meal["prep_tasks"])))
        prep_assigned_to = get_prep_assignee(assigned_cook, config, loc)
        if prep_assigned_to is None:
            return None

    # Generate unique ID for this scheduled meal instance
    import time

    meal_id_timestamp = int(time.time() * 1000)  # milliseconds

    meal_data = {
        "id": f"sm_{meal_id_timestamp}",
        "meal_id": meal["meal_id"],
        "cooking_dates": cooking_dates,
        "eating_dates_per_person": eating_dates,
        "meal_type": meal_type,
        "assigned_cook": assigned_cook,
    }

    if prep_assigned_to and prep_assigned_to != assigned_cook:
        meal_data["prep_assigned_to"] = prep_assigned_to

    return meal_data


def collect_shopping_trip(scheduled_meals: List[Dict[str, Any]], loc: Localizer) -> Dict[str, Any]:
    """Collect data for one shopping trip."""
    print("\n" + "=" * 50)

    # Show available meals with their unique IDs
    meal_choices = [
        Choice(
            title=f"{meal['meal_id']} - {meal['cooking_dates'][0]} (ID: {meal['id']})",
            value=meal["id"],  # Use unique scheduled meal ID
        )
        for meal in scheduled_meals
    ]

    selected_meal_ids = questionary.checkbox(loc.t("select_meals_for_shopping"), choices=meal_choices).ask()

    if selected_meal_ids is None or not selected_meal_ids:
        return None

    # Get shopping date
    shopping_date = questionary.text(
        loc.t("shopping_date"), validate=lambda x: validate_date(x) or loc.t("invalid_date_format")
    ).ask()

    if shopping_date is None:
        return None

    return {"shopping_date": shopping_date, "scheduled_meal_ids": selected_meal_ids}


def generate_filename(scheduled_meals: List[Dict[str, Any]]) -> str:
    """Generate filename based on earliest cooking date."""
    all_dates = []
    for meal in scheduled_meals:
        all_dates.extend(meal["cooking_dates"])

    if not all_dates:
        return f"meal_plan_{datetime.now().strftime('%Y-%m-%d')}.json"

    earliest_date = min(all_dates)
    return f"{earliest_date}.json"


def save_meal_plan(meal_plan: Dict[str, Any], output_dir: str = "data") -> str:
    """Save meal plan to JSON file."""
    os.makedirs(output_dir, exist_ok=True)

    filename = generate_filename(meal_plan["scheduled_meals"])
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(meal_plan, f, indent=2, ensure_ascii=False)

    return filepath


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive meal plan generator")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration JSON file (default: my_config.json if exists, otherwise defaults)",
        default=None,
    )
    args = parser.parse_args()

    # Load configuration
    config_path = args.config or "my_config.json"
    if os.path.exists(config_path):
        config = TaskConfig.from_file(config_path)
    else:
        config = TaskConfig()

    loc = get_localizer(config.language)

    print(loc.t("app_title"))
    print("=" * 50)

    # Load meals database
    try:
        meals_db = load_meals_database()
        print(loc.t("meals_loaded", count=len(meals_db["meals"])))
    except FileNotFoundError:
        print(loc.t("error_database_not_found"))
        return
    except Exception as e:
        print(loc.t("error_loading_database", error=e))
        return

    # Collect meals
    num_meals = questionary.text(loc.t("how_many_meals"), validate=lambda x: x.isdigit() and int(x) > 0).ask()

    if num_meals is None:
        print(loc.t("cancelled"))
        return

    scheduled_meals = []
    for i in range(int(num_meals)):
        print(loc.t("meal_number", current=i + 1, total=num_meals))
        meal_data = collect_meal_data(meals_db, config, loc)
        if meal_data:
            scheduled_meals.append(meal_data)
        else:
            print(loc.t("cancelled_or_skipped"))

    if not scheduled_meals:
        print(loc.t("no_meals_added"))
        return

    # Collect shopping trips
    print("\n" + "=" * 50)
    num_trips = questionary.text(
        loc.t("how_many_shopping_trips"), default="1", validate=lambda x: x.isdigit() and int(x) > 0
    ).ask()

    if num_trips is None:
        print(loc.t("no_shopping_trips_warning"))
        num_trips = "0"

    shopping_trips = []
    for i in range(int(num_trips)):
        print(loc.t("shopping_trip_number", current=i + 1, total=num_trips))
        trip_data = collect_shopping_trip(scheduled_meals, loc)
        if trip_data:
            shopping_trips.append(trip_data)
        else:
            print(loc.t("cancelled_or_skipped_shopping"))

    if not shopping_trips:
        print(loc.t("no_shopping_trips_added"))

    # Create meal plan
    meal_plan = {"scheduled_meals": scheduled_meals, "shopping_trips": shopping_trips}

    # Save to file
    try:
        filepath = save_meal_plan(meal_plan)
        print(loc.t("plan_saved", filepath=filepath))
    except Exception as e:
        print(loc.t("error_saving_file", error=e))
        return

    # Show summary
    print("\n" + "=" * 50)
    print(loc.t("summary_title"))
    print("=" * 50)
    print(loc.t("summary_meals", count=len(scheduled_meals)))
    print(loc.t("summary_shopping_trips", count=len(shopping_trips)))
    print(loc.t("summary_file", filepath=filepath))

    # Ask about Todoist
    add_to_todoist = questionary.confirm(loc.t("add_to_todoist_question"), default=False).ask()

    if add_to_todoist is None:
        print(loc.t("done"))
        return

    if add_to_todoist:
        print(loc.t("creating_todoist_tasks"))

        # Get API token
        api_token = os.getenv("TODOIST_API_TOKEN")
        if not api_token:
            print(loc.t("error_no_api_token"))
            print(loc.t("error_api_token_instructions"))
            return

        try:
            # Load and expand meal plan
            planner = MealPlanner(config=config, meals_db=meals_db)

            expanded_plan = planner.expand_meal_plan(meal_plan)

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
