"""
Localization support for Recipier.
Provides translations for CLI and Todoist text.
"""

from typing import Any, Dict


class Translations:
    """Translation strings for different languages."""

    POLISH = {
        # generate_meal_plan.py - Main UI
        "app_title": "🍳 Generator Planów Posiłków",
        "meals_loaded": "✓ Załadowano bazę {count} posiłków",
        "error_database_not_found": "✗ Błąd: Nie znaleziono pliku meals_database.json",
        "error_loading_database": "✗ Błąd wczytywania bazy danych: {error}",
        "how_many_meals": "\nIle posiłków chcesz zaplanować?",
        "cancelled": "\nAnulowano.",
        "meal_number": "\n📝 Posiłek {current}/{total}",
        "no_meals_added": "\n✗ Nie dodano żadnych posiłków!",
        "how_many_shopping_trips": "Ile wycieczek na zakupy?",
        "no_shopping_trips_warning": "\n⚠️  Nie dodano zakupów - kontynuowanie bez wycieczek na zakupy.",
        "shopping_trip_number": "\n🛒 Zakupy {current}/{total}",
        "no_shopping_trips_added": "\n⚠️  Nie dodano żadnych wycieczek na zakupy!",
        "plan_saved": "\n✓ Zapisano plan posiłków: {filepath}",
        "error_saving_file": "\n✗ Błąd zapisu pliku: {error}",
        "summary_title": "\n📊 PODSUMOWANIE",
        "summary_meals": "Posiłków: {count}",
        "summary_shopping_trips": "Wycieczek na zakupy: {count}",
        "summary_file": "Plik: {filepath}",
        "add_to_todoist_question": "\nCzy dodać zadania do Todoist?",
        "done": "\n✨ Gotowe!",
        "creating_todoist_tasks": "\n🚀 Tworzenie zadań w Todoist...",
        "error_no_api_token": "✗ Błąd: Nie ustawiono zmiennej TODOIST_API_TOKEN",
        "error_api_token_instructions": "Ustaw ją za pomocą: export TODOIST_API_TOKEN='your_token_here'",
        "tasks_created": "\n✅ Utworzono {count} zadań w Todoist!",
        "error_creating_tasks": "\n✗ Błąd przy tworzeniu zadań w Todoist: {error}",
        "full_traceback": "\nPełny traceback:",
        "cancelled_or_skipped": "Anulowano lub pominięto posiłek.",
        "cancelled_or_skipped_shopping": "Anulowano lub pominięto zakupy.",
        # generate_meal_plan.py - Meal data collection
        "select_meal": "Wybierz posiłek (strzałki ↑↓ aby przewijać, zacznij pisać aby filtrować):",
        "selected_meal": "\nWybrano: {name}",
        "is_meal_prep": "Czy to meal prep (gotowane raz na kilka dni)?",
        "cooking_date": "Podaj datę gotowania (YYYY-MM-DD):",
        "invalid_date_format": "Nieprawidłowy format daty (YYYY-MM-DD)",
        "how_many_cooking_dates": "Ile dat gotowania?",
        "cooking_date_number": "Podaj datę {number} (YYYY-MM-DD):",
        "servings_for_user": "Ile porcji dla {user}?",
        "meal_type_question": "Jaki typ posiłku?",
        "meal_type_breakfast": "Śniadanie",
        "meal_type_second_breakfast": "Drugie śniadanie",
        "meal_type_dinner": "Obiad",
        "meal_type_supper": "Kolacja",
        "who_cooks": "Kto gotuje?",
        "prep_same_as_cook": "Czy przygotowania robi {cook}?",
        "who_does_prep": "Kto robi przygotowania?",
        "meal_has_prep_tasks": "\n⚠️  Ten posiłek wymaga przygotowań ({count} zadań)",
        # generate_meal_plan.py - Shopping trip collection
        "select_meals_for_shopping": "Wybierz posiłki do zakupów:",
        "shopping_date": "Podaj datę zakupów (YYYY-MM-DD):",
        # meal_planner.py - Task generation
        "shopping_task_title": "{emoji}Zakupy na: {meals}",
        "shopping_task_description": "Lista zakupów",
        "prep_task_title": "{emoji}Przygotowania do {meal}",
        "prep_task_description": "{description}\n\nData gotowania: {date}",
        "cooking_task_title": "{emoji}Gotowanie: {meal}",
        "cooking_task_description_line1": "**{meal_type}** na {date}",
        "cooking_task_description_portions": "Porcje: {portions}",
        "cooking_task_description_calories": "Kalorie: {calories}",
        "cooking_task_description_session": "Sesja gotowania {current} z {total}",
        "portion_count": "{count} porcji",
        "portion_for_person": "Porcja dla {person}",
        "portion_singular": "porcja",
        "portion_plural": "porcje",
        # create_meal_tasks.py - CLI output
        "usage": "Usage: recipier <meal_plan.json> <meals_database.json> [--config config.json]",
        "error_arguments": "Error: meal_plan.json and meals_database.json are required",
        "error_meal_plan_not_found": "Error: Meal plan file not found: {path}",
        "error_database_not_found_create": "Error: Meals database file not found: {path}",
        "error_config_not_found": "Error: Config file not found: {path}",
        "creating_tasks": "Creating tasks in Todoist...",
        "tasks_created_count": "✓ Created {count} tasks",
        "task_created": "  ✓ {title}",
        # Meal types for Todoist
        "breakfast": "Śniadanie",
        "second_breakfast": "Drugie śniadanie",
        "dinner": "Obiad",
        "supper": "Kolacja",
        # Serving tasks (getting meal ready to eat after cooking)
        "eating_task_title": "{emoji}Podać: {meal}",
        "eating_task_description": "{meal}\nOsoby: {people}",
        "cooking_task_eating_today": "🍽️ Jedzenie dzisiaj: {people}",
        "cooking_task_meal_prep_note": "🥡 Meal prep - podanie w innych dniach",
        "cooking_steps_header": "📋 Kroki przygotowania:",
        "suggested_seasonings_label": "🧂 Sugerowane przyprawy",
        "seasoning_note": "sprawdź czy masz",
        # Rounding warnings
        "rounding_warning_header": "⚠️ Ostrzeżenia o zaokrągleniu:",
        "rounding_warning_item": "• {ingredient}: zmiana o {percent}% ({original}g → {rounded}g). Rozważ {portions} porcji.",
        # UI strings
        "eating_dates": "Daty spożycia",
        "add_eating_date": "Dodaj datę spożycia",
        "eating_dates_locked": "Zsynchronizowane",
        "eating_dates_unlocked": "Niezależne",
        # Validation errors
        "error_no_eating_dates": "Przynajmniej jedna osoba musi mieć daty spożycia",
        "error_person_no_eating_dates": "{person} musi mieć przynajmniej jedną datę spożycia",
        "error_eating_before_cooking": "{person}: data spożycia {eating_date} jest przed datą gotowania {cooking_date}",
        "error_eating_date_not_in_cooking": "{person}: data spożycia {eating_date} nie znajduje się w datach gotowania {cooking_dates}",
        "error_unknown_people": "Nieznane osoby w planie posiłków: {unknown_list}. Dostępne osoby: {available_list}",
        "error_meal_not_found": "Posiłek '{meal_id}' nie znaleziony w bazie danych",
        "error_no_cooking_dates": "Brak dat gotowania",
        "error_invalid_date_format": "Nieprawidłowy format daty, oczekiwano RRRR-MM-DD",
        "error_scheduled_meal_not_found": "ID zaplanowanego posiłku '{scheduled_meal_id}' nie znalezione w planie",
        # Todoist sections
        "section_shopping": "Zakupy",
        "section_prep": "Przygotowania",
        "section_cooking": "Gotowanie",
        "section_eating": "Podawanie",
        # Category labels for shopping
        "category_produce": "warzywa-owoce",
        "category_meat": "mięso",
        "category_dairy": "nabiał",
        "category_pantry": "spiżarnia",
        "category_frozen": "mrożonki",
        "category_bakery": "pieczywo",
        "category_beverages": "napoje",
        "category_spices": "przyprawy",
        "category_other": "inne",
    }

    ENGLISH = {
        # generate_meal_plan.py - Main UI
        "app_title": "🍳 Meal Plan Generator",
        "meals_loaded": "✓ Loaded database with {count} meals",
        "error_database_not_found": "✗ Error: meals_database.json file not found",
        "error_loading_database": "✗ Error loading database: {error}",
        "how_many_meals": "\nHow many meals do you want to plan?",
        "cancelled": "\nCancelled.",
        "meal_number": "\n📝 Meal {current}/{total}",
        "no_meals_added": "\n✗ No meals added!",
        "how_many_shopping_trips": "How many shopping trips?",
        "no_shopping_trips_warning": "\n⚠️  No shopping trips added - continuing without shopping trips.",
        "shopping_trip_number": "\n🛒 Shopping trip {current}/{total}",
        "no_shopping_trips_added": "\n⚠️  No shopping trips added!",
        "plan_saved": "\n✓ Meal plan saved: {filepath}",
        "error_saving_file": "\n✗ Error saving file: {error}",
        "summary_title": "\n📊 SUMMARY",
        "summary_meals": "Meals: {count}",
        "summary_shopping_trips": "Shopping trips: {count}",
        "summary_file": "File: {filepath}",
        "add_to_todoist_question": "\nAdd tasks to Todoist?",
        "done": "\n✨ Done!",
        "creating_todoist_tasks": "\n🚀 Creating tasks in Todoist...",
        "error_no_api_token": "✗ Error: TODOIST_API_TOKEN environment variable not set",
        "error_api_token_instructions": "Set it with: export TODOIST_API_TOKEN='your_token_here'",
        "tasks_created": "\n✅ Created {count} tasks in Todoist!",
        "error_creating_tasks": "\n✗ Error creating Todoist tasks: {error}",
        "full_traceback": "\nFull traceback:",
        "cancelled_or_skipped": "Cancelled or skipped meal.",
        "cancelled_or_skipped_shopping": "Cancelled or skipped shopping trip.",
        # generate_meal_plan.py - Meal data collection
        "select_meal": "Select a meal (↑↓ arrows to scroll, start typing to filter):",
        "selected_meal": "\nSelected: {name}",
        "is_meal_prep": "Is this meal prep (cooked once for multiple days)?",
        "cooking_date": "Enter cooking date (YYYY-MM-DD):",
        "invalid_date_format": "Invalid date format (YYYY-MM-DD)",
        "how_many_cooking_dates": "How many cooking dates?",
        "cooking_date_number": "Enter date {number} (YYYY-MM-DD):",
        "servings_for_user": "How many servings for {user}?",
        "meal_type_question": "What type of meal?",
        "meal_type_breakfast": "Breakfast",
        "meal_type_second_breakfast": "2nd Breakfast",
        "meal_type_dinner": "Dinner",
        "meal_type_supper": "Supper",
        "who_cooks": "Who cooks?",
        "prep_same_as_cook": "Does {cook} do the prep?",
        "who_does_prep": "Who does the prep?",
        "meal_has_prep_tasks": "\n⚠️  This meal requires prep ({count} tasks)",
        # generate_meal_plan.py - Shopping trip collection
        "select_meals_for_shopping": "Select meals for shopping:",
        "shopping_date": "Enter shopping date (YYYY-MM-DD):",
        # meal_planner.py - Task generation
        "shopping_task_title": "{emoji}Shopping for: {meals}",
        "shopping_task_description": "Shopping list",
        "prep_task_title": "{emoji}Prep for {meal}",
        "prep_task_description": "{description}\n\nCooking date: {date}",
        "cooking_task_title": "{emoji}Cook: {meal}",
        "cooking_task_description_line1": "**{meal_type}** for {date}",
        "cooking_task_description_portions": "Portions: {portions}",
        "cooking_task_description_calories": "Calories: {calories}",
        "cooking_task_description_session": "Cooking session {current} of {total}",
        "portion_count": "{count} portion" if "{count}" == "1" else "{count} portions",
        "portion_for_person": "Portion for {person}",
        "portion_singular": "portion",
        "portion_plural": "portions",
        # create_meal_tasks.py - CLI output
        "usage": "Usage: recipier <meal_plan.json> <meals_database.json> [--config config.json]",
        "error_arguments": "Error: meal_plan.json and meals_database.json are required",
        "error_meal_plan_not_found": "Error: Meal plan file not found: {path}",
        "error_database_not_found_create": "Error: Meals database file not found: {path}",
        "error_config_not_found": "Error: Config file not found: {path}",
        "creating_tasks": "Creating tasks in Todoist...",
        "tasks_created_count": "✓ Created {count} tasks",
        "task_created": "  ✓ {title}",
        # Meal types for Todoist
        "breakfast": "Breakfast",
        "second_breakfast": "2nd Breakfast",
        "dinner": "Dinner",
        "supper": "Supper",
        # Serving tasks (getting meal ready to eat after cooking)
        "eating_task_title": "{emoji}Serve: {meal}",
        "eating_task_description": "{meal}\nPeople: {people}",
        "cooking_task_eating_today": "🍽️ Eating today: {people}",
        "cooking_task_meal_prep_note": "🥡 Meal prep - serving on other days",
        "cooking_steps_header": "📋 Cooking Steps:",
        "suggested_seasonings_label": "🧂 Suggested Seasonings",
        "seasoning_note": "check if you have",
        # Rounding warnings
        "rounding_warning_header": "⚠️ Rounding Warnings:",
        "rounding_warning_item": "• {ingredient}: {percent}% change ({original}g → {rounded}g). Consider {portions} portions.",
        # UI strings
        "eating_dates": "Eating Dates",
        "add_eating_date": "Add eating date",
        "eating_dates_locked": "Synced",
        "eating_dates_unlocked": "Independent",
        # Validation errors
        "error_no_eating_dates": "At least one person must have eating dates",
        "error_person_no_eating_dates": "{person} must have at least 1 eating date",
        "error_eating_before_cooking": "{person}: eating date {eating_date} is before cooking date {cooking_date}",
        "error_eating_date_not_in_cooking": "{person}: eating date {eating_date} is not in cooking dates {cooking_dates}",
        "error_unknown_people": "Unknown people in meal plan: {unknown_list}. Available people: {available_list}",
        "error_meal_not_found": "Meal '{meal_id}' not found in database",
        "error_no_cooking_dates": "No cooking dates specified",
        "error_invalid_date_format": "Invalid date format, expected YYYY-MM-DD",
        "error_scheduled_meal_not_found": "Scheduled meal ID '{scheduled_meal_id}' not found in meal plan",
        # Todoist sections
        "section_shopping": "Shopping",
        "section_prep": "Prep",
        "section_cooking": "Cooking",
        "section_eating": "Serving",
        # Category labels for shopping
        "category_produce": "produce",
        "category_meat": "meat",
        "category_dairy": "dairy",
        "category_pantry": "pantry",
        "category_frozen": "frozen",
        "category_bakery": "bakery",
        "category_beverages": "beverages",
        "category_spices": "spices",
        "category_other": "other",
    }


