/**
 * CalendarView - FullCalendar component with drag-and-drop support
 */
import { useRef, useMemo, useEffect, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import plLocale from '@fullcalendar/core/locales/pl';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';

// Meal type color mapping
const MEAL_TYPE_COLORS = {
  breakfast: '#fef3c7',
  second_breakfast: '#dbeafe',
  dinner: '#fecaca',
  supper: '#d1fae5',
  snack: '#e9d5ff',
};

export default function CalendarView() {
  const calendarRef = useRef(null);
  const { scheduledMeals, openConfigModal, getScheduledMealById, getMealNameSync, fetchMealName, language } = useMealPlan();

  // Track temporary preview event (for showing where meal will be placed)
  const [previewEvent, setPreviewEvent] = useState(null);

  // Prefetch meal names for all scheduled meals
  useEffect(() => {
    scheduledMeals.forEach(meal => {
      fetchMealName(meal.meal_id);
    });
  }, [scheduledMeals, fetchMealName]);

  /**
   * Transform scheduled meals into FullCalendar events
   * Include preview event if present
   */
  const events = useMemo(() => {
    const allEvents = [];

    scheduledMeals.forEach((meal) => {
      // Create an event for each cooking date
      const mealName = getMealNameSync(meal.meal_id);
      meal.cooking_dates.forEach((date, dateIndex) => {
        allEvents.push({
          id: `${meal.id}_${date}`,  // Use scheduled meal unique ID
          title: mealName,
          start: date,
          allDay: true,
          backgroundColor: MEAL_TYPE_COLORS[meal.meal_type] || '#e5e7eb',
          borderColor: '#9ca3af',
          extendedProps: {
            scheduled_meal_id: meal.id,  // Unique ID for this scheduled meal instance
            meal_id: meal.meal_id,  // Recipe reference
            meal_type: meal.meal_type,
            assigned_cook: meal.assigned_cook,
            servings_per_person: meal.servings_per_person,
            cooking_dates: meal.cooking_dates,
            is_meal_prep: meal.cooking_dates.length === 1,
            session_number: dateIndex + 1,
            total_sessions: meal.cooking_dates.length,
          }
        });
      });
    });

    // Add preview event if present
    if (previewEvent) {
      allEvents.push(previewEvent);
    }

    return allEvents;
  }, [scheduledMeals, getMealNameSync, previewEvent]);

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
        backgroundColor: '#e5e7eb',  // Gray for preview
        borderColor: '#9ca3af',
        textColor: '#6b7280',
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
    const { meal_type, assigned_cook, is_meal_prep, session_number, total_sessions } = eventInfo.event.extendedProps;

    return (
      <div className="p-1 text-xs">
        <div className="font-semibold truncate">{eventInfo.event.title}</div>
        <div className="text-gray-700 truncate">
          {assigned_cook && `👨‍🍳 ${assigned_cook}`}
        </div>
        {!is_meal_prep && total_sessions > 1 && (
          <div className="text-gray-600 text-[10px]">
            Session {session_number}/{total_sessions}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full bg-white rounded-lg shadow p-4">
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
        weekends={true}
        firstDay={1} // Monday
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
  );
}
