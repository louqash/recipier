/**
 * Shopping Trip Manager
 * Allows creating shopping trips and assigning meals to them
 */
import { useState, useEffect } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan';
import { useTranslation } from '../../hooks/useTranslation';
import { formatMealWithDates } from '../../localization/translations';

export default function ShoppingManager() {
  const {
    shoppingTrips,
    scheduledMeals,
    addShoppingTrip,
    updateShoppingTrip,
    removeShoppingTrip,
    addMealToTrip,
    removeMealFromTrip,
    getScheduledMealById,
    getMealNameSync,
    fetchMealName,
    language,
  } = useMealPlan();
  const { t, mealCount } = useTranslation();

  const [newTripDate, setNewTripDate] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [showMealSelector, setShowMealSelector] = useState(null); // tripIndex or null

  // Prefetch meal names for all scheduled meals
  useEffect(() => {
    scheduledMeals.forEach(meal => {
      fetchMealName(meal.meal_id);
    });
  }, [scheduledMeals, fetchMealName]);

  // Get meal display with cooking dates
  const getScheduledMealDisplay = (scheduledMealId) => {
    const meal = getScheduledMealById(scheduledMealId);
    if (!meal) return scheduledMealId;
    const mealName = getMealNameSync(meal.meal_id);
    return formatMealWithDates(mealName, meal.cooking_dates, language);
  };

  // Check if a meal is already assigned to any shopping trip
  const getMealTripAssignment = (mealId) => {
    for (let i = 0; i < shoppingTrips.length; i++) {
      if (shoppingTrips[i].scheduled_meal_ids.includes(mealId)) {
        return i; // Return trip index
      }
    }
    return -1; // Not assigned to any trip
  };

  // Handle adding a new shopping trip
  const handleAddTrip = (e) => {
    e.preventDefault();
    if (!newTripDate) return;

    addShoppingTrip({
      shopping_date: newTripDate,
      scheduled_meal_ids: []
    });

    setNewTripDate('');
    setShowAddForm(false);
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            🛒 {t('shopping_trips')}
          </h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium transition-colors"
          >
            {showAddForm ? t('cancel') : `+ ${t('add_shopping_trip')}`}
          </button>
        </div>

        {/* Add Trip Form */}
        {showAddForm && (
          <form onSubmit={handleAddTrip} className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex gap-2">
              <input
                type="date"
                value={newTripDate}
                onChange={(e) => setNewTripDate(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={t('shopping_date')}
                required
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                {t('add')}
              </button>
            </div>
          </form>
        )}

        {/* Shopping Trips List */}
        {shoppingTrips.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>{t('no_shopping_trips')}</p>
            <p className="text-sm mt-1">{t('add_trip_instruction')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {shoppingTrips.map((trip, index) => (
              <div
                key={index}
                className="border-2 border-gray-300 rounded-lg p-4 bg-gray-50 transition-colors"
              >
                {/* Trip Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex-1">
                    <div className="text-sm text-gray-500">{t('shopping_date')}</div>
                    <div className="font-semibold text-gray-900">
                      {new Date(trip.shopping_date).toLocaleDateString(
                        language === 'polish' ? 'pl-PL' : 'en-US',
                        {
                          weekday: 'short',
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        }
                      )}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => setShowMealSelector(showMealSelector === index ? null : index)}
                      className="text-green-600 hover:text-green-700 p-1 text-sm"
                      title={t('add_meals')}
                    >
                      ➕
                    </button>
                    <button
                      onClick={() => removeShoppingTrip(index)}
                      className="text-red-500 hover:text-red-700 p-1"
                      title={t('delete_trip')}
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                {/* Meal Selector Dropdown */}
                {showMealSelector === index && (
                  <div className="mb-3 p-2 bg-white rounded border border-gray-300 max-h-40 overflow-y-auto">
                    <div className="text-xs text-gray-500 mb-2">{t('select_meals_to_add')}</div>
                    {scheduledMeals.length === 0 ? (
                      <div className="text-xs text-gray-400 italic">{t('no_meals_scheduled')}</div>
                    ) : (
                      scheduledMeals
                        .filter((meal) => {
                          const assignedTripIndex = getMealTripAssignment(meal.id);
                          // Only show meals that are unassigned or assigned to current trip
                          return assignedTripIndex === -1 || assignedTripIndex === index;
                        })
                        .map((meal) => {
                          const alreadyAdded = trip.scheduled_meal_ids.includes(meal.id);

                          return (
                            <button
                              key={meal.id}
                              onClick={() => {
                                if (!alreadyAdded) {
                                  addMealToTrip(index, meal.id);
                                }
                              }}
                              disabled={alreadyAdded}
                              className={`block w-full text-left px-2 py-1 text-xs rounded mb-1 ${
                                alreadyAdded
                                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                  : 'hover:bg-blue-50 text-gray-700 cursor-pointer'
                              }`}
                            >
                              {alreadyAdded ? '✓ ' : ''}
                              {formatMealWithDates(getMealNameSync(meal.meal_id), meal.cooking_dates, language)}
                            </button>
                          );
                        })
                    )}
                  </div>
                )}

                {/* Meals List */}
                <div className="space-y-2">
                  {trip.scheduled_meal_ids.length === 0 ? (
                    <p className="text-sm text-gray-400 italic text-center py-2">
                      {t('no_meals_yet')}
                    </p>
                  ) : (
                    trip.scheduled_meal_ids.map((scheduledMealId) => (
                      <div
                        key={scheduledMealId}
                        className="bg-white px-3 py-2 rounded border border-gray-200 flex items-center justify-between group"
                      >
                        <span className="text-sm text-gray-700">
                          {getScheduledMealDisplay(scheduledMealId)}
                        </span>
                        <button
                          onClick={() => removeMealFromTrip(index, scheduledMealId)}
                          className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Remove meal"
                        >
                          ✕
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* Meal Count */}
                <div className="mt-3 pt-3 border-t border-gray-200 text-sm text-gray-500">
                  {mealCount(trip.scheduled_meal_ids.length)}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help Text */}
        {shoppingTrips.length > 0 && (
          <div className="mt-4 text-sm text-gray-500 text-center">
            💡 {t('click_plus_to_add')}
          </div>
        )}
      </div>
    </div>
  );
}
