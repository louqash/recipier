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
    settings_saved: 'Ustawienia zapisane!',
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
    eating_dates: 'Daty spożycia',
    add_eating_date: 'Dodaj datę spożycia',
    eating_dates_locked: 'Zsynchronizowane',
    eating_dates_unlocked: 'Niezależne',
    remove: 'Usuń',
    error_person_no_eating_dates: '{person} musi mieć przynajmniej jedną datę spożycia',
    error_eating_before_cooking: '{person}: data spożycia {eating_date} jest przed datą gotowania {cooking_date}',
    error_eating_dates_not_divisible: '{person} ma {num_eating} dat spożycia, które nie dzielą się równo przez {num_cooking} sesji',

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
    search_meals: 'Szukaj posiłków lub składników...',
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
    eating: 'Jedzenie',

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

    // Meal Details Modal
    calories: 'Kalorie',
    ingredients: 'Składniki',
    ingredient_name: 'Składnik',
    total: 'Suma',
    suggested_seasonings_title: 'Sugerowane przyprawy',
    cooking_steps: 'Kroki przygotowania',
    prep_tasks: 'Przygotowania',
    days_before_cooking: 'dni przed gotowaniem',
    package_size_note: 'Opakowanie: {{size}}',

    // Rounding Warning Modal
    rounding_warning_title: 'Ostrzeżenia o zaokrągleniu składników',
    rounding_warning_description: 'Następujące składniki zostaną znacząco zaokrąglone aby dopasować wielkość opakowań:',
    rounding_change: 'Zmiana',
    rounding_suggestion: 'Sugestia: Rozważ {{portions}} porcji aby zmniejszyć wpływ zaokrąglenia',
    rounding_calories_preserved: 'Kalorie posiłków zostaną zachowane poprzez dostosowanie innych składników.',
    rounding_used_in_meals: 'Używany w posiłkach',
    rounding_current_portions: 'porcji obecnie',
    rounding_add_portions: 'dodaj +{{count}} porcji',
    rounding_options_header: 'Opcje zwiększenia porcji',
    rounding_option_individual: 'Zwiększ {{meal}} o {{count}} porcji',
    rounding_option_combined: 'Zwiększ wszystkie {{meals}} posiłki o {{count}} porcji każdy',
    rounding_no_practical_solution: 'Brak praktycznego rozwiązania - zaokrąglenie jest zbyt duże. Rozważ pominięcie zaokrąglenia lub użycie innego składnika.',
    package_size_label: 'opakowanie',
    skip_rounding: 'Pomiń zaokrąglenie',
    continue_with_rounding: 'Kontynuuj z zaokrągleniem',
    continue_anyway: 'Kontynuuj mimo to',

    // Ingredient Categories
    category_produce: 'Warzywa i owoce',
    category_meat: 'Mięso',
    category_dairy: 'Nabiał',
    category_pantry: 'Spiżarnia',
    category_frozen: 'Mrożonki',
    category_bakery: 'Pieczywo',
    category_beverages: 'Napoje',
    category_spices: 'Przyprawy',
    category_other: 'Inne',

    // Footer
    footer_version: 'Wersja',

    // Font Size Settings
    font_size_label: 'Rozmiar czcionki',
    font_size_small: 'Mały',
    font_size_medium: 'Średni',
    font_size_large: 'Duży',
    font_size_description: 'Wybierz rozmiar czcionki dla lepszej czytelności',
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
    settings_saved: 'Settings saved!',
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
    eating_dates: 'Eating Dates',
    add_eating_date: 'Add eating date',
    eating_dates_locked: 'Synced',
    eating_dates_unlocked: 'Independent',
    remove: 'Remove',
    error_person_no_eating_dates: '{person} must have at least 1 eating date',
    error_eating_before_cooking: '{person}: eating date {eating_date} is before cooking {cooking_date}',
    error_eating_dates_not_divisible: '{person} has {num_eating} eating dates, not divisible by {num_cooking} sessions',

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
    search_meals: 'Search meals or ingredients...',
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
    eating: 'Eating',

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

    // Meal Details Modal
    calories: 'Calories',
    ingredients: 'Ingredients',
    ingredient_name: 'Ingredient',
    total: 'Total',
    suggested_seasonings_title: 'Suggested Seasonings',
    cooking_steps: 'Cooking Steps',
    prep_tasks: 'Preparation Tasks',
    days_before_cooking: 'days before cooking',
    package_size_note: 'Package: {{size}}',

    // Rounding Warning Modal
    rounding_warning_title: 'Ingredient Rounding Warnings',
    rounding_warning_description: 'The following ingredients will be significantly rounded to match package sizes:',
    rounding_change: 'Change',
    rounding_suggestion: 'Suggestion: Consider {{portions}} portions to reduce rounding impact',
    rounding_calories_preserved: 'Meal calories will be preserved by adjusting other ingredients.',
    rounding_used_in_meals: 'Used in meals',
    rounding_current_portions: 'current portions',
    rounding_add_portions: 'add +{{count}} portions',
    rounding_options_header: 'Portion increase options',
    rounding_option_individual: 'Increase {{meal}} by {{count}} portions',
    rounding_option_combined: 'Increase all {{meals}} meals by {{count}} portions each',
    rounding_no_practical_solution: 'No practical solution - rounding impact is too large. Consider skipping rounding or using a different ingredient.',
    package_size_label: 'package',
    skip_rounding: 'Skip Rounding',
    continue_with_rounding: 'Continue with Rounding',
    continue_anyway: 'Continue Anyway',

    // Ingredient Categories
    category_produce: 'Produce',
    category_meat: 'Meat',
    category_dairy: 'Dairy',
    category_pantry: 'Pantry',
    category_frozen: 'Frozen',
    category_bakery: 'Bakery',
    category_beverages: 'Beverages',
    category_spices: 'Spices',
    category_other: 'Other',

    // Footer
    footer_version: 'Version',

    // Font Size Settings
    font_size_label: 'Font Size',
    font_size_small: 'Small',
    font_size_medium: 'Medium',
    font_size_large: 'Large',
    font_size_description: 'Choose font size for better readability',
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
