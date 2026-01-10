/**
 * Convert ingredient quantity to display format
 * Handles special cases like eggs (display in pieces instead of grams)
 *
 * @param {string} ingredientName - Name of the ingredient
 * @param {number} quantityInGrams - Quantity in grams
 * @param {string} unit - Original unit (usually "g" or "ml")
 * @param {Object} ingredientDetails - ingredient_details from database
 * @returns {Object} { quantity: number, unit: string }
 */
export function convertIngredientForDisplay(ingredientName, quantityInGrams, unit, ingredientDetails) {
  // Check if ingredient has display_unit conversion
  const details = ingredientDetails?.[ingredientName];

  if (details?.display_unit && details?.grams_per_unit && unit === 'g') {
    // Convert grams to units (e.g., 112g / 56g per egg = 2 eggs)
    const quantity = Math.round(quantityInGrams / details.grams_per_unit);
    return {
      quantity,
      unit: details.display_unit
    };
  }

  // Return original quantity and unit
  return {
    quantity: quantityInGrams,
    unit
  };
}

/**
 * Format ingredient quantity with unit for display
 *
 * @param {string} ingredientName - Name of the ingredient
 * @param {number} quantityInGrams - Quantity in grams
 * @param {string} unit - Original unit
 * @param {Object} ingredientDetails - ingredient_details from database
 * @returns {string} Formatted string like "2 szt." or "100g"
 */
export function formatIngredientQuantity(ingredientName, quantityInGrams, unit, ingredientDetails) {
  const { quantity, unit: displayUnit } = convertIngredientForDisplay(
    ingredientName,
    quantityInGrams,
    unit,
    ingredientDetails
  );

  return `${quantity}${displayUnit}`;
}
