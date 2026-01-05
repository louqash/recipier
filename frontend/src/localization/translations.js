/**
 * Frontend translations for Recipier
 * Supports Polish and English
 */

export const translations = {
  polish: {
    // App title
    app_title: 'Recipier',

    // Action Bar
    save: 'Zapisz',
    load: 'Wczytaj',
    generate_tasks: 'Generuj zadania',
    settings: 'Ustawienia',

    // Settings Modal
    settings_title: 'Ustawienia',
    todoist_token_label: 'Token API Todoist',
    todoist_token_placeholder: 'Wklej swój token API',
    get_token_instructions: 'Pobierz swój token z',
    todoist_developer_settings: 'ustawień developerskich Todoist',
    close: 'Zamknij',

    // Meal Config Modal
    configure_meal: 'Konfiguruj posiłek',
    meal_name: 'Nazwa posiłku',
    cooking_dates: 'Daty gotowania',
    is_meal_prep: 'Czy to meal prep?',
    meal_prep_description: 'Gotowane raz na kilka dni',
    how_many_cooking_dates: 'Ile dat gotowania?',
    add_date: 'Dodaj datę',
    servings_per_person: 'Porcje na osobę',
    meal_type: 'Typ posiłku',
    breakfast: 'Śniadanie',
    second_breakfast: 'Drugie śniadanie',
    dinner: 'Obiad',
    supper: 'Kolacja',
    who_cooks: 'Kto gotuje?',
    cancel: 'Anuluj',
    save_meal: 'Zapisz posiłek',
    validation_error: 'Błąd walidacji',
    confirm_delete_meal: 'Czy na pewno chcesz usunąć ten posiłek?',
    delete: 'Usuń',
    multiple_dates_notice: '(Kilka dat: gotuj świeżo w każdej dacie)',
    multiple_dates_explanation: 'Z kilkoma datami gotowania, przygotujesz 1 porcję na osobę w każdej dacie (świeże gotowanie)',
    prep_assigned_to: 'Przygotowanie przypisane do',
    meal_requires_prep: '(Ten posiłek wymaga przygotowania)',
    portion_locked: 'Zablokowane (skalowanie proporcjonalne)',
    portion_unlocked: 'Odblokowane (niezależne)',

    // Shopping Manager
    shopping_trips: 'Zakupy',
    add_shopping_trip: 'Dodaj zakupy',
    shopping_date: 'Data zakupów',
    add: 'Dodaj',
    no_shopping_trips: 'Brak zaplanowanych zakupów.',
    add_trip_instruction: 'Dodaj zakupy i użyj przycisku ➕ aby dodać posiłki.',
    click_plus_to_add: 'Kliknij przycisk ➕ na zakupach aby dodać posiłki',
    add_meals: 'Dodaj posiłki',
    delete_trip: 'Usuń zakupy',
    no_meals_yet: 'Brak posiłków',
    select_meals_to_add: 'Wybierz posiłki do dodania:',
    no_meals_scheduled: 'Brak zaplanowanych posiłków',
    meal_in_other_trip: 'Ten posiłek jest już przypisany do innych zakupów',
    more_dates: 'i {count} inne',  // "+N more dates" truncation
    meal_count_singular: 'posiłek',
    meal_count_plural: 'posiłki',
    meal_count_many: 'posiłków',
    shopping_count_singular: 'zakupy',
    shopping_count_plural: 'zakupy',
    shopping_count_many: 'zakupów',

    // Meals Library
    meals_library: 'Biblioteka posiłków',
    search_meals: 'Szukaj posiłków...',
    loading_meals: 'Wczytywanie posiłków...',
    no_meals_found: 'Nie znaleziono posiłków',
    drag_to_calendar: 'Przeciągnij na kalendarz',
    base_servings: 'Porcje bazowe:',
    ingredient_count_singular: 'składnik',
    ingredient_count_plural: 'składniki',
    ingredient_count_many: 'składników',
    requires_prep: 'Wymaga przygotowania',

    // Calendar
    week: 'Tydzień',
    month: 'Miesiąc',
    today: 'Dziś',

    // Toast messages
    meal_plan_saved: 'Plan posiłków zapisany',
    meal_plan_loaded: 'Plan posiłków wczytany',
    tasks_generated: 'Zadania utworzone w Todoist',
    error_saving: 'Błąd podczas zapisywania',
    error_loading: 'Błąd podczas wczytywania',
    error_generating_tasks: 'Błąd podczas tworzenia zadań',
    todoist_token_required: 'Wymagany token Todoist',

    // Days of week
    monday: 'Pon',
    tuesday: 'Wt',
    wednesday: 'Śr',
    thursday: 'Czw',
    friday: 'Pt',
    saturday: 'Sob',
    sunday: 'Nie',
  },

  english: {
    // App title
    app_title: 'Recipier',

    // Action Bar
    save: 'Save',
    load: 'Load',
    generate_tasks: 'Generate Tasks',
    settings: 'Settings',

    // Settings Modal
    settings_title: 'Settings',
    todoist_token_label: 'Todoist API Token',
    todoist_token_placeholder: 'Paste your API token',
    get_token_instructions: 'Get your token from',
    todoist_developer_settings: 'Todoist developer settings',
    close: 'Close',

    // Meal Config Modal
    configure_meal: 'Configure Meal',
    meal_name: 'Meal Name',
    cooking_dates: 'Cooking Dates',
    is_meal_prep: 'Is this meal prep?',
    meal_prep_description: 'Cooked once for multiple days',
    how_many_cooking_dates: 'How many cooking dates?',
    add_date: 'Add Date',
    servings_per_person: 'Servings per Person',
    meal_type: 'Meal Type',
    breakfast: 'Breakfast',
    second_breakfast: '2nd Breakfast',
    dinner: 'Dinner',
    supper: 'Supper',
    who_cooks: 'Who cooks?',
    cancel: 'Cancel',
    save_meal: 'Save Meal',
    validation_error: 'Validation Error',
    confirm_delete_meal: 'Are you sure you want to delete this meal?',
    delete: 'Delete',
    multiple_dates_notice: '(Multiple dates: cook fresh on each date)',
    multiple_dates_explanation: 'With multiple cooking dates, you\'ll cook 1 portion per person on each date (fresh cooking)',
    prep_assigned_to: 'Prep Assigned To',
    meal_requires_prep: '(This meal requires preparation)',
    portion_locked: 'Locked (proportional scaling)',
    portion_unlocked: 'Unlocked (independent)',

    // Shopping Manager
    shopping_trips: 'Shopping Trips',
    add_shopping_trip: 'Add Shopping Trip',
    shopping_date: 'Shopping Date',
    add: 'Add',
    no_shopping_trips: 'No shopping trips yet.',
    add_trip_instruction: 'Add a trip and use the ➕ button to add meals.',
    click_plus_to_add: 'Click the ➕ button on a shopping trip to add meals',
    add_meals: 'Add meals',
    delete_trip: 'Delete trip',
    no_meals_yet: 'No meals yet',
    select_meals_to_add: 'Select meals to add:',
    no_meals_scheduled: 'No meals scheduled',
    meal_in_other_trip: 'This meal is already assigned to another shopping trip',
    more_dates: '+{count} more',  // "+N more dates" truncation
    meal_count_singular: 'meal',
    meal_count_plural: 'meals',
    meal_count_many: 'meals',
    shopping_count_singular: 'shopping trip',
    shopping_count_plural: 'shopping trips',
    shopping_count_many: 'shopping trips',

    // Meals Library
    meals_library: 'Meals Library',
    search_meals: 'Search meals...',
    loading_meals: 'Loading meals...',
    no_meals_found: 'No meals found',
    drag_to_calendar: 'Drag to calendar',
    base_servings: 'Base servings:',
    ingredient_count_singular: 'ingredient',
    ingredient_count_plural: 'ingredients',
    ingredient_count_many: 'ingredients',
    requires_prep: 'Requires prep',

    // Calendar
    week: 'Week',
    month: 'Month',
    today: 'Today',

    // Toast messages
    meal_plan_saved: 'Meal plan saved',
    meal_plan_loaded: 'Meal plan loaded',
    tasks_generated: 'Tasks created in Todoist',
    error_saving: 'Error saving',
    error_loading: 'Error loading',
    error_generating_tasks: 'Error generating tasks',
    todoist_token_required: 'Todoist token required',

    // Days of week
    monday: 'Mon',
    tuesday: 'Tue',
    wednesday: 'Wed',
    thursday: 'Thu',
    friday: 'Fri',
    saturday: 'Sat',
    sunday: 'Sun',
  }
};

