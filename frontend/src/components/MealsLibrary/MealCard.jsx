/**
 * MealCard - Draggable meal card component
 */
import { useTranslation } from '../../hooks/useTranslation';

export default function MealCard({ meal }) {
  const { t, ingredientCount } = useTranslation();
  const mealData = JSON.stringify({
    meal_id: meal.meal_id,
    meal_name: meal.name
  });

  return (
    <div
      className="meal-card select-none"
      data-meal-data={mealData}
    >
      {/* Meal Name */}
      <h3 className="font-semibold text-sm mb-2 text-gray-900">
        {meal.name}
      </h3>

      {/* Meal Details */}
      <div className="text-xs text-gray-600 space-y-1">
        {/* Ingredients Count */}
        <div className="text-gray-500">
          {ingredientCount(meal.ingredients.length)}
        </div>

        {/* Prep Indicator */}
        {meal.prep_tasks && meal.prep_tasks.length > 0 && (
          <div className="pt-1 text-orange-600 flex items-center gap-1">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{t('requires_prep')}</span>
          </div>
        )}
      </div>

      {/* Drag indicator */}
      <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-400 text-center">
        {t('drag_to_calendar')}
      </div>
    </div>
  );
}
