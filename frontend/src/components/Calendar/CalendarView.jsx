/**
 * CalendarView - FullCalendar component with drag-and-drop support
 */
import { useRef, useMemo, useEffect, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import plLocale from '@fullcalendar/core/locales/pl';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';
import { useTheme } from '../../hooks/useTheme.jsx';
import { useTranslation } from '../../hooks/useTranslation';
import { useMeals } from '../../hooks/useMeals';
import RoundingWarningModal from '../RoundingWarningModal/RoundingWarningModal';

export default function CalendarView() {
  const calendarRef = useRef(null);
  const { scheduledMeals, openConfigModal, getScheduledMealById, getMealNameSync, fetchMealName, language, dietProfiles, mealNutrition, roundingWarnings } = useMealPlan();
  const { mealColors, colors } = useTheme();
  const { t } = useTranslation();
  const { meals: allMeals } = useMeals('');

  // Track temporary preview event (for showing where meal will be placed)
  const [previewEvent, setPreviewEvent] = useState(null);
  const [showWarningsModal, setShowWarningsModal] = useState(false);

  // Prefetch meal names for all scheduled meals
  useEffect(() => {
    scheduledMeals.forEach(meal => {
      fetchMealName(meal.meal_id);
    });
  }, [scheduledMeals, fetchMealName]);

  // Calculate daily nutrition totals per profile (BASED ON EATING DATES) using backend nutrition
  const dailyNutritionTotals = useMemo(() => {
    if (!mealNutrition || Object.keys(mealNutrition).length === 0) {
      return {};
    }

    // { "2026-01-05": { "high_calorie": {calories, fat, protein, carbs}, "low_calorie": {...} } }
    const totals = {};

    scheduledMeals.forEach(scheduledMeal => {
      const mealId = scheduledMeal.id;
      const nutrition = mealNutrition[mealId];

      if (!nutrition) return;

      // Get eating dates per person
      const eatingDatesPerPerson = scheduledMeal.eating_dates_per_person || {};

      // For each person, add nutrition per eating date
      Object.entries(eatingDatesPerPerson).forEach(([person, eatingDates]) => {
        // Map person to their diet profile
        const profile = dietProfiles[person] || person;

        // Backend returns nutrition keyed by PROFILE name (duża porcja, mała porcja)
        if (!nutrition[profile]) return;

        const personNutrition = nutrition[profile];

        // Backend returns TOTAL nutrition for all portions
        // Divide by number of eating dates to get per-portion nutrition
        const numPortions = eatingDates.length;
        if (numPortions === 0) return;

        const perPortionNutrition = {
          calories: (personNutrition.calories || 0) / numPortions,
          fat: (personNutrition.fat || 0) / numPortions,
          protein: (personNutrition.protein || 0) / numPortions,
          carbs: (personNutrition.carbs || 0) / numPortions
        };

        // Each eating date gets one portion
        eatingDates.forEach(date => {
          if (!totals[date]) {
            totals[date] = {};
          }
          if (!totals[date][profile]) {
            totals[date][profile] = {
              calories: 0,
              fat: 0,
              protein: 0,
              carbs: 0
            };
          }

          // Add per-portion nutrition values to this date
          totals[date][profile].calories += perPortionNutrition.calories;
          totals[date][profile].fat += perPortionNutrition.fat;
          totals[date][profile].protein += perPortionNutrition.protein;
          totals[date][profile].carbs += perPortionNutrition.carbs;
        });
      });
    });

    return totals;
  }, [scheduledMeals, mealNutrition, dietProfiles]);

  /**
   * Get meal type order for sorting events
   */
  const getMealTypeOrder = (mealType) => {
    const orderMap = {
      'breakfast': 1,
      'second_breakfast': 2,
      'dinner': 3,
      'supper': 4
    };
    return orderMap[mealType] || 5;
  };

  /**
   * Transform scheduled meals into FullCalendar events
   * Include preview event if present
   */
  const events = useMemo(() => {
    const allEvents = [];

    scheduledMeals.forEach((meal) => {
      const mealName = getMealNameSync(meal.meal_id);
      const cookingDatesSet = new Set(meal.cooking_dates);

      // Create an event for each cooking date
      meal.cooking_dates.forEach((date, dateIndex) => {
        // Check who's eating on this cooking date
        const eatingDatesPerPerson = meal.eating_dates_per_person || {};
        const peopleEatingToday = [];
        Object.entries(eatingDatesPerPerson).forEach(([person, dates]) => {
          if (dates.includes(date)) {
            peopleEatingToday.push(person);
          }
        });

        allEvents.push({
          id: `${meal.id}_cook_${date}`,
          title: mealName,
          start: date,
          allDay: true,
          backgroundColor: mealColors[meal.meal_type] || colors.surface0,
          borderColor: colors.overlay0,
          extendedProps: {
            scheduled_meal_id: meal.id,
            meal_id: meal.meal_id,
            meal_type: meal.meal_type,
            assigned_cook: meal.assigned_cook,
            cooking_dates: meal.cooking_dates,
            is_meal_prep: meal.cooking_dates.length === 1,
            session_number: dateIndex + 1,
            total_sessions: meal.cooking_dates.length,
            event_type: 'cooking',
            eating_people_today: peopleEatingToday,
            mealTypeOrder: getMealTypeOrder(meal.meal_type),
            eventTypeOrder: 1, // Cooking events before eating events
          }
        });
      });

      // Create eating events for non-cooking dates
      const eatingDatesPerPerson = meal.eating_dates_per_person || {};
      const eatingDatesToPeople = {}; // Group people by eating date

      Object.entries(eatingDatesPerPerson).forEach(([person, dates]) => {
        dates.forEach(date => {
          // Only create eating event if it's NOT a cooking date
          if (!cookingDatesSet.has(date)) {
            if (!eatingDatesToPeople[date]) {
              eatingDatesToPeople[date] = [];
            }
            eatingDatesToPeople[date].push(person);
          }
        });
      });

      // Create eating events
      Object.entries(eatingDatesToPeople).forEach(([date, people]) => {
        allEvents.push({
          id: `${meal.id}_eat_${date}`,
          title: `🍽️ ${mealName}`,
          start: date,
          allDay: true,
          backgroundColor: colors.surface1,
          borderColor: mealColors[meal.meal_type] || colors.overlay1, // Colored border matching meal type
          textColor: colors.text,
          classNames: ['eating-event'], // Custom class for wider border
          extendedProps: {
            scheduled_meal_id: meal.id,
            meal_id: meal.meal_id,
            meal_type: meal.meal_type,
            eating_people: people,
            assigned_cook: meal.assigned_cook, // Add assigned cook
            event_type: 'eating',
            mealTypeOrder: getMealTypeOrder(meal.meal_type),
            eventTypeOrder: 2, // Eating events after cooking events
          }
        });
      });
    });

    // Add preview event if present
    if (previewEvent) {
      allEvents.push(previewEvent);
    }

    return allEvents;
  }, [scheduledMeals, getMealNameSync, previewEvent, mealColors, colors]);

  /**
   * Handle external meal drop from MealsLibrary
   */
  const handleDrop = async (info) => {
    try {
      // Get meal data from the dragged element's dataset
      const mealDataStr = info.draggedEl?.dataset?.mealData;

      if (!mealDataStr) {
        console.error('No meal data found on dragged element');
        return;
      }

      const mealData = JSON.parse(mealDataStr);
      const mealId = mealData.meal_id;
      const mealName = mealData.meal_name;

      if (!mealId) {
        console.error('No meal_id in meal data');
        return;
      }

      // Create preview event to show placement while modal is open
      const preview = {
        id: 'preview-event',
        title: mealName || mealId,
        start: info.dateStr,
        allDay: true,
        backgroundColor: colors.surface0,
        borderColor: colors.overlay0,
        textColor: colors.subtext0,
        classNames: ['preview-event'],
        extendedProps: {
          isPreview: true
        }
      };
      setPreviewEvent(preview);

      // Open configuration modal and wait for result
      const saved = await openConfigModal(mealId, info.dateStr);

      // Remove preview event after modal closes (whether saved or cancelled)
      setPreviewEvent(null);

    } catch (error) {
      console.error('Error handling drop:', error);
      alert(`Failed to open meal configuration: ${error.message}`);
      // Remove preview event on error
      setPreviewEvent(null);
    }
  };

  /**
   * Handle event (meal) click to edit
   */
  const handleEventClick = (info) => {
    // Ignore clicks on preview events
    if (info.event.extendedProps.isPreview) {
      return;
    }

    const { scheduled_meal_id, meal_id } = info.event.extendedProps;
    const existingMeal = getScheduledMealById(scheduled_meal_id);

    if (existingMeal) {
      // Open modal with existing configuration
      openConfigModal(meal_id, null, existingMeal);
    }
  };

  /**
   * Render event content
   */
  const renderEventContent = (eventInfo) => {
    const { event_type, assigned_cook, is_meal_prep, session_number, total_sessions, eating_people, eating_people_today } = eventInfo.event.extendedProps;

    if (event_type === 'eating') {
      // Eating event
      return (
        <div className="p-1 text-xs" style={{ color: colors.text }}>
          <div className="font-semibold truncate">{eventInfo.event.title}</div>
          {assigned_cook && (
            <div className="truncate" style={{ opacity: 0.8 }}>
              👨‍🍳 {assigned_cook}
            </div>
          )}
          <div className="truncate" style={{ opacity: 0.8 }}>
            🍽️ {eating_people && eating_people.join(', ')}
          </div>
        </div>
      );
    }

    // Cooking event
    return (
      <div className="p-1 text-xs" style={{ color: '#1a1a1a' }}>
        <div className="font-semibold truncate">{eventInfo.event.title}</div>
        <div className="truncate" style={{ opacity: 0.8 }}>
          {assigned_cook && `👨‍🍳 ${assigned_cook}`}
        </div>
        {eating_people_today && eating_people_today.length > 0 && (
          <div className="truncate" style={{ opacity: 0.8 }}>
            🍽️ {eating_people_today.join(', ')}
          </div>
        )}
        {!is_meal_prep && total_sessions > 1 && (
          <div className="text-[10px]" style={{ opacity: 0.7 }}>
            Session {session_number}/{total_sessions}
          </div>
        )}
      </div>
    );
  };

  /**
   * Render day cell content with nutrition totals
   */
  const renderDayCellContent = (dayCellInfo) => {
    // Format date in local time to avoid timezone issues
    const year = dayCellInfo.date.getFullYear();
    const month = String(dayCellInfo.date.getMonth() + 1).padStart(2, '0');
    const day = String(dayCellInfo.date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    const nutritionTotals = dailyNutritionTotals[dateStr];

    return (
      <div className="flex flex-col h-full">
        {/* Date number */}
        <div className="fc-daygrid-day-top">
          <span className="fc-daygrid-day-number">{dayCellInfo.dayNumberText}</span>
        </div>

        {/* Daily nutrition totals */}
        {nutritionTotals && Object.keys(nutritionTotals).length > 0 && (
          <div
            className="mt-1 mb-2 mx-1 px-2 py-1 rounded text-[10px] leading-tight"
            style={{
              backgroundColor: colors.surface0,
              color: colors.text,
              border: `1px solid ${colors.surface1}`
            }}
          >
            {Object.entries(nutritionTotals).map(([profile, nutrition]) => (
              <div key={profile} className="space-y-0.5">
                <div className="truncate font-semibold">
                  {profile}: {Math.round(nutrition.calories)} kcal
                </div>
                <div className="truncate text-[9px]" style={{ color: colors.subtext0 }}>
                  {t('fat_short')}: {Math.round(nutrition.fat)}g · {t('protein_short')}: {Math.round(nutrition.protein)}g · {t('carbs_short')}: {Math.round(nutrition.carbs)}g
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full rounded-lg shadow p-4 flex flex-col" style={{ backgroundColor: colors.base }}>
      {/* Rounding Warnings Banner */}
      {roundingWarnings && roundingWarnings.length > 0 && (
        <div
          className="mb-6 p-3 rounded-lg flex items-start gap-3 cursor-pointer hover:opacity-90 transition-opacity"
          style={{
            backgroundColor: colors.yellow + '20',
            border: `1px solid ${colors.yellow}`
          }}
          onClick={() => setShowWarningsModal(true)}
        >
          <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20" style={{ color: colors.yellow }}>
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div className="flex-1">
            <div className="font-semibold text-sm mb-1" style={{ color: colors.text }}>
              {roundingWarnings.length === 1
                ? t('one_rounding_warning')
                : t('multiple_rounding_warnings').replace('{count}', roundingWarnings.length)}
            </div>
            <div className="text-xs" style={{ color: colors.subtext0 }}>
              {t('click_to_view_details')}
            </div>
          </div>
        </div>
      )}

      {/* Color Legend */}
      <div className="mb-3 flex flex-wrap gap-3 text-xs" style={{ color: colors.subtext1 }}>
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: mealColors.breakfast }}></div>
          <span>{t('breakfast')}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: mealColors.second_breakfast }}></div>
          <span>{t('second_breakfast')}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: mealColors.dinner }}></div>
          <span>{t('dinner')}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: mealColors.supper }}></div>
          <span>{t('supper')}</span>
        </div>
        <div className="flex items-center gap-1.5" style={{ borderLeft: `1px solid ${colors.overlay0}`, paddingLeft: '12px' }}>
          <div className="w-4 h-4 rounded flex items-center justify-center text-[10px]" style={{ backgroundColor: colors.surface1 }}>🍽️</div>
          <span>{t('eating')}</span>
        </div>
      </div>

      <style>{`
        /* Calendar text colors */
        .fc {
          color: ${colors.text};
        }
        .fc .fc-col-header-cell-cushion {
          color: ${colors.text};
        }
        .fc .fc-daygrid-day-number {
          color: ${colors.text};
        }
        .fc .fc-toolbar-title {
          color: ${colors.text};
        }
        /* Toolbar buttons */
        .fc .fc-button {
          background-color: ${colors.surface0};
          border-color: ${colors.surface1};
          color: ${colors.text};
        }
        .fc .fc-button:hover {
          background-color: ${colors.surface1};
          border-color: ${colors.surface2};
          color: ${colors.text};
        }
        .fc .fc-button:disabled {
          opacity: 0.5;
        }
        .fc .fc-button-primary:not(:disabled):active,
        .fc .fc-button-primary:not(:disabled).fc-button-active {
          background-color: ${colors.blue};
          border-color: ${colors.blue};
          color: ${colors.base};
        }
        /* Grid borders */
        .fc .fc-scrollgrid {
          border-color: ${colors.surface0};
        }
        .fc td, .fc th {
          border-color: ${colors.surface0};
        }
        /* Day cell background */
        .fc .fc-daygrid-day {
          background-color: ${colors.base};
        }
        .fc .fc-day-today {
          background-color: ${colors.surface0} !important;
        }
        /* Eating events - wider border */
        .fc .eating-event {
          border-width: 3px !important;
        }
      `}</style>

      <div className="flex-1 overflow-hidden">
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, interactionPlugin]}
          initialView="dayGridWeek"
          locale={language === 'polish' ? plLocale : 'en'}
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridWeek,dayGridMonth'
          }}
          height="100%"
          editable={false}
          droppable={true}
          drop={handleDrop}
          eventClick={handleEventClick}
          events={events}
          eventContent={renderEventContent}
          dayCellContent={renderDayCellContent}
          weekends={true}
          firstDay={1} // Monday
          eventOrder="mealTypeOrder,eventTypeOrder" // Sort by meal time, then cooking before eating
          // Date formatting
          titleFormat={{ year: 'numeric', month: 'short', day: 'numeric' }}
          dayHeaderFormat={{ weekday: 'short', day: 'numeric', month: 'short' }}
          eventTimeFormat={{
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false
          }}
        />
      </div>

      {/* Rounding Warning Modal */}
      <RoundingWarningModal
        isOpen={showWarningsModal}
        onClose={() => setShowWarningsModal(false)}
        onContinue={() => setShowWarningsModal(false)}
        warnings={roundingWarnings}
        viewOnly={true}
      />
    </div>
  );
}
