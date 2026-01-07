/**
 * MealDetailsModal - Displays full meal information
 * Shows ingredients, calories, seasonings, and cooking steps
 */
import { useEffect } from 'react';
import { useTheme } from '../../hooks/useTheme';
import { useTranslation } from '../../hooks/useTranslation';
import { useMeals } from '../../hooks/useMeals';
import { calculateMealCalories } from '../../utils/calorieCalculator';

export default function MealDetailsModal({ isOpen, onClose, mealId, caloriesDict }) {
  const { colors } = useTheme();
  const { t } = useTranslation();
  const { meals, loading } = useMeals('');

  // Get the meal data
  const meal = meals?.find(m => m.meal_id === mealId);

  // Close modal on ESC key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEsc);
      return () => window.removeEventListener('keydown', handleEsc);
    }
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;
  if (loading) return null;
  if (!meal) return null;

  // Calculate calories per diet profile
  const calories = caloriesDict ? calculateMealCalories(meal, caloriesDict) : {};

  // Get diet profiles from base_servings
  const dietProfiles = meal.base_servings ? Object.keys(meal.base_servings) : [];

  // Group ingredients by category and calculate quantities per profile
  const ingredientsByCategory = {};
  meal.ingredients?.forEach(ingredient => {
    const category = ingredient.category || 'other';
    if (!ingredientsByCategory[category]) {
      ingredientsByCategory[category] = [];
    }

    // Calculate quantities for each diet profile
    const quantitiesPerProfile = {};
    dietProfiles.forEach(profile => {
      const multiplier = meal.base_servings[profile] || 1;
      // Check for ingredient-specific override
      const overrideMultiplier = ingredient.base_servings_override?.[profile];
      const finalMultiplier = overrideMultiplier !== undefined ? overrideMultiplier : multiplier;

      quantitiesPerProfile[profile] = {
        quantity: Math.round(ingredient.quantity * finalMultiplier), // Round to whole number
        unit: ingredient.unit
      };
    });

    ingredientsByCategory[category].push({
      ...ingredient,
      quantitiesPerProfile
    });
  });

  // Handle backdrop click
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      onClick={handleBackdropClick}
    >
      <div
        className="relative w-full max-w-6xl max-h-[90vh] overflow-y-auto rounded-lg shadow-xl"
        style={{ backgroundColor: colors.base }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="sticky top-0 z-10 flex items-center justify-between p-4 border-b"
          style={{ backgroundColor: colors.base, borderColor: colors.surface0 }}
        >
          <h2 className="text-xl font-bold" style={{ color: colors.text }}>
            {meal.name}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-opacity-80 transition-colors"
            style={{ backgroundColor: colors.surface0, color: colors.text }}
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content - Two Column Layout */}
        <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LEFT COLUMN - Ingredients & Details */}
          <div className="space-y-6">
            {/* Calories Section */}
            {Object.keys(calories).length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: colors.text }}>
                  {t('calories')}
                </h3>
                <div className="flex flex-wrap gap-3">
                  {Object.entries(calories).map(([profile, kcal]) => (
                    <div
                      key={profile}
                      className="px-3 py-2 rounded-lg"
                      style={{ backgroundColor: colors.surface0, color: colors.text }}
                    >
                      <span className="font-medium">{profile}:</span> ~{Math.round(kcal)} kcal
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Ingredients Section */}
            <div>
            <h3 className="text-lg font-semibold mb-3" style={{ color: colors.text }}>
              {t('ingredients')}
            </h3>
            <div className="space-y-4">
              {Object.entries(ingredientsByCategory).map(([category, ingredients]) => (
                <div key={category}>
                  {/* Ingredients Table */}
                  <div className="overflow-x-auto pt-4">
                    <table className="w-full text-sm" style={{ borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ borderBottom: `2px solid ${colors.surface1}` }}>
                          <th
                            className="text-left py-2 px-2 font-medium uppercase"
                            style={{ color: colors.subtext1 }}
                          >
                            {t(`category_${category}`) !== `category_${category}` ? t(`category_${category}`) : category}
                          </th>
                          {dietProfiles.map(profile => (
                            <th
                              key={profile}
                              className="text-right py-2 px-2 font-medium relative"
                              style={{ color: colors.subtext1 }}
                            >
                              <div className="relative inline-block">
                                <div className="text-xs font-normal absolute -top-3 right-0" style={{ color: colors.subtext0 }}>
                                  ({meal.base_servings[profile]}x)
                                </div>
                                {profile}
                              </div>
                            </th>
                          ))}
                          <th
                            className="text-right py-2 px-2 font-medium"
                            style={{ color: colors.subtext1 }}
                          >
                            {t('total')}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {ingredients.map((ingredient, idx) => {
                          // Calculate total quantity across all profiles
                          const totalQuantity = dietProfiles.reduce((sum, profile) => {
                            return sum + ingredient.quantitiesPerProfile[profile].quantity;
                          }, 0);

                          return (
                            <tr
                              key={idx}
                              style={{
                                backgroundColor: idx % 2 === 0 ? colors.surface0 : 'transparent',
                                borderBottom: `1px solid ${colors.surface1}`
                              }}
                            >
                              <td className="py-2 px-2" style={{ color: colors.text }}>
                                <div>
                                  {ingredient.name}
                                  {ingredient.notes && (
                                    <div
                                      className="text-xs italic mt-0.5"
                                      style={{ color: colors.subtext0 }}
                                    >
                                      {ingredient.notes}
                                    </div>
                                  )}
                                </div>
                              </td>
                              {dietProfiles.map(profile => (
                                <td
                                  key={profile}
                                  className="text-right py-2 px-2 font-medium"
                                  style={{ color: colors.text }}
                                >
                                  {ingredient.quantitiesPerProfile[profile].quantity}
                                  {ingredient.quantitiesPerProfile[profile].unit}
                                </td>
                              ))}
                              <td
                                className="text-right py-2 px-2 font-bold"
                                style={{ color: colors.text }}
                              >
                                {Math.round(totalQuantity)}
                                {ingredient.unit}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
            </div>

            {/* Seasonings Section */}
            {meal.suggested_seasonings && (
              <div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: colors.text }}>
                  🧂 {t('suggested_seasonings_title')}
                </h3>
                <div
                  className="p-3 rounded-lg"
                  style={{ backgroundColor: colors.surface0, color: colors.text }}
                >
                  {meal.suggested_seasonings}
                </div>
              </div>
            )}
          </div>

          {/* RIGHT COLUMN - Steps & Prep */}
          <div className="space-y-6">
            {/* Cooking Steps Section */}
            {meal.steps && meal.steps.length > 0 && (
              <div>
              <h3 className="text-lg font-semibold mb-3" style={{ color: colors.text }}>
                📋 {t('cooking_steps')}
              </h3>
              <ol className="space-y-2">
                {meal.steps.map((step, idx) => (
                  <li
                    key={idx}
                    className="flex gap-3 p-3 rounded-lg"
                    style={{ backgroundColor: colors.surface0 }}
                  >
                    <span
                      className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full text-sm font-bold"
                      style={{ backgroundColor: colors.blue, color: colors.base }}
                    >
                      {idx + 1}
                    </span>
                    <span style={{ color: colors.text }}>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Prep Tasks Section */}
          {meal.prep_tasks && meal.prep_tasks.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3" style={{ color: colors.text }}>
                ⚠️ {t('prep_tasks')}
              </h3>
              <div className="space-y-2">
                {meal.prep_tasks.map((task, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg"
                    style={{ backgroundColor: colors.surface0, color: colors.text }}
                  >
                    <p className="font-medium">{task.description}</p>
                    {task.days_before && (
                      <p className="text-sm mt-1" style={{ color: colors.subtext1 }}>
                        {task.days_before} {t('days_before_cooking')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
