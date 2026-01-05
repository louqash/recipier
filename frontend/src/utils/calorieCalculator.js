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
 * Calculate total calories for a meal for all diet profiles
 * @param {Object} meal - Meal object from database
 * @param {Object} caloriesDict - Ingredient calories dictionary
 * @returns {Object} - Dynamic object with profile names as keys, e.g., { "high_calorie": 2850, "low_calorie": 1700 }
 */
export function calculateMealCalories(meal, caloriesDict) {
  if (!meal || !meal.ingredients || !caloriesDict) {
    return {};
  }

  const baseServings = meal.base_servings || {};
  const profileNames = Object.keys(baseServings);

  if (profileNames.length === 0) {
    return {};
  }

  // Initialize totals for each profile
  const totals = {};
  profileNames.forEach(profile => {
    totals[profile] = 0;
  });

  // Calculate calories for each profile
  meal.ingredients.forEach(ingredient => {
    const ingredientName = ingredient.name;
    const caloriesPer100g = caloriesDict[ingredientName] || 0;
    const quantity = ingredient.quantity || 0;

    // Base calories for this ingredient (per 1 serving)
    const baseCalories = (quantity / 100) * caloriesPer100g;

    // Add to each profile's total
    profileNames.forEach(profile => {
      // Check for ingredient-level override, otherwise use meal-level base_servings
      const servings = ingredient.base_servings_override?.[profile] ?? baseServings[profile];
      totals[profile] += baseCalories * servings;
    });
  });

  // Round all totals
  const result = {};
  profileNames.forEach(profile => {
    result[profile] = Math.round(totals[profile]);
  });

  return result;
}

/**
 * Format calorie display for all diet profiles as an array (for multi-line display)
 * @param {Object} caloriesPerProfile - Object with profile names as keys and calorie counts as values
 *                                      e.g., { "high_calorie": 2850, "low_calorie": 1700 }
 *                                      or { "weekend": 3000, "weekday": 2000, "cutting": 1500 }
 * @returns {Array<string>} - Array of formatted strings like ["high_calorie: ~2850 kcal", "low_calorie: ~1700 kcal"]
 */
export function formatCalories(caloriesPerProfile) {
  if (!caloriesPerProfile || Object.keys(caloriesPerProfile).length === 0) {
    return [];
  }

  return Object.entries(caloriesPerProfile)
    .map(([profile, calories]) => `${profile}: ~${calories} kcal`);
}
