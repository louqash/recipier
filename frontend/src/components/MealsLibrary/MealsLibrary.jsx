/**
 * MealsLibrary - Sidebar component showing draggable meal cards
 */
import { useState, useEffect, useRef } from 'react';
import { Draggable } from '@fullcalendar/interaction';
import MealCard from './MealCard';
import { useMeals } from '../../hooks/useMeals';
import { useTranslation } from '../../hooks/useTranslation';

export default function MealsLibrary() {
  const [searchQuery, setSearchQuery] = useState('');
  const { meals, loading, error } = useMeals(searchQuery);
  const mealsContainerRef = useRef(null);
  const { t, mealCount } = useTranslation();

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
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold mb-3">{t('meals_library')}</h2>

        {/* Search */}
        <input
          type="text"
          placeholder={t('search_meals')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input-field w-full text-sm"
        />
      </div>

      {/* Meals List */}
      <div ref={mealsContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <p className="mt-2 text-sm text-gray-600">{t('loading_meals')}</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3 text-red-800 text-sm">
            {error}
          </div>
        )}

        {!loading && !error && meals.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-sm">
            {t('no_meals_found')}
          </div>
        )}

        {!loading && !error && meals.map((meal) => (
          <MealCard key={meal.meal_id} meal={meal} />
        ))}
      </div>

      {/* Footer */}
      {!loading && !error && meals.length > 0 && (
        <div className="p-3 border-t border-gray-200 text-xs text-gray-500 text-center">
          {mealCount(meals.length)}
        </div>
      )}
    </div>
  );
}
