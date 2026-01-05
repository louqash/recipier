/**
 * MealCard - Draggable meal card component
 */
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme.jsx';
import { calculateMealCalories, formatCalories } from '../../utils/calorieCalculator';

export default function MealCard({ meal, caloriesDict }) {
  const { t, ingredientCount } = useTranslation();
  const { colors } = useTheme();
  const mealData = JSON.stringify({
    meal_id: meal.meal_id,
    meal_name: meal.name
  });

  // Calculate calories if dictionary is loaded
  const caloriesPerProfile = caloriesDict ? calculateMealCalories(meal, caloriesDict) : null;

  return (
    <div
      className="meal-card select-none p-3 rounded-lg cursor-move"
      data-meal-data={mealData}
      style={{
        backgroundColor: colors.surface0,
        border: `1px solid ${colors.surface1}`
      }}
    >
      {/* Meal Name */}
      <h3 className="font-semibold text-sm mb-2" style={{ color: colors.text }}>
        {meal.name}
      </h3>

      {/* Meal Details */}
      <div className="text-xs space-y-1" style={{ color: colors.subtext1 }}>
        {/* Ingredients Count */}
        <div style={{ color: colors.subtext0 }}>
          {ingredientCount(meal.ingredients.length)}
        </div>

        {/* Calories */}
        {caloriesPerProfile && Object.keys(caloriesPerProfile).length > 0 && (
          <div style={{ color: colors.subtext0 }}>
            {formatCalories(caloriesPerProfile).map((line, index) => (
              <div key={index}>{line}</div>
            ))}
          </div>
        )}

        {/* Prep Indicator */}
        {meal.prep_tasks && meal.prep_tasks.length > 0 && (
          <div className="pt-1 flex items-center gap-1" style={{ color: colors.peach }}>
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{t('requires_prep')}</span>
          </div>
        )}
      </div>

      {/* Drag indicator */}
      <div className="mt-2 pt-2 text-xs text-center" style={{
        borderTop: `1px solid ${colors.surface1}`,
        color: colors.overlay0
      }}>
        {t('drag_to_calendar')}
      </div>
    </div>
  );
}
