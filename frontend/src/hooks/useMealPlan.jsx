/**
 * Central state management for meal planning
 * Manages scheduled meals, shopping trips, and modal state
 */
import { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { mealsAPI } from '../api/client';
import { translations } from '../localization/translations';

const MealPlanContext = createContext(null);

/**
 * Generate unique ID for scheduled meal instance
 * Format: sm_{timestamp}
 */
const generateScheduledMealId = () => {
  return `sm_${Date.now()}`;
};

export function MealPlanProvider({ children }) {
  // Meal plan state
  const [scheduledMeals, setScheduledMeals] = useState([]);
  const [shoppingTrips, setShoppingTrips] = useState([]);
  const [mealNamesCache, setMealNamesCache] = useState({}); // meal_id -> name mapping

  // UI state
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [currentMealData, setCurrentMealData] = useState(null);
  const [currentMealConfig, setCurrentMealConfig] = useState(null);

  // Settings
  const [language, setLanguage] = useState('polish');
  const [todoistToken, setTodoistToken] = useState(
    sessionStorage.getItem('todoist_token') || ''
  );
  const [dietProfiles, setDietProfiles] = useState({}); // person -> profile mapping (e.g., "John" -> "high_calorie", "Jane" -> "low_calorie")

  /**
   * Add a new scheduled meal
   * Automatically generates unique ID if not provided
   */
  const addScheduledMeal = useCallback((mealConfig) => {
    const mealWithId = {
      ...mealConfig,
      id: mealConfig.id || generateScheduledMealId()
    };
    setScheduledMeals(prev => [...prev, mealWithId]);
  }, []);

  /**
   * Update an existing scheduled meal
   */
  const updateScheduledMeal = useCallback((index, updates) => {
    setScheduledMeals(prev => {
      const newMeals = [...prev];
      newMeals[index] = { ...newMeals[index], ...updates };
      return newMeals;
    });
  }, []);

  /**
   * Remove a scheduled meal and clean up from shopping trips
   */
  const removeScheduledMeal = useCallback((index) => {
    // Get the meal ID before removing
    const mealId = scheduledMeals[index]?.id;

    // Remove the meal from scheduledMeals
    setScheduledMeals(prev => prev.filter((_, i) => i !== index));

    // Remove the meal from all shopping trips
    if (mealId) {
      setShoppingTrips(prev =>
        prev.map(trip => ({
          ...trip,
          scheduled_meal_ids: trip.scheduled_meal_ids.filter(id => id !== mealId)
        }))
      );
    }
  }, [scheduledMeals]);

  /**
   * Find scheduled meal index by unique ID
   */
  const findScheduledMeal = useCallback((id) => {
    return scheduledMeals.findIndex(meal => meal.id === id);
  }, [scheduledMeals]);

  /**
   * Get scheduled meal by unique ID
   */
  const getScheduledMealById = useCallback((id) => {
    return scheduledMeals.find(meal => meal.id === id);
  }, [scheduledMeals]);

  /**
   * Add a shopping trip
   */
  const addShoppingTrip = useCallback((trip) => {
    setShoppingTrips(prev => [...prev, trip]);
  }, []);

  /**
   * Update a shopping trip
   */
  const updateShoppingTrip = useCallback((index, updates) => {
    setShoppingTrips(prev => {
      const newTrips = [...prev];
      newTrips[index] = { ...newTrips[index], ...updates };
      return newTrips;
    });
  }, []);

  /**
   * Remove a shopping trip
   */
  const removeShoppingTrip = useCallback((index) => {
    setShoppingTrips(prev => prev.filter((_, i) => i !== index));
  }, []);

  /**
   * Add scheduled meal to shopping trip
   * @param {number} tripIndex - Index of shopping trip
   * @param {string} scheduledMealId - Unique ID of scheduled meal instance
   */
  const addMealToTrip = useCallback((tripIndex, scheduledMealId) => {
    setShoppingTrips(prev => {
      const newTrips = [...prev];
      if (!newTrips[tripIndex].scheduled_meal_ids.includes(scheduledMealId)) {
        newTrips[tripIndex].scheduled_meal_ids.push(scheduledMealId);
      }
      return newTrips;
    });
  }, []);

  /**
   * Remove scheduled meal from shopping trip
   * @param {number} tripIndex - Index of shopping trip
   * @param {string} scheduledMealId - Unique ID of scheduled meal instance
   */
  const removeMealFromTrip = useCallback((tripIndex, scheduledMealId) => {
    setShoppingTrips(prev => {
      const newTrips = [...prev];
      newTrips[tripIndex].scheduled_meal_ids = newTrips[tripIndex].scheduled_meal_ids.filter(
        id => id !== scheduledMealId
      );
      return newTrips;
    });
  }, []);

  /**
   * Get meal name from cache (synchronous)
   * Returns meal_id as fallback if not in cache
   */
  const getMealNameSync = useCallback((mealId) => {
    return mealNamesCache[mealId] || mealId;
  }, [mealNamesCache]);

  /**
   * Fetch and cache meal name (async)
   */
  const fetchMealName = useCallback(async (mealId) => {
    if (mealNamesCache[mealId]) {
      return mealNamesCache[mealId];
    }

    try {
      const mealData = await mealsAPI.getById(mealId);
      const name = mealData.name;
      setMealNamesCache(prev => ({ ...prev, [mealId]: name }));
      return name;
    } catch (error) {
      console.error(`Failed to fetch meal name for ${mealId}:`, error);
      return mealId;
    }
  }, [mealNamesCache]);

  /**
   * Open meal configuration modal
   * Fetches full meal data from API
   * Returns a promise that resolves to true if saved, false if cancelled
   */
  const openConfigModal = useCallback(async (mealId, date = null, existingConfig = null) => {
    return new Promise(async (resolve) => {
      try {
        // Fetch full meal data from API
        const mealData = await mealsAPI.getById(mealId);
        // Cache the meal name
        setMealNamesCache(prev => ({ ...prev, [mealId]: mealData.name }));
        setCurrentMealData(mealData);
        setCurrentMealConfig({
          initialDate: date,
          existingConfig: existingConfig,
          onComplete: resolve  // Store the resolve function
        });
        setConfigModalOpen(true);
      } catch (error) {
        console.error('Failed to load meal data:', error);
        alert('Failed to load meal data. Please try again.');
        resolve(false);  // Resolve with false on error
      }
    });
  }, []);

  /**
   * Close meal configuration modal
   * @param {boolean} saved - Whether the modal was saved (true) or cancelled (false)
   */
  const closeConfigModal = useCallback((saved = false) => {
    // Call the completion callback if it exists
    if (currentMealConfig?.onComplete) {
      currentMealConfig.onComplete(saved);
    }
    setConfigModalOpen(false);
    setCurrentMealData(null);
    setCurrentMealConfig(null);
  }, [currentMealConfig]);

  /**
   * Clear all meal plan data
   */
  const clearMealPlan = useCallback(() => {
    setScheduledMeals([]);
    setShoppingTrips([]);
  }, []);

  /**
   * Load meal plan from data
   * Validates new format and rejects old formats
   */
  const loadMealPlan = useCallback((mealPlanData) => {
    // Validate scheduled_meals have IDs
    if (mealPlanData.scheduled_meals) {
      const missingIds = mealPlanData.scheduled_meals.some(meal => !meal.id);
      if (missingIds) {
        throw new Error('Old meal plan format detected. Please create a new meal plan using the web interface.');
      }
      setScheduledMeals(mealPlanData.scheduled_meals);
    }

    // Validate shopping_trips use new field names
    if (mealPlanData.shopping_trips) {
      const oldFormat = mealPlanData.shopping_trips.some(
        trip => trip.meal_ids || trip.date
      );
      if (oldFormat) {
        throw new Error('Old shopping trip format detected. Please create a new meal plan using the web interface.');
      }
      setShoppingTrips(mealPlanData.shopping_trips);
    }
  }, []);

  /**
   * Get meal plan as JSON (for saving/API calls)
   */
  const getMealPlanJSON = useCallback(() => {
    return {
      scheduled_meals: scheduledMeals,
      shopping_trips: shoppingTrips
    };
  }, [scheduledMeals, shoppingTrips]);

  /**
   * Update Todoist token and save to session storage
   */
  const updateTodoistToken = useCallback((token) => {
    setTodoistToken(token);
    sessionStorage.setItem('todoist_token', token);
  }, []);

  /**
   * Validate cooking dates and portions
   * Returns { valid: boolean, errors: string[] }
   */
  const validateMealConfig = useCallback((config) => {
    const errors = [];
    const t = translations[language] || translations.polish;
    const eatingDates = config.eating_dates_per_person || {};
    const firstCookingDate = config.cooking_dates?.length > 0 ? config.cooking_dates.sort()[0] : null;

    Object.entries(eatingDates).forEach(([person, dates]) => {
      if (!dates || dates.length === 0) {
        errors.push(t.error_person_no_eating_dates.replace('{person}', person));
      }

      dates.forEach(date => {
        if (firstCookingDate && date < firstCookingDate) {
          errors.push(
            t.error_eating_before_cooking
              .replace('{person}', person)
              .replace('{eating_date}', date)
              .replace('{cooking_date}', firstCookingDate)
          );
        }
      });

      if (config.cooking_dates.length > 1 && dates.length % config.cooking_dates.length !== 0) {
        errors.push(
          t.error_eating_dates_not_divisible
            .replace('{person}', person)
            .replace('{num_eating}', dates.length)
            .replace('{num_cooking}', config.cooking_dates.length)
        );
      }
    });

    return {
      valid: errors.length === 0,
      errors
    };
  }, [language]);

  /**
   * Modal state for MealConfigModal component
   */
  const modalState = useMemo(() => ({
    isOpen: configModalOpen,
    meal: currentMealData,
    initialDate: currentMealConfig?.initialDate,
    existingConfig: currentMealConfig?.existingConfig
  }), [configModalOpen, currentMealData, currentMealConfig]);

  const value = {
    // State
    scheduledMeals,
    shoppingTrips,
    modalState,
    language,
    todoistToken,
    dietProfiles,

    // Meal actions
    addScheduledMeal,
    updateScheduledMeal,
    removeScheduledMeal,
    findScheduledMeal,
    getScheduledMealById,
    getMealNameSync,
    fetchMealName,

    // Shopping trip actions
    addShoppingTrip,
    updateShoppingTrip,
    removeShoppingTrip,
    addMealToTrip,
    removeMealFromTrip,

    // Modal actions
    openConfigModal,
    closeConfigModal,

    // Meal plan actions
    clearMealPlan,
    loadMealPlan,
    getMealPlanJSON,

    // Settings
    setLanguage,
    updateTodoistToken,
    setDietProfiles,

    // Validation
    validateMealConfig,
  };

  return (
    <MealPlanContext.Provider value={value}>
      {children}
    </MealPlanContext.Provider>
  );
}

/**
 * Hook to access meal plan context
 */
export function useMealPlan() {
  const context = useContext(MealPlanContext);
  if (!context) {
    throw new Error('useMealPlan must be used within MealPlanProvider');
  }
  return context;
}
