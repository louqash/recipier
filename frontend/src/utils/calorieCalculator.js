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
 * Get unit size for an ingredient (formatted for display)
 * @param {string} ingredientName - Name of the ingredient
 * @param {Object} ingredientDetails - Ingredient details dictionary
 * @returns {string|null} - Unit size formatted (e.g., "1 szt." or "56g"), or null if not set
 */
export function getUnitSize(ingredientName, ingredientDetails) {
  const details = ingredientDetails[ingredientName];
  if (!details?.unit_size) {
    return null;
  }

  // If ingredient has display_unit conversion (like eggs), show in display units
  if (details.display_unit && details.grams_per_unit) {
    const quantity = Math.round(details.unit_size / details.grams_per_unit);
    return `${quantity} ${details.display_unit}`;
  }

  // Otherwise show in grams
  return `${details.unit_size}g`;
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
 * Calculate meal calories for database meal preview (WITHOUT rounding)
 * This is a simple preview calculator for library cards only.
 * For scheduled meals with rounding, use backend API instead.
 *
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
 * Format calorie display for all diet profiles (simplified for preview)
 * @param {Object} caloriesPerProfile - Object with profile names as keys and calorie counts as values
 * @returns {Array<string>} - Array of formatted strings like ["high_calorie: ~2850 kcal", "low_calorie: ~1700 kcal"]
 */
export function formatCalories(caloriesPerProfile) {
  if (!caloriesPerProfile || Object.keys(caloriesPerProfile).length === 0) {
    return [];
  }

  return Object.entries(caloriesPerProfile)
    .map(([profile, calories]) => `${profile}: ~${calories} kcal`);
}

/**
 * Calculate meal nutrition (calories + macros) for database meal preview (WITHOUT rounding)
 * This is a simple preview calculator only. For scheduled meals with rounding, use backend API.
 *
 * @param {Object} meal - Meal object from database
 * @param {Object} ingredientDetails - Full ingredient details dictionary
 * @returns {Object} - Dynamic object with profile names as keys, each containing {calories, fat, protein, carbs}
 */
export function calculateMealNutrition(meal, ingredientDetails) {
  if (!meal || !meal.ingredients || !ingredientDetails) {
    return {};
  }

  const baseServings = meal.base_servings || {};
  const profileNames = Object.keys(baseServings);

  if (profileNames.length === 0) {
    return {};
  }

  // Initialize nutrition totals for each profile
  const nutrition = {};
  profileNames.forEach(profile => {
    nutrition[profile] = {
      calories: 0,
      fat: 0,
      protein: 0,
      carbs: 0
    };
  });

  // Calculate nutrition for each profile
  meal.ingredients.forEach(ingredient => {
    const ingredientName = ingredient.name;
    const details = ingredientDetails[ingredientName] || {};
    const quantity = ingredient.quantity || 0;

    const caloriesPer100g = details.calories_per_100g || 0;
    const fatPer100g = details.fat_per_100g || 0;
    const proteinPer100g = details.protein_per_100g || 0;
    const carbsPer100g = details.carbs_per_100g || 0;

    // Base nutrition for this ingredient (per 1 serving)
    const baseCalories = (quantity / 100) * caloriesPer100g;
    const baseFat = (quantity / 100) * fatPer100g;
    const baseProtein = (quantity / 100) * proteinPer100g;
    const baseCarbs = (quantity / 100) * carbsPer100g;

    // Add to each profile's total
    profileNames.forEach(profile => {
      const servings = baseServings[profile];
      nutrition[profile].calories += baseCalories * servings;
      nutrition[profile].fat += baseFat * servings;
      nutrition[profile].protein += baseProtein * servings;
      nutrition[profile].carbs += baseCarbs * servings;
    });
  });

  // Round all nutrition values
  const result = {};
  profileNames.forEach(profile => {
    result[profile] = {
      calories: Math.round(nutrition[profile].calories),
      fat: Math.round(nutrition[profile].fat * 10) / 10, // Round to 1 decimal
      protein: Math.round(nutrition[profile].protein * 10) / 10,
      carbs: Math.round(nutrition[profile].carbs * 10) / 10
    };
  });

  return result;
}

/**
 * Legacy function for loading ingredient calories (for preview calculations)
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
