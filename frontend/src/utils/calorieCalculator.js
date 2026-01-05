import { mealsAPI } from '../api/client';

// Cache for ingredient calories (loaded once and reused)
let caloriesCache = null;

/**
 * Load ingredient calories from backend
 * @returns {Promise<Object>} - Dictionary of ingredient name -> calories per 100g
 */
export async function loadIngredientCalories() {
  if (caloriesCache) {
    return caloriesCache;
  }

  try {
    const response = await mealsAPI.getCalories();
    caloriesCache = response.ingredient_calories || {};
    return caloriesCache;
  } catch (error) {
    console.error('Failed to load ingredient calories:', error);
    return {};
  }
}

/**
 * Calculate total calories for a meal
 * @param {Object} meal - Meal object from database
 * @param {Object} caloriesDict - Ingredient calories dictionary
 * @returns {Object} - { high_calorie: number, low_calorie: number }
 */
export function calculateMealCalories(meal, caloriesDict) {
  if (!meal || !meal.ingredients || !caloriesDict) {
    return { high_calorie: 0, low_calorie: 0 };
  }

  const baseServings = meal.base_servings || { high_calorie: 1, low_calorie: 1 };

  let highCalorieTotal = 0;
  let lowCalorieTotal = 0;

  meal.ingredients.forEach(ingredient => {
    const ingredientName = ingredient.name;
    const caloriesPer100g = caloriesDict[ingredientName] || 0;
    const quantity = ingredient.quantity || 0;

    // Base calories for this ingredient (per 1 serving)
    const baseCalories = (quantity / 100) * caloriesPer100g;

    // Check for ingredient-level base_servings override
    const highServings = ingredient.base_servings_override?.high_calorie ?? baseServings.high_calorie;
    const lowServings = ingredient.base_servings_override?.low_calorie ?? baseServings.low_calorie;

    // Calculate for each person type
    highCalorieTotal += baseCalories * highServings;
    lowCalorieTotal += baseCalories * lowServings;
  });

  return {
    high_calorie: Math.round(highCalorieTotal),
    low_calorie: Math.round(lowCalorieTotal)
  };
}

/**
 * Format calorie display
 * @param {number} highCal - Calories for high_calorie person
 * @param {number} lowCal - Calories for low_calorie person
 * @param {string} language - 'polish' or 'english'
 * @returns {string} - Formatted string like "~2850 kcal / ~1700 kcal"
 */
export function formatCalories(highCal, lowCal, language = 'polish') {
  return `~${highCal} kcal / ~${lowCal} kcal`;
}
