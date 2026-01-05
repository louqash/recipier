/**
 * MealConfigModal - Modal for configuring meals when dropped on calendar
 */
import { useState, useEffect, useMemo, useRef } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme.jsx';
import { configAPI } from '../../api/client';

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
  const { colors } = useTheme();

  // Dynamic meal types from translations
  const MEAL_TYPES = useMemo(() => [
    { value: 'breakfast', label: t('breakfast') },
    { value: 'second_breakfast', label: t('second_breakfast') },
    { value: 'dinner', label: t('dinner') },
    { value: 'supper', label: t('supper') },
  ], [t]);

  // Dynamic users from config
  const [availableUsers, setAvailableUsers] = useState([]);
  const [cooks, setCooks] = useState([]);
  const hasFetchedUsers = useRef(false);

  // Form state
  const [cookingDates, setCookingDates] = useState([]);
  const [servingsPerPerson, setServingsPerPerson] = useState({});
  const [lockedPersons, setLockedPersons] = useState({}); // Lock state for proportional scaling
  const [mealType, setMealType] = useState('dinner');
  const [assignedCook, setAssignedCook] = useState('');
  const [prepAssignedTo, setPrepAssignedTo] = useState('');
  const [validationErrors, setValidationErrors] = useState([]);

  // Fetch users from config on mount
  useEffect(() => {
    if (hasFetchedUsers.current) return;

    const fetchUsers = async () => {
      hasFetchedUsers.current = true;
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

        // Initialize default servings and locks (all locked by default)
        const defaultServings = {};
        const defaultLocks = {};
        users.forEach(user => {
          defaultServings[user] = 1;
          defaultLocks[user] = true; // All locked by default
        });
        setServingsPerPerson(defaultServings);
        setLockedPersons(defaultLocks);
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
      // Reset locks (all locked by default)
      const defaultLocks = {};
      availableUsers.forEach(user => {
        defaultLocks[user] = true;
      });
      setLockedPersons(defaultLocks);
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
    const newDates = [...cookingDates, newDate];
    setCookingDates(newDates);

    // Automatically adjust portions to match number of dates
    const numDates = newDates.length;
    setServingsPerPerson(prev => {
      const updated = {};
      Object.keys(prev).forEach(person => {
        updated[person] = numDates;
      });
      return updated;
    });
  };

  const handleRemoveCookingDate = (index) => {
    const newDates = cookingDates.filter((_, i) => i !== index);
    setCookingDates(newDates);

    // Automatically adjust portions to match number of dates
    const numDates = newDates.length;
    if (numDates > 0) {
      setServingsPerPerson(prev => {
        const updated = {};
        Object.keys(prev).forEach(person => {
          updated[person] = numDates;
        });
        return updated;
      });
    }
  };

  const handleDateChange = (index, newDate) => {
    const updated = [...cookingDates];
    updated[index] = newDate;
    setCookingDates(updated);
  };

  const handleServingChange = (person, delta) => {
    setServingsPerPerson(prev => {
      const oldValue = prev[person] || 0;
      const newValue = Math.max(0, Math.min(10, oldValue + delta));

      // If this person is not locked, just update them
      if (!lockedPersons[person]) {
        return {
          ...prev,
          [person]: newValue
        };
      }

      // If this person is locked, apply proportional change to all locked persons
      const ratio = oldValue > 0 ? newValue / oldValue : 0;
      const updated = { ...prev };

      // Apply ratio to all locked persons
      Object.keys(lockedPersons).forEach(p => {
        if (lockedPersons[p]) {
          const scaledValue = Math.round((prev[p] || 0) * ratio);
          updated[p] = Math.max(0, Math.min(10, scaledValue));
        }
      });

      return updated;
    });
  };

  const toggleLock = (person) => {
    setLockedPersons(prev => ({
      ...prev,
      [person]: !prev[person]
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
      <div className="rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4" style={{
        backgroundColor: colors.base
      }}>
        {/* Header */}
        <div className="sticky top-0 px-6 py-4" style={{
          backgroundColor: colors.base,
          borderBottom: `1px solid ${colors.surface0}`
        }}>
          <h2 className="text-xl font-semibold" style={{ color: colors.text }}>
            {t('configure_meal')}
          </h2>
          <p className="text-sm mt-1" style={{ color: colors.subtext1 }}>{t('meal_name')}: {meal.name}</p>
        </div>

        {/* Form */}
        <div className="p-6 space-y-6">
          {/* Cooking Dates */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text }}>
              {t('cooking_dates')}
              {isMultiSession && (
                <span className="ml-2 text-xs" style={{ color: colors.peach }}>
                  {t('multiple_dates_notice')}
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
                    style={{
                      backgroundColor: colors.surface0,
                      borderColor: colors.surface1,
                      color: colors.text,
                      colorScheme: colors.base === '#1e1e2e' ? 'dark' : 'light'
                    }}
                  />
                  {cookingDates.length > 1 && (
                    <button
                      onClick={() => handleRemoveCookingDate(index)}
                      className="px-3 py-2 rounded transition-colors"
                      style={{ color: colors.red }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      {t('cancel')}
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={handleAddCookingDate}
                className="text-sm font-medium"
                style={{ color: colors.blue }}
              >
                + {t('add_date')}
              </button>
            </div>
            {isMultiSession && (
              <p className="text-xs mt-2" style={{ color: colors.subtext0 }}>
                {t('multiple_dates_explanation')}
              </p>
            )}
          </div>

          {/* Servings Per Person */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text }}>
              {t('servings_per_person')}
            </label>
            <div className="space-y-3">
              {Object.entries(servingsPerPerson).map(([person, servings]) => (
                <div key={person} className="flex items-center justify-between rounded p-3" style={{
                  backgroundColor: colors.surface0
                }}>
                  <span className="text-sm font-medium" style={{ color: colors.text }}>{person}</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleLock(person)}
                      className="w-8 h-8 rounded flex items-center justify-center transition-colors"
                      style={{
                        backgroundColor: lockedPersons[person] ? colors.blue : colors.overlay0,
                        color: colors.base,
                        borderWidth: '1px',
                        borderStyle: 'solid',
                        borderColor: lockedPersons[person] ? colors.sapphire : colors.overlay1
                      }}
                      title={lockedPersons[person] ? t('portion_locked') : t('portion_unlocked')}
                    >
                      {lockedPersons[person] ? '🔗' : '🔓'}
                    </button>
                    <button
                      onClick={() => handleServingChange(person, -1)}
                      className="w-8 h-8 rounded flex items-center justify-center font-semibold"
                      style={{
                        backgroundColor: colors.base,
                        borderWidth: '1px',
                        borderStyle: 'solid',
                        borderColor: colors.surface1,
                        color: colors.text
                      }}
                      disabled={servings <= 0}
                    >
                      -
                    </button>
                    <span className="w-12 text-center font-semibold" style={{ color: colors.text }}>{servings}</span>
                    <button
                      onClick={() => handleServingChange(person, 1)}
                      className="w-8 h-8 rounded flex items-center justify-center font-semibold"
                      style={{
                        backgroundColor: colors.base,
                        borderWidth: '1px',
                        borderStyle: 'solid',
                        borderColor: colors.surface1,
                        color: colors.text
                      }}
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
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text }}>
              {t('meal_type')}
            </label>
            <select
              value={mealType}
              onChange={(e) => setMealType(e.target.value)}
              className="input-field w-full"
              style={{
                backgroundColor: colors.surface0,
                borderColor: colors.surface1,
                color: colors.text
              }}
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
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text }}>
              {t('who_cooks')}
            </label>
            <select
              value={assignedCook}
              onChange={(e) => setAssignedCook(e.target.value)}
              className="input-field w-full"
              style={{
                backgroundColor: colors.surface0,
                borderColor: colors.surface1,
                color: colors.text
              }}
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
              <label className="block text-sm font-medium mb-2" style={{ color: colors.text }}>
                {t('prep_assigned_to')}
                <span className="ml-2 text-xs" style={{ color: colors.subtext0 }}>
                  {t('meal_requires_prep')}
                </span>
              </label>
              <select
                value={prepAssignedTo}
                onChange={(e) => setPrepAssignedTo(e.target.value)}
                className="input-field w-full"
                style={{
                  backgroundColor: colors.surface0,
                  borderColor: colors.surface1,
                  color: colors.text
                }}
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
            <div className="rounded p-4" style={{
              backgroundColor: colors.red + '20',
              border: `1px solid ${colors.red}`
            }}>
              <h4 className="text-sm font-semibold mb-2" style={{ color: colors.red }}>{t('validation_error')}:</h4>
              <ul className="text-sm space-y-1" style={{ color: colors.red }}>
                {validationErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 px-6 py-4 flex justify-between gap-3" style={{
          backgroundColor: colors.surface0,
          borderTop: `1px solid ${colors.surface1}`
        }}>
          {/* Delete button (only in edit mode) */}
          {existingConfig && (
            <button
              onClick={handleDelete}
              className="px-4 py-2 rounded transition-colors"
              style={{
                backgroundColor: colors.red,
                color: colors.base
              }}
            >
              {t('delete')}
            </button>
          )}

          {/* Spacer when not in edit mode */}
          {!existingConfig && <div />}

          {/* Cancel and Save buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2 rounded transition-colors"
              style={{
                backgroundColor: colors.base,
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: colors.surface1,
                color: colors.text
              }}
            >
              {t('cancel')}
            </button>
            <button
              onClick={handleSave}
              disabled={validationErrors.length > 0}
              className="px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              style={{
                backgroundColor: colors.blue,
                color: colors.base
              }}
            >
              {t('save_meal')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
