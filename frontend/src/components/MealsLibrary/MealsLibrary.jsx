/**
 * MealsLibrary - Sidebar component showing draggable meal cards
 */
import { useState, useEffect, useRef } from 'react';
import { Draggable } from '@fullcalendar/interaction';
import MealCard from './MealCard';
import MealDetailsModal from '../MealDetailsModal/MealDetailsModal';
import { useMeals } from '../../hooks/useMeals';
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme.jsx';
import { loadIngredientCalories } from '../../utils/calorieCalculator';

export default function MealsLibrary() {
  const [searchQuery, setSearchQuery] = useState('');
  const [caloriesDict, setCaloriesDict] = useState(null);
  const [detailsModalMealId, setDetailsModalMealId] = useState(null);
  const { meals, loading, error } = useMeals(searchQuery);
  const mealsContainerRef = useRef(null);
  const { t, mealCount } = useTranslation();
  const { colors } = useTheme();

  // Load ingredient calories dictionary once on mount
  useEffect(() => {
    loadIngredientCalories().then(setCaloriesDict);
  }, []);

  // Initialize FullCalendar Draggable on meal cards
  useEffect(() => {
    let draggable = null;

    if (mealsContainerRef.current && meals.length > 0) {
      draggable = new Draggable(mealsContainerRef.current, {
        itemSelector: '.meal-card',
        eventData: function(eventEl) {
          const mealData = JSON.parse(eventEl.dataset.mealData || '{}');
          return {
            title: mealData.meal_name,
            meal_id: mealData.meal_id,
            create: true
          };
        }
      });
    }

    // Cleanup function to destroy draggable instance
    return () => {
      if (draggable) {
        draggable.destroy();
      }
    };
  }, [meals.length]); // Only reinitialize when number of meals changes

  return (
    <div className="h-full flex flex-col" style={{
      backgroundColor: colors.base,
      borderRight: `1px solid ${colors.surface0}`
    }}>
      {/* Header */}
      <div className="p-4" style={{ borderBottom: `1px solid ${colors.surface0}` }}>
        <h2 className="text-lg font-semibold mb-3" style={{ color: colors.text }}>
          {t('meals_library')}
        </h2>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder={t('search_meals')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field w-full text-sm pr-8"
            style={{
              backgroundColor: colors.surface0,
              borderColor: colors.surface1,
              color: colors.text
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-opacity-80 transition-colors"
              style={{ color: colors.overlay0 }}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Meals List */}
      <div ref={mealsContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2" style={{ borderBottomColor: colors.blue }}></div>
            <p className="mt-2 text-sm" style={{ color: colors.subtext1 }}>{t('loading_meals')}</p>
          </div>
        )}

        {error && (
          <div className="rounded p-3 text-sm" style={{
            backgroundColor: colors.red + '20',
            border: `1px solid ${colors.red}`,
            color: colors.red
          }}>
            {error}
          </div>
        )}

        {!loading && !error && meals.length === 0 && (
          <div className="text-center py-8 text-sm" style={{ color: colors.subtext0 }}>
            {t('no_meals_found')}
          </div>
        )}

        {!loading && !error && meals.map((meal) => (
          <MealCard
            key={meal.meal_id}
            meal={meal}
            caloriesDict={caloriesDict}
            onShowDetails={setDetailsModalMealId}
          />
        ))}
      </div>

      {/* Footer */}
      {!loading && !error && meals.length > 0 && (
        <div className="p-3 text-xs text-center" style={{
          borderTop: `1px solid ${colors.surface0}`,
          color: colors.subtext0
        }}>
          {mealCount(meals.length)}
        </div>
      )}

      {/* Meal Details Modal */}
      <MealDetailsModal
        isOpen={detailsModalMealId !== null}
        onClose={() => setDetailsModalMealId(null)}
        mealId={detailsModalMealId}
      />
    </div>
  );
}
