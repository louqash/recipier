/**
 * MealConfigModal - Modal for configuring meals when dropped on calendar
 */
import { useState, useEffect, useMemo } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';
import { useTranslation } from '../../hooks/useTranslation';
import { configAPI } from '../../api/client';

const MEAL_TYPES = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'second_breakfast', label: 'Second Breakfast' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'supper', label: 'Supper' },
];

export default function MealConfigModal() {
  const {
    modalState,
    closeConfigModal,
    addScheduledMeal,
    updateScheduledMeal,
    findScheduledMeal,
    removeScheduledMeal
  } = useMealPlan();

  const { isOpen, meal, initialDate, existingConfig } = modalState;
  const { t } = useTranslation();

  // Dynamic users from config
  const [availableUsers, setAvailableUsers] = useState([]);
  const [cooks, setCooks] = useState([]);

  // Form state
  const [cookingDates, setCookingDates] = useState([]);
  const [servingsPerPerson, setServingsPerPerson] = useState({});
  const [mealType, setMealType] = useState('dinner');
  const [assignedCook, setAssignedCook] = useState('');
  const [prepAssignedTo, setPrepAssignedTo] = useState('');
  const [validationErrors, setValidationErrors] = useState([]);

  // Fetch users from config on mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await configAPI.getUsers();
        const users = response.users || [];

        if (users.length === 0) {
          console.error('No users configured in config file');
          alert('No users configured. Please set up user_mapping in config file.');
          return;
        }

        setAvailableUsers(users);
        setCooks([...users, 'Both']);

        // Set default values once users are loaded
        setAssignedCook(users[0]);
        setPrepAssignedTo(users[0]);

        // Initialize default servings
        const defaultServings = {};
        users.forEach(user => {
          defaultServings[user] = 1;
        });
        setServingsPerPerson(defaultServings);
      } catch (error) {
        console.error('Failed to fetch users:', error);
        alert('Failed to load user configuration. Please check your config file.');
      }
    };
    fetchUsers();
  }, []);

  // Initialize form when modal opens
  useEffect(() => {
    if (isOpen && availableUsers.length > 0) {
      if (existingConfig) {
        // Editing existing meal
        setCookingDates(existingConfig.cooking_dates || []);
        setServingsPerPerson(existingConfig.servings_per_person || createDefaultServings());
        setMealType(existingConfig.meal_type || 'dinner');
        setAssignedCook(existingConfig.assigned_cook || availableUsers[0]);
        setPrepAssignedTo(existingConfig.prep_assigned_to || availableUsers[0]);
      } else {
        // New meal - initialize with dropped date
        setCookingDates(initialDate ? [initialDate] : []);
        setServingsPerPerson(createDefaultServings());
        setMealType('dinner');
        setAssignedCook(availableUsers[0]);
        setPrepAssignedTo(availableUsers[0]);
      }
      setValidationErrors([]);
    }
  }, [isOpen, initialDate, existingConfig, availableUsers]);

  // Helper to create default servings
  const createDefaultServings = () => {
    const servings = {};
    availableUsers.forEach(user => {
      servings[user] = 1;
    });
    return servings;
  };

  // Validate configuration in real-time
  useEffect(() => {
    if (!isOpen) return;

    const errors = [];
    const numCookingDates = cookingDates.length;

    if (numCookingDates === 0) {
      errors.push('At least one cooking date is required');
    }

    // Critical validation: for multiple cooking dates, portions must match
    if (numCookingDates > 1) {
      Object.entries(servingsPerPerson).forEach(([person, portions]) => {
        if (portions !== numCookingDates) {
          errors.push(
            `For ${numCookingDates} cooking dates, ${person} must have ${numCookingDates} portions (currently ${portions})`
          );
        }
      });
    }

    setValidationErrors(errors);
  }, [cookingDates, servingsPerPerson, isOpen]);

  const handleAddCookingDate = () => {
    let newDate;
    if (cookingDates.length > 0) {
      // Find the latest date and add 1 day
      const sortedDates = [...cookingDates].sort();
      const latestDate = new Date(sortedDates[sortedDates.length - 1]);
      latestDate.setDate(latestDate.getDate() + 1);
      newDate = latestDate.toISOString().split('T')[0];
    } else {
      // No dates yet, use today
      newDate = new Date().toISOString().split('T')[0];
    }
    setCookingDates([...cookingDates, newDate]);
  };

  const handleRemoveCookingDate = (index) => {
    setCookingDates(cookingDates.filter((_, i) => i !== index));
  };

  const handleDateChange = (index, newDate) => {
    const updated = [...cookingDates];
    updated[index] = newDate;
    setCookingDates(updated);
  };

  const handleServingChange = (person, delta) => {
    setServingsPerPerson(prev => ({
      ...prev,
      [person]: Math.max(0, Math.min(10, (prev[person] || 0) + delta))
    }));
  };

  const handleSave = () => {
    if (validationErrors.length > 0) {
      return; // Don't save if there are validation errors
    }

    const config = {
      meal_id: meal?.meal_id,
      cooking_dates: cookingDates.sort(),
      servings_per_person: servingsPerPerson,
      meal_type: mealType,
      assigned_cook: assignedCook,
      prep_assigned_to: meal?.prep_tasks?.length > 0 ? prepAssignedTo : undefined,
    };

    if (existingConfig) {
      // Preserve the ID when editing
      config.id = existingConfig.id;
      const index = findScheduledMeal(existingConfig.id);
      if (index !== -1) {
        updateScheduledMeal(index, config);
      }
    } else {
      // ID will be auto-generated by addScheduledMeal
      addScheduledMeal(config);
    }

    closeConfigModal(true);  // Pass true to indicate save
  };

  const handleCancel = () => {
    closeConfigModal(false);  // Pass false to indicate cancel
  };

  const handleDelete = () => {
    if (!existingConfig) return;

    // Confirm deletion
    if (!window.confirm(t('confirm_delete_meal') || 'Are you sure you want to delete this meal?')) {
      return;
    }

    const index = findScheduledMeal(existingConfig.id);
    if (index !== -1) {
      removeScheduledMeal(index);
    }
    closeConfigModal(true);  // Pass true since deletion is a successful action
  };

  const isMultiSession = cookingDates.length > 1;
  const hasPrepTasks = meal?.prep_tasks?.length > 0;

  if (!isOpen || !meal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">
            {existingConfig ? 'Edit Meal' : 'Configure Meal'}
          </h2>
          <p className="text-sm text-gray-600 mt-1">{meal.name}</p>
        </div>

        {/* Form */}
        <div className="p-6 space-y-6">
          {/* Cooking Dates */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cooking Dates
              {isMultiSession && (
                <span className="ml-2 text-xs text-orange-600">
                  (Multiple dates: cook fresh on each date)
                </span>
              )}
            </label>
            <div className="space-y-2">
              {cookingDates.map((date, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => handleDateChange(index, e.target.value)}
                    className="input-field flex-1"
                  />
                  {cookingDates.length > 1 && (
                    <button
                      onClick={() => handleRemoveCookingDate(index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={handleAddCookingDate}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                + Add Cooking Date
              </button>
            </div>
            {isMultiSession && (
              <p className="text-xs text-gray-500 mt-2">
                With multiple cooking dates, you'll cook 1 portion per person on each date (fresh cooking)
              </p>
            )}
          </div>

          {/* Servings Per Person */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Servings Per Person
            </label>
            <div className="space-y-3">
              {Object.entries(servingsPerPerson).map(([person, servings]) => (
                <div key={person} className="flex items-center justify-between bg-gray-50 rounded p-3">
                  <span className="text-sm font-medium text-gray-700">{person}</span>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleServingChange(person, -1)}
                      className="w-8 h-8 rounded bg-white border border-gray-300 hover:bg-gray-50 flex items-center justify-center font-semibold"
                      disabled={servings <= 0}
                    >
                      -
                    </button>
                    <span className="w-12 text-center font-semibold">{servings}</span>
                    <button
                      onClick={() => handleServingChange(person, 1)}
                      className="w-8 h-8 rounded bg-white border border-gray-300 hover:bg-gray-50 flex items-center justify-center font-semibold"
                      disabled={servings >= 10}
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Meal Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Meal Type
            </label>
            <select
              value={mealType}
              onChange={(e) => setMealType(e.target.value)}
              className="input-field w-full"
            >
              {MEAL_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Assigned Cook */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Assigned Cook
            </label>
            <select
              value={assignedCook}
              onChange={(e) => setAssignedCook(e.target.value)}
              className="input-field w-full"
            >
              {cooks.map(cook => (
                <option key={cook} value={cook}>
                  {cook}
                </option>
              ))}
            </select>
          </div>

          {/* Prep Assignment (conditional) */}
          {hasPrepTasks && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prep Assigned To
                <span className="ml-2 text-xs text-gray-500">
                  (This meal requires preparation)
                </span>
              </label>
              <select
                value={prepAssignedTo}
                onChange={(e) => setPrepAssignedTo(e.target.value)}
                className="input-field w-full"
              >
                {cooks.map(cook => (
                  <option key={cook} value={cook}>
                    {cook}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Validation Errors */}
          {validationErrors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded p-4">
              <h4 className="text-sm font-semibold text-red-800 mb-2">Validation Errors:</h4>
              <ul className="text-sm text-red-700 space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-between gap-3">
          {/* Delete button (only in edit mode) */}
          {existingConfig && (
            <button
              onClick={handleDelete}
              className="px-4 py-2 text-white bg-red-600 rounded hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          )}

          {/* Spacer when not in edit mode */}
          {!existingConfig && <div />}

          {/* Cancel and Save buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={validationErrors.length > 0}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {existingConfig ? 'Update' : 'Add to Calendar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