/**
 * Get translation by key
 */
export function getTranslation(language, key) {
  const lang = language === 'english' ? 'english' : 'polish';
  return translations[lang][key] || key;
}

/**
 * Get plural form for meal count (Polish has 3 forms!)
 */
export function getMealCountText(language, count) {
  const lang = language === 'english' ? 'english' : 'polish';

  if (lang === 'polish') {
    if (count === 1) return `${count} ${translations.polish.meal_count_singular}`;
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) {
      return `${count} ${translations.polish.meal_count_plural}`;
    }
    return `${count} ${translations.polish.meal_count_many}`;
  } else {
    return count === 1
      ? `${count} ${translations.english.meal_count_singular}`
      : `${count} ${translations.english.meal_count_plural}`;
  }
}

/**
 * Get plural form for shopping trip count (Polish has 3 forms!)
 */
export function getShoppingCountText(language, count) {
  const lang = language === 'english' ? 'english' : 'polish';

  if (lang === 'polish') {
    if (count === 1) return `${count} ${translations.polish.shopping_count_singular}`;
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) {
      return `${count} ${translations.polish.shopping_count_plural}`;
    }
    return `${count} ${translations.polish.shopping_count_many}`;
  } else {
    return count === 1
      ? `${count} ${translations.english.shopping_count_singular}`
      : `${count} ${translations.english.shopping_count_plural}`;
  }
}

