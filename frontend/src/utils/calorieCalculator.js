import { mealsAPI } from '../api/client';

// Cache for ingredient details (loaded once and reused)
let detailsCache = null;

/**
 * Load ingredient details from backend
 * @returns {Promise<Object>} - Dictionary of ingredient name -> {calories_per_100g, unit_size, adjustable}
 */
export async function loadIngredientDetails() {
  if (detailsCache) {
    return detailsCache;
  }

  try {
    const response = await mealsAPI.getIngredientDetails();
    detailsCache = response.ingredient_details || {};
    return detailsCache;
  } catch (error) {
    console.error('Failed to load ingredient details:', error);
    return {};
  }
}

/**
 * Legacy function for backward compatibility
 * @returns {Promise<Object>} - Dictionary of ingredient name -> calories per 100g
 */
export async function loadIngredientCalories() {
  const details = await loadIngredientDetails();
  const calories = {};
  for (const [name, data] of Object.entries(details)) {
    calories[name] = data.calories_per_100g;
  }
  return calories;
}

/**
 * Get unit size for an ingredient
 * @param {string} ingredientName - Name of the ingredient
 * @param {Object} ingredientDetails - Ingredient details dictionary
 * @returns {number|null} - Unit size in grams/ml, or null if not set
 */
export function getUnitSize(ingredientName, ingredientDetails) {
  return ingredientDetails[ingredientName]?.unit_size || null;
}

/**
 * Check if ingredient is adjustable
 * @param {string} ingredientName - Name of the ingredient
 * @param {Object} ingredientDetails - Ingredient details dictionary
 * @returns {boolean} - True if adjustable (default), false otherwise
 */
export function isAdjustable(ingredientName, ingredientDetails) {
  return ingredientDetails[ingredientName]?.adjustable !== false;
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
      const servings = baseServings[profile];
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
