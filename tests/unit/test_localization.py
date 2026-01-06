"""
Unit tests for localization module.
"""

import pytest

from recipier.localization import Localizer, Translations


@pytest.mark.unit
class TestLocalizer:
    """Tests for Localizer class."""

    def test_polish_localizer(self):
        """Test Polish localizer initialization."""
        loc = Localizer(language="polish")

        assert loc.language == "polish"
        assert loc.translations == Translations.POLISH

    def test_english_localizer(self):
        """Test English localizer initialization."""
        loc = Localizer(language="english")

        assert loc.language == "english"
        assert loc.translations == Translations.ENGLISH

    def test_invalid_language(self):
        """Test invalid language raises error."""
        with pytest.raises(ValueError, match="Unsupported language: spanish"):
            Localizer(language="spanish")

    def test_case_insensitive(self):
        """Test language parameter is case-insensitive."""
        loc1 = Localizer(language="POLISH")
        loc2 = Localizer(language="Polish")
        loc3 = Localizer(language="polish")

        assert loc1.language == "polish"
        assert loc2.language == "polish"
        assert loc3.language == "polish"

    def test_translate_simple_key(self):
        """Test translating simple key."""
        loc = Localizer(language="english")

        assert loc.t("app_title") == "🍳 Meal Plan Generator"

    def test_translate_with_formatting(self):
        """Test translating key with format arguments."""
        loc = Localizer(language="english")

        result = loc.t("meals_loaded", count=5)
        assert "5" in result
        assert "meals" in result

    def test_translate_missing_key(self):
        """Test translating missing key returns error message."""
        loc = Localizer(language="english")

        result = loc.t("nonexistent_key")
        assert "[Missing translation: nonexistent_key]" == result

    def test_meal_type_translation(self):
        """Test meal type translations."""
        loc_en = Localizer(language="english")
        loc_pl = Localizer(language="polish")

        assert loc_en.get_meal_type_translation("breakfast") == "Breakfast"
        assert loc_pl.get_meal_type_translation("breakfast") == "Śniadanie"

        assert loc_en.get_meal_type_translation("dinner") == "Dinner"
        assert loc_pl.get_meal_type_translation("dinner") == "Obiad"

    def test_polish_translations_complete(self):
        """Test Polish translations have all required keys."""
        required_keys = [
            "app_title",
            "meals_loaded",
            "shopping_task_title",
            "cooking_task_title",
            "eating_task_title",
            "breakfast",
            "dinner",
            "supper",
        ]

        for key in required_keys:
            assert key in Translations.POLISH, f"Missing key: {key}"

    def test_english_translations_complete(self):
        """Test English translations have all required keys."""
        required_keys = [
            "app_title",
            "meals_loaded",
            "shopping_task_title",
            "cooking_task_title",
            "eating_task_title",
            "breakfast",
            "dinner",
            "supper",
        ]

        for key in required_keys:
            assert key in Translations.ENGLISH, f"Missing key: {key}"

    def test_translations_parity(self):
        """Test Polish and English have same keys."""
        polish_keys = set(Translations.POLISH.keys())
        english_keys = set(Translations.ENGLISH.keys())

        missing_in_english = polish_keys - english_keys
        missing_in_polish = english_keys - polish_keys

        assert not missing_in_english, f"Keys missing in English: {missing_in_english}"
        assert not missing_in_polish, f"Keys missing in Polish: {missing_in_polish}"

    def test_format_placeholders_match(self):
        """Test that format placeholders match between languages."""
        import re

        # Get all keys
        keys = Translations.POLISH.keys()

        for key in keys:
            polish_text = Translations.POLISH[key]
            english_text = Translations.ENGLISH[key]

            # Extract placeholders {xxx}
            polish_placeholders = set(re.findall(r"\{(\w+)\}", polish_text))
            english_placeholders = set(re.findall(r"\{(\w+)\}", english_text))

            assert (
                polish_placeholders == english_placeholders
            ), f"Placeholder mismatch in '{key}': Polish {polish_placeholders} vs English {english_placeholders}"

    def test_special_characters_polish(self):
        """Test Polish translations contain proper special characters."""
        loc = Localizer(language="polish")

        # Polish should have special characters like ą, ć, ę, ł, ń, ó, ś, ź, ż
        breakfast = loc.t("breakfast")
        assert "Śniadanie" == breakfast  # Contains 'Ś'

    def test_emoji_in_translations(self):
        """Test translations with emoji formatting work correctly."""
        loc = Localizer(language="english")

        result = loc.t("shopping_task_title", emoji="🛒", meals="Spaghetti, Salad")
        assert "🛒" in result
        assert "Spaghetti, Salad" in result
