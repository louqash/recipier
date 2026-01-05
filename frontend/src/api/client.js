/**
 * API client for Recipier backend
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// Meals API
export const mealsAPI = {
  /**
   * Get all meals with optional search filter
   * @param {string} search - Search query for filtering meals
   * @returns {Promise<{meals: Array, total_count: number}>}
   */
  async getAll(search = '') {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    return fetchAPI(`/meals/${params}`);
  },

  /**
   * Get single meal by ID
   * @param {string} mealId - Meal identifier
   * @returns {Promise<Object>}
   */
  async getById(mealId) {
    return fetchAPI(`/meals/${mealId}`);
  },
};

// Meal Plan API
export const mealPlanAPI = {
  /**
   * Validate meal plan structure
   * @param {Object} mealPlan - Meal plan to validate
   * @returns {Promise<{valid: boolean, errors: Array, warnings: Array}>}
   */
  async validate(mealPlan) {
    return fetchAPI('/meal-plan/validate', {
      method: 'POST',
      body: JSON.stringify(mealPlan),
    });
  },

  /**
   * Expand meal plan (calculate ingredient quantities)
   * @param {Object} mealPlan - Meal plan to expand
   * @returns {Promise<Object>} Expanded meal plan with calculated quantities
   */
  async expand(mealPlan) {
    return fetchAPI('/meal-plan/expand', {
      method: 'POST',
      body: JSON.stringify(mealPlan),
    });
  },

  /**
   * Save meal plan to file
   * @param {Object} mealPlan - Meal plan to save
   * @returns {Promise<{success: boolean, file_path: string, message: string}>}
   */
  async save(mealPlan) {
    return fetchAPI('/meal-plan/save', {
      method: 'POST',
      body: JSON.stringify(mealPlan),
    });
  },

  /**
   * Load meal plan by date
   * @param {string} date - Date in YYYY-MM-DD format
   * @returns {Promise<Object>} Loaded meal plan
   */
  async load(date) {
    return fetchAPI(`/meal-plan/load/${date}`);
  },
};

// Tasks API
export const tasksAPI = {
  /**
   * Generate Todoist tasks from meal plan
   * @param {Object} request - Task generation request
   * @param {Object} request.meal_plan - Meal plan
   * @param {Object} request.config - Task configuration
   * @param {string} request.todoist_token - Todoist API token
   * @returns {Promise<{success: boolean, tasks_created: number, tasks: Array}>}
   */
  async generate(request) {
    return fetchAPI('/tasks/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Preview tasks without creating them
   * @param {string} mealPlanFile - Optional meal plan filename
   * @returns {Promise<{tasks: Array, total_count: number}>}
   */
  async preview(mealPlanFile = '') {
    const params = mealPlanFile ? `?meal_plan_file=${encodeURIComponent(mealPlanFile)}` : '';
    return fetchAPI(`/tasks/preview${params}`);
  },
};

// Config API
export const configAPI = {
  /**
   * Get configuration status (check if ENV token is set)
   * Returns only whether token exists, NOT the token itself (security)
   * @returns {Promise<{has_env_token: boolean}>}
   */
  async getStatus() {
    return fetchAPI('/config/status');
  },
};

// Localization API
export const localizationAPI = {
  /**
   * Get translations for a language
   * @param {string} language - Language code (polish, english)
   * @returns {Promise<{language: string, translations: Object}>}
   */
  async getTranslations(language = 'polish') {
    return fetchAPI(`/localization/${language}`);
  },
};