/**
 * Get plural form for ingredient count (Polish has 3 forms!)
 */
export function getIngredientCountText(language, count) {
  const lang = language === 'english' ? 'english' : 'polish';

  if (lang === 'polish') {
    if (count === 1) return `${count} ${translations.polish.ingredient_count_singular}`;
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) {
      return `${count} ${translations.polish.ingredient_count_plural}`;
    }
    return `${count} ${translations.polish.ingredient_count_many}`;
  } else {
    return count === 1
      ? `${count} ${translations.english.ingredient_count_singular}`
      : `${count} ${translations.english.ingredient_count_plural}`;
  }
}

/**
 * Format cooking dates with locale support and truncation
 * @param {string[]} dates - Array of date strings (YYYY-MM-DD format)
 * @param {string} language - 'polish' or 'english'
 * @param {number} maxDates - Maximum dates to show before truncating (default: 3)
 * @returns {string} Formatted date string like "Jan 5, Jan 7" or "sty 5, sty 7, +2 more"
 */
export function formatCookingDates(dates, language, maxDates = 3) {
  const locale = language === 'polish' ? 'pl-PL' : 'en-US';

  // Format each date
  const formatted = dates.map(d =>
    new Date(d).toLocaleDateString(locale, { month: 'short', day: 'numeric' })
  );

  // Truncate if too many dates
  if (formatted.length > maxDates) {
    const shown = formatted.slice(0, maxDates).join(', ');
    const remaining = formatted.length - maxDates;
    const moreDatesText = getTranslation(language, 'more_dates').replace('{count}', remaining);
    return `${shown}, ${moreDatesText}`;
  }

  return formatted.join(', ');
}

/**
 * Format meal name with cooking dates
 * @param {string} mealName - Name of the meal
 * @param {string[]} cookingDates - Array of cooking dates
 * @param {string} language - 'polish' or 'english'
 * @returns {string} Formatted string like "Spaghetti (Jan 5, Jan 7)"
 */
export function formatMealWithDates(mealName, cookingDates, language) {
  const dates = formatCookingDates(cookingDates, language);
  return `${mealName} (${dates})`;
}
