/**
 * Shopping Trip Manager
 * Allows creating shopping trips and assigning meals to them
 */
import { useState, useEffect } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan';
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme.jsx';
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
  const { colors } = useTheme();

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
    <div className="p-4" style={{
      backgroundColor: colors.base,
      borderTop: `1px solid ${colors.surface0}`
    }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold" style={{ color: colors.text }}>
            🛒 {t('shopping_trips')}
          </h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: colors.green,
              color: colors.base
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.teal}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.green}
          >
            {showAddForm ? t('cancel') : `+ ${t('add_shopping_trip')}`}
          </button>
        </div>

        {/* Add Trip Form */}
        {showAddForm && (
          <form onSubmit={handleAddTrip} className="mb-4 p-3 rounded-lg" style={{
            backgroundColor: colors.surface0,
            border: `1px solid ${colors.surface1}`
          }}>
            <div className="flex gap-2">
              <input
                type="date"
                value={newTripDate}
                onChange={(e) => setNewTripDate(e.target.value)}
                className="flex-1 px-3 py-2 rounded-lg focus:outline-none focus:ring-2"
                style={{
                  backgroundColor: colors.base,
                  borderColor: colors.surface1,
                  color: colors.text,
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  colorScheme: colors.base === '#1e1e2e' ? 'dark' : 'light'
                }}
                placeholder={t('shopping_date')}
                required
              />
              <button
                type="submit"
                className="px-4 py-2 rounded-lg font-medium transition-colors"
                style={{
                  backgroundColor: colors.blue,
                  color: colors.base
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.sapphire}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.blue}
              >
                {t('add')}
              </button>
            </div>
          </form>
        )}

        {/* Shopping Trips List */}
        {shoppingTrips.length === 0 ? (
          <div className="text-center py-8" style={{ color: colors.subtext0 }}>
            <p>{t('no_shopping_trips')}</p>
            <p className="text-sm mt-1">{t('add_trip_instruction')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {shoppingTrips.map((trip, index) => (
              <div
                key={index}
                className="rounded-lg p-4 transition-colors"
                style={{
                  backgroundColor: colors.surface0,
                  border: `2px solid ${colors.surface1}`
                }}
              >
                {/* Trip Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex-1">
                    <div className="text-sm" style={{ color: colors.subtext0 }}>
                      {t('shopping_date')}
                    </div>
                    <div className="font-semibold" style={{ color: colors.text }}>
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
                      className="p-1 text-sm transition-colors"
                      style={{ color: colors.green }}
                      onMouseEnter={(e) => e.currentTarget.style.color = colors.teal}
                      onMouseLeave={(e) => e.currentTarget.style.color = colors.green}
                      title={t('add_meals')}
                    >
                      ➕
                    </button>
                    <button
                      onClick={() => removeShoppingTrip(index)}
                      className="p-1 transition-colors"
                      style={{ color: colors.red }}
                      onMouseEnter={(e) => e.currentTarget.style.color = colors.maroon}
                      onMouseLeave={(e) => e.currentTarget.style.color = colors.red}
                      title={t('delete_trip')}
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                {/* Meal Selector Dropdown */}
                {showMealSelector === index && (
                  <div className="mb-3 p-2 rounded max-h-40 overflow-y-auto" style={{
                    backgroundColor: colors.base,
                    border: `1px solid ${colors.surface1}`
                  }}>
                    <div className="text-xs mb-2" style={{ color: colors.subtext0 }}>
                      {t('select_meals_to_add')}
                    </div>
                    {scheduledMeals.length === 0 ? (
                      <div className="text-xs italic" style={{ color: colors.overlay0 }}>
                        {t('no_meals_scheduled')}
                      </div>
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
                              className="block w-full text-left px-2 py-1 text-xs rounded mb-1 transition-colors"
                              style={{
                                backgroundColor: alreadyAdded ? colors.surface0 : 'transparent',
                                color: alreadyAdded ? colors.overlay0 : colors.text,
                                cursor: alreadyAdded ? 'not-allowed' : 'pointer'
                              }}
                              onMouseEnter={(e) => {
                                if (!alreadyAdded) {
                                  e.currentTarget.style.backgroundColor = colors.surface0;
                                }
                              }}
                              onMouseLeave={(e) => {
                                if (!alreadyAdded) {
                                  e.currentTarget.style.backgroundColor = 'transparent';
                                }
                              }}
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
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {trip.scheduled_meal_ids.length === 0 ? (
                    <p className="text-sm italic text-center py-2" style={{ color: colors.overlay0 }}>
                      {t('no_meals_yet')}
                    </p>
                  ) : (
                    trip.scheduled_meal_ids.map((scheduledMealId) => (
                      <div
                        key={scheduledMealId}
                        className="px-3 py-2 rounded flex items-center justify-between group"
                        style={{
                          backgroundColor: colors.base,
                          border: `1px solid ${colors.surface1}`
                        }}
                      >
                        <span className="text-sm" style={{ color: colors.text }}>
                          {getScheduledMealDisplay(scheduledMealId)}
                        </span>
                        <button
                          onClick={() => removeMealFromTrip(index, scheduledMealId)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                          style={{ color: colors.overlay0 }}
                          onMouseEnter={(e) => e.currentTarget.style.color = colors.red}
                          onMouseLeave={(e) => e.currentTarget.style.color = colors.overlay0}
                          title="Remove meal"
                        >
                          ✕
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* Meal Count */}
                <div className="mt-3 pt-3 text-sm" style={{
                  borderTop: `1px solid ${colors.surface1}`,
                  color: colors.subtext0
                }}>
                  {mealCount(trip.scheduled_meal_ids.length)}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help Text */}
        {shoppingTrips.length > 0 && (
          <div className="mt-4 text-sm text-center" style={{ color: colors.subtext0 }}>
            💡 {t('click_plus_to_add')}
          </div>
        )}
      </div>
    </div>
  );
}
