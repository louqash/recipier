/**
 * Translation hook
 * Provides easy access to translations based on current language
 */
import { useMealPlan } from './useMealPlan';
import { getTranslation, getMealCountText, getIngredientCountText } from '../localization/translations';

export function useTranslation() {
  const { language } = useMealPlan();

  /**
   * Get translation by key
   */
  const t = (key) => {
    return getTranslation(language, key);
  };

  /**
   * Get meal count with proper plural form
   */
  const mealCount = (count) => {
    return getMealCountText(language, count);
  };

  /**
   * Get ingredient count with proper plural form
   */
  const ingredientCount = (count) => {
    return getIngredientCountText(language, count);
  };

  return { t, mealCount, ingredientCount, language };
}
