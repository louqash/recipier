"""
Utility module for ingredient rounding warnings.

This module contains logic for detecting when ingredient quantities
will be significantly rounded due to package size constraints and
generating helpful warnings with suggestions for reducing the impact.
"""

from typing import Any, Dict, Optional


def generate_rounding_warning(
    ingredient_name: str, original_total: float, rounded_total: float, unit_size: float, meal_plan: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Generate warning if ingredient change exceeds 50% at meal plan level.

    Args:
        ingredient_name: Name of the ingredient being rounded
        original_total: Original total quantity across all meals
        rounded_total: Rounded quantity (multiple of unit_size)
        unit_size: Package/unit size in grams/ml
        meal_plan: Expanded meal plan with meals and per_person data

    Returns:
        Warning dict with ingredient_name, original_quantity, rounded_quantity,
        percent_change, suggested_portions, and meals info, or None if change
        is acceptable (<50%).

    The warning includes:
    - Overall percent change and quantities
    - Suggested meal plan multiplier to reduce rounding impact
    - List of meals using this ingredient with:
        - Meal name
        - Current portion count
        - Suggested additional portions for that specific meal
    """
    if original_total == 0:
        return None

    change_ratio = abs(rounded_total - original_total) / original_total

    if change_ratio > 0.5:
        # Find which meals use this ingredient
        meal_info = []
        meal_quantities = []  # Store (meal_name, current_portions, qty_per_portion) for later calculations

        for meal in meal_plan["meals"]:
            # Check if this meal contains the ingredient
            has_ingredient = any(ing["name"] == ingredient_name for ing in meal["ingredients"])
            if has_ingredient:
                # Calculate current portions (sum of eating dates across all people)
                eating_dates_per_person = meal.get("eating_dates_per_person", {})
                current_portions = sum(len(dates) for dates in eating_dates_per_person.values())

                # Get ingredient quantity for this meal
                meal_ingredient = next((ing for ing in meal["ingredients"] if ing["name"] == ingredient_name), None)
                if meal_ingredient:
                    meal_qty = meal_ingredient["quantity"]
                    qty_per_portion = meal_qty / current_portions if current_portions > 0 else meal_qty

                    meal_quantities.append(
                        {
                            "meal_name": meal["name"],
                            "current_portions": current_portions,
                            "qty_per_portion": qty_per_portion,
                            "total_qty": meal_qty,
                        }
                    )

                    # Calculate suggested additional portions for this specific meal alone
                    suggested_additional = 0
                    for add_portions in range(1, 10):
                        test_total = (current_portions + add_portions) * qty_per_portion
                        test_rounded = round(test_total / unit_size) * unit_size
                        if abs(test_rounded - test_total) / test_total <= 0.3:  # Less strict for individual meals
                            suggested_additional = add_portions
                            break

                    meal_info.append(
                        {
                            "meal_name": meal["name"],
                            "current_portions": current_portions,
                            "suggested_additional_portions": suggested_additional,
                        }
                    )

        # Calculate combined increase option (increase all meals by same amount)
        # Only suggest up to 5 additional portions per meal as practical limit
        combined_increase = 0
        if len(meal_quantities) > 1:
            # Find the minimum increase needed when all meals increase together
            for add_portions in range(1, 6):  # Max 5 additional portions
                # Calculate new total if we add portions to all meals
                new_total = sum(
                    (mq["current_portions"] + add_portions) * mq["qty_per_portion"] for mq in meal_quantities
                )
                new_rounded = round(new_total / unit_size) * unit_size
                if abs(new_rounded - new_total) / new_total <= 0.5:
                    combined_increase = add_portions
                    break

        # Filter meal_info to only show practical suggestions (≤5 portions)
        practical_meal_info = []
        for meal in meal_info:
            if meal["suggested_additional_portions"] > 0 and meal["suggested_additional_portions"] <= 5:
                practical_meal_info.append(meal)
            elif meal["suggested_additional_portions"] == 0:
                # Include meals with no practical solution
                practical_meal_info.append(meal)

        return {
            "ingredient_name": ingredient_name,
            "original_quantity": original_total,
            "rounded_quantity": rounded_total,
            "percent_change": change_ratio,
            "meals": practical_meal_info,
            "combined_increase": combined_increase,
            "unit_size": unit_size,
        }

    return None
