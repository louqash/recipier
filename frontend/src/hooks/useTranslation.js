/**
 * Translation hook
 * Provides easy access to translations based on current language
 */
import { useCallback } from 'react';
import { useMealPlan } from './useMealPlan';
import { getTranslation, getMealCountText, getShoppingCountText, getIngredientCountText } from '../localization/translations';

export function useTranslation() {
  const { language } = useMealPlan();

  /**
   * Get translation by key
   */
  const t = useCallback((key) => {
    return getTranslation(language, key);
  }, [language]);

  /**
   * Get meal count with proper plural form
   */
  const mealCount = useCallback((count) => {
    return getMealCountText(language, count);
  }, [language]);

  /**
   * Get shopping trip count with proper plural form
   */
  const shoppingCount = useCallback((count) => {
    return getShoppingCountText(language, count);
  }, [language]);

  /**
   * Get ingredient count with proper plural form
   */
  const ingredientCount = useCallback((count) => {
    return getIngredientCountText(language, count);
  }, [language]);

  return { t, mealCount, shoppingCount, ingredientCount, language };
}
