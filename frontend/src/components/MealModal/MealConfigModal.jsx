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
    removeScheduledMeal,
    setDietProfiles
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
  const [eatingDatesPerPerson, setEatingDatesPerPerson] = useState({});
  const [lockedEatingDates, setLockedEatingDates] = useState(true); // Global lock for eating dates sync
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
        const profiles = response.diet_profiles || {};

        if (users.length === 0) {
          console.error('No users configured in config file');
          alert('No users configured. Please set up user_mapping in config file.');
          return;
        }

        setAvailableUsers(users);
        setCooks([...users, 'Both']);
        setDietProfiles(profiles); // Store diet profiles in context

        // Set default values once users are loaded
        setAssignedCook(users[0]);
        setPrepAssignedTo(users[0]);

        // Initialize default eating dates (empty, will be set when modal opens)
        const defaultEatingDates = {};
        users.forEach(user => {
          defaultEatingDates[user] = [];
        });
        setEatingDatesPerPerson(defaultEatingDates);
        setLockedEatingDates(true); // All locked by default
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
        setEatingDatesPerPerson(existingConfig.eating_dates_per_person || createDefaultEatingDates(existingConfig.cooking_dates));
        setMealType(existingConfig.meal_type || 'dinner');
        setAssignedCook(existingConfig.assigned_cook || availableUsers[0]);
        setPrepAssignedTo(existingConfig.prep_assigned_to || availableUsers[0]);
      } else {
        // New meal - initialize with dropped date
        const initialCookingDates = initialDate ? [initialDate] : [];
        setCookingDates(initialCookingDates);
        setEatingDatesPerPerson(createDefaultEatingDates(initialCookingDates));
        setMealType('dinner');
        setAssignedCook(availableUsers[0]);
        setPrepAssignedTo(availableUsers[0]);
      }
      setLockedEatingDates(true); // Always start locked
      setValidationErrors([]);
    }
  }, [isOpen, initialDate, existingConfig, availableUsers]);

  // Helper to create default eating dates
  const createDefaultEatingDates = (cookingDates = []) => {
    const defaults = {};
    const firstDate = cookingDates.length > 0 ? cookingDates[0] : null;
    availableUsers.forEach(user => {
      defaults[user] = firstDate ? [firstDate] : [];
    });
    return defaults;
  };

  // Validate configuration in real-time
  useEffect(() => {
    if (!isOpen) return;

    const errors = [];
    const numCookingDates = cookingDates.length;
    const firstCookingDate = cookingDates.length > 0 ? cookingDates.sort()[0] : null;

    if (numCookingDates === 0) {
      errors.push(t('At least one cooking date is required'));
    }

    // Validate eating dates
    Object.entries(eatingDatesPerPerson).forEach(([person, dates]) => {
      if (!dates || dates.length === 0) {
        errors.push(t('error_person_no_eating_dates').replace('{person}', person));
      }

      dates.forEach(date => {
        if (firstCookingDate && date < firstCookingDate) {
          errors.push(
            t('error_eating_before_cooking')
              .replace('{person}', person)
              .replace('{eating_date}', date)
              .replace('{cooking_date}', firstCookingDate)
          );
        }
      });

      if (numCookingDates > 1 && dates.length % numCookingDates !== 0) {
        errors.push(
          t('error_eating_dates_not_divisible')
            .replace('{person}', person)
            .replace('{num_eating}', dates.length)
            .replace('{num_cooking}', numCookingDates)
        );
      }
    });

    setValidationErrors(errors);
  }, [cookingDates, eatingDatesPerPerson, isOpen, t]);

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

    // AUTO-ADD eating date for all users (day after last eating date)
    setEatingDatesPerPerson(prev => {
      const updated = {};
      Object.keys(prev).forEach(person => {
        const userDates = [...(prev[person] || [])].sort();
        const lastEatingDate = userDates.length > 0 ? userDates[userDates.length - 1] : newDate;
        const nextDate = new Date(lastEatingDate);
        nextDate.setDate(nextDate.getDate() + 1);
        const nextDateStr = nextDate.toISOString().split('T')[0];
        updated[person] = [...(prev[person] || []), nextDateStr];
      });
      return updated;
    });
  };

  const handleRemoveCookingDate = (index) => {
    const newDates = cookingDates.filter((_, i) => i !== index);
    setCookingDates(newDates);

    // Also remove the corresponding eating date at the same index for all people
    setEatingDatesPerPerson(prev => {
      const updated = {};
      Object.keys(prev).forEach(person => {
        updated[person] = (prev[person] || []).filter((_, i) => i !== index);
      });
      return updated;
    });
  };

  const handleDateChange = (index, newDate) => {
    const updated = [...cookingDates];
    updated[index] = newDate;
    setCookingDates(updated);
  };

  const handleAddEatingDate = (person) => {
    setEatingDatesPerPerson(prev => {
      const userDates = [...(prev[person] || [])].sort();
      const lastDate = userDates.length > 0
        ? new Date(userDates[userDates.length - 1])
        : new Date(cookingDates[0] || new Date());
      lastDate.setDate(lastDate.getDate() + 1);
      const newDateStr = lastDate.toISOString().split('T')[0];

      if (lockedEatingDates) {
        // Add to all users
        const updated = {};
        Object.keys(prev).forEach(p => {
          updated[p] = [...(prev[p] || []), newDateStr];
        });
        return updated;
      } else {
        // Add only to this user
        return {
          ...prev,
          [person]: [...(prev[person] || []), newDateStr]
        };
      }
    });
  };

  const handleRemoveEatingDate = (person, index) => {
    setEatingDatesPerPerson(prev => {
      if (lockedEatingDates) {
        // Remove from all users (same index)
        const updated = {};
        Object.keys(prev).forEach(p => {
          updated[p] = (prev[p] || []).filter((_, i) => i !== index);
        });
        return updated;
      } else {
        // Remove only from this user
        return {
          ...prev,
          [person]: (prev[person] || []).filter((_, i) => i !== index)
        };
      }
    });
  };

  const handleEatingDateChange = (person, index, newDate) => {
    setEatingDatesPerPerson(prev => {
      if (lockedEatingDates) {
        // Update all people's dates at this index
        const updated = {};
        Object.keys(prev).forEach(p => {
          updated[p] = (prev[p] || []).map((date, i) => i === index ? newDate : date);
        });
        return updated;
      } else {
        // Update only this person's date
        return {
          ...prev,
          [person]: (prev[person] || []).map((date, i) => i === index ? newDate : date)
        };
      }
    });
  };

  // Helper to adjust date by days
  const adjustDate = (dateStr, days) => {
    const date = new Date(dateStr);
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
  };

  const handleCookingDatePrevNext = (index, days) => {
    const updated = [...cookingDates];
    updated[index] = adjustDate(updated[index], days);
    setCookingDates(updated);
  };

  const handleEatingDatePrevNext = (person, index, days) => {
    const currentDate = eatingDatesPerPerson[person]?.[index];
    if (!currentDate) return;
    const newDate = adjustDate(currentDate, days);
    handleEatingDateChange(person, index, newDate);
  };

  const handleSave = () => {
    if (validationErrors.length > 0) {
      return; // Don't save if there are validation errors
    }

    const config = {
      meal_id: meal?.meal_id,
      cooking_dates: cookingDates.sort(),
      eating_dates_per_person: eatingDatesPerPerson,
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
                  <button
                    onClick={() => handleCookingDatePrevNext(index, -1)}
                    className="px-2 py-2 rounded transition-colors text-sm font-medium"
                    style={{
                      backgroundColor: colors.surface0,
                      color: colors.text,
                      border: `1px solid ${colors.surface1}`
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface1}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                    title="Previous day"
                  >
                    ←
                  </button>
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
                  <button
                    onClick={() => handleCookingDatePrevNext(index, 1)}
                    className="px-2 py-2 rounded transition-colors text-sm font-medium"
                    style={{
                      backgroundColor: colors.surface0,
                      color: colors.text,
                      border: `1px solid ${colors.surface1}`
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface1}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                    title="Next day"
                  >
                    →
                  </button>
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

          {/* Eating Dates Per Person */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium" style={{ color: colors.text }}>
                {t('eating_dates')}
              </label>
              <button
                onClick={() => setLockedEatingDates(!lockedEatingDates)}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors"
                style={{
                  backgroundColor: lockedEatingDates ? colors.blue : colors.overlay0,
                  color: lockedEatingDates ? colors.base : colors.text,
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: lockedEatingDates ? colors.sapphire : colors.overlay1
                }}
                title={lockedEatingDates ? t('eating_dates_locked') : t('eating_dates_unlocked')}
              >
                {lockedEatingDates ? '🔗' : '🔓'}
                <span>{t(lockedEatingDates ? 'eating_dates_locked' : 'eating_dates_unlocked')}</span>
              </button>
            </div>

            {Object.entries(eatingDatesPerPerson).map(([person, dates]) => (
              <div key={person} className="mb-3 p-3 rounded" style={{ backgroundColor: colors.surface0 }}>
                <div className="text-sm font-medium mb-2" style={{ color: colors.text }}>{person}</div>
                <div className="space-y-2">
                  {(dates || []).map((date, index) => (
                    <div key={index} className="flex gap-2">
                      <button
                        onClick={() => handleEatingDatePrevNext(person, index, -1)}
                        className="px-2 py-2 rounded transition-colors text-sm font-medium"
                        style={{
                          backgroundColor: colors.surface0,
                          color: colors.text,
                          border: `1px solid ${colors.surface1}`
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface1}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                        title="Previous day"
                      >
                        ←
                      </button>
                      <input
                        type="date"
                        value={date}
                        onChange={(e) => handleEatingDateChange(person, index, e.target.value)}
                        min={cookingDates.length > 0 ? cookingDates[0] : undefined}
                        className="input-field flex-1"
                        style={{
                          backgroundColor: colors.base,
                          borderColor: colors.surface1,
                          color: colors.text,
                          colorScheme: colors.base === '#1e1e2e' ? 'dark' : 'light'
                        }}
                      />
                      <button
                        onClick={() => handleEatingDatePrevNext(person, index, 1)}
                        className="px-2 py-2 rounded transition-colors text-sm font-medium"
                        style={{
                          backgroundColor: colors.surface0,
                          color: colors.text,
                          border: `1px solid ${colors.surface1}`
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface1}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                        title="Next day"
                      >
                        →
                      </button>
                      {dates.length > 1 && (
                        <button
                          onClick={() => handleRemoveEatingDate(person, index)}
                          className="px-3 py-2 rounded transition-colors text-sm"
                          style={{ color: colors.red }}
                          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        >
                          {t('remove')}
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => handleAddEatingDate(person)}
                    className="text-sm font-medium"
                    style={{ color: colors.blue }}
                  >
                    + {t('add_eating_date')}
                  </button>
                </div>
              </div>
            ))}
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