class Localizer:
    """Handles translation lookups."""

    def __init__(self, language: str = "polish"):
        """Initialize with a language.

        Args:
            language: "polish" or "english"
        """
        self.language = language.lower()
        if self.language == "polish":
            self.translations = Translations.POLISH
        elif self.language == "english":
            self.translations = Translations.ENGLISH
        else:
            raise ValueError(f"Unsupported language: {language}. Use 'polish' or 'english'.")

    def t(self, key: str, **kwargs) -> str:
        """Get translated string with optional formatting.

        Args:
            key: Translation key
            **kwargs: Format arguments for the string

        Returns:
            Translated and formatted string
        """
        template = self.translations.get(key, f"[Missing translation: {key}]")
        if kwargs:
            return template.format(**kwargs)
        return template

    def get_meal_type_translation(self, meal_type: str) -> str:
        """Get translation for meal type."""
        return self.t(meal_type)

    def get_category_label(self, category: str) -> str:
        """Get localized label for a category.

        Args:
            category: Category name (e.g., "produce", "meat", "dairy")

        Returns:
            Localized category label
        """
        return self.t(f"category_{category}")

    def get_section_name(self, section_type: str) -> str:
        """Get localized section name.

        Args:
            section_type: Section type (e.g., "shopping", "prep", "cooking", "eating")

        Returns:
            Localized section name
        """
        return self.t(f"section_{section_type}")


# Convenience function for creating a localizer
def get_localizer(language: str = "polish") -> Localizer:
    """Create a Localizer instance.

    Args:
        language: "polish" or "english"

    Returns:
        Localizer instance
    """
    return Localizer(language)
