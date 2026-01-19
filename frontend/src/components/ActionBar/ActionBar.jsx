/**
 * ActionBar - Top action bar with Save, Load, Generate Tasks buttons
 */
import { useState, useRef, useEffect } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme.jsx';
import { tasksAPI, configAPI } from '../../api/client';
import SettingsModal from '../Settings/SettingsModal';
import TaskGenerationWarningModal from './TaskGenerationWarningModal';
import ShoppingTripDateModal from '../ShoppingManager/ShoppingTripDateModal';
import RoundingWarningModal from '../RoundingWarningModal/RoundingWarningModal';

export default function ActionBar() {
  const { scheduledMeals, shoppingTrips, getMealPlanJSON, loadMealPlan, language, setLanguage, addShoppingTrip } = useMealPlan();
  const { t, mealCount: getMealCountText, shoppingCount: getShoppingCountText } = useTranslation();
  const { theme, toggleTheme, colors } = useTheme();
  const [saveStatus, setSaveStatus] = useState(null); // { type: 'success' | 'error', message: string }
  const [generating, setGenerating] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [hasEnvToken, setHasEnvToken] = useState(false);
  const [warningModalOpen, setWarningModalOpen] = useState(false);
  const [roundingWarnings, setRoundingWarnings] = useState([]);
  const [warningState, setWarningState] = useState({ type: 'none', count: 0 }); // type: 'none' | 'no_trips' | 'unassigned_meals'
  const [dateModalOpen, setDateModalOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false); // Mobile menu state
  const fileInputRef = useRef(null);
  const mobileMenuRef = useRef(null);

  // Check if Todoist token is set via environment variable
  useEffect(() => {
    const checkEnvToken = async () => {
      try {
        const status = await configAPI.getStatus();
        setHasEnvToken(status.has_env_token);
      } catch (error) {
        console.error('Failed to check ENV token:', error);
      }
    };
    checkEnvToken();
  }, []);

  // Close mobile menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target)) {
        setMobileMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [mobileMenuRef]);

  /**
   * Save meal plan as JSON file (client-side download)
   */
  const handleSave = () => {
    if (scheduledMeals.length === 0) {
      setSaveStatus({
        type: 'error',
        message: 'No meals scheduled to save'
      });
      setTimeout(() => setSaveStatus(null), 3000);
      return;
    }

    try {
      const mealPlan = getMealPlanJSON();

      // Find earliest cooking date for filename
      const allDates = scheduledMeals.flatMap(meal => meal.cooking_dates);
      const earliestDate = allDates.length > 0 ? allDates.sort()[0] : new Date().toISOString().split('T')[0];

      // Create blob and download
      const blob = new Blob([JSON.stringify(mealPlan, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meal-plan-${earliestDate}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      setSaveStatus({
        type: 'success',
        message: `Saved meal-plan-${earliestDate}.json`
      });

      setTimeout(() => setSaveStatus(null), 3000);

    } catch (error) {
      console.error('Failed to save meal plan:', error);
      setSaveStatus({
        type: 'error',
        message: 'Failed to save meal plan'
      });
      setTimeout(() => setSaveStatus(null), 5000);
    }
    setMobileMenuOpen(false);
  };

  /**
   * Load meal plan from JSON file
   */
  const handleLoad = () => {
    fileInputRef.current?.click();
    setMobileMenuOpen(false);
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const mealPlan = JSON.parse(text);

      // Validate structure
      if (!mealPlan.scheduled_meals || !Array.isArray(mealPlan.scheduled_meals)) {
        throw new Error('Invalid meal plan format');
      }

      loadMealPlan(mealPlan);

      setSaveStatus({
        type: 'success',
        message: `Loaded ${file.name}`
      });
      setTimeout(() => setSaveStatus(null), 3000);

    } catch (error) {
      console.error('Failed to load meal plan:', error);
      setSaveStatus({
        type: 'error',
        message: error.message || 'Failed to load meal plan'
      });
      setTimeout(() => setSaveStatus(null), 5000);
    }

    // Reset file input
    e.target.value = '';
  };

  /* Check if a meal is already assigned to any shopping trip */
  const isMealAssigned = (mealId) => {
    return shoppingTrips.some(trip => trip.scheduled_meal_ids.includes(mealId));
  };

  /**
   * Generate Todoist tasks from current meal plan
   */
  const handleGenerateTasks = async () => {
    if (scheduledMeals.length === 0) {
      setSaveStatus({
        type: 'error',
        message: 'No meals scheduled'
      });
      setTimeout(() => setSaveStatus(null), 3000);
      return;
    }

    // 1. Check for NO shopping trips
    if (shoppingTrips.length === 0) {
      setWarningState({ type: 'no_trips' });
      return;
    }

    // 2. Check for UNASSIGNED meals
    const unassignedCount = scheduledMeals.filter(meal => !isMealAssigned(meal.id)).length;
    if (unassignedCount > 0) {
      setWarningState({ type: 'unassigned_meals', count: unassignedCount });
      return;
    }

    // 3. Proceed to backend checks (rounding warnings)
    await proceedToRoundingCheck();
  };

  // Step 2: Backend Rounding Check (original logic moved here)
  const proceedToRoundingCheck = async () => {
    try {
      setGenerating(true);
      setSaveStatus(null);
      setWarningState({ type: 'none' }); // Clear any warnings

      const mealPlan = getMealPlanJSON();

      // Check for rounding warnings first
      console.log('Checking for rounding warnings...');
      const warningsResponse = await tasksAPI.checkWarnings(mealPlan);
      console.log('Warnings response:', warningsResponse);

      if (warningsResponse.warnings && warningsResponse.warnings.length > 0) {
        // Show warning modal and wait for user decision
        console.log('Showing warning modal with', warningsResponse.warnings.length, 'warnings');
        setRoundingWarnings(warningsResponse.warnings);
        setWarningModalOpen(true);
        setGenerating(false);
        return;
      }

      console.log('No warnings, proceeding with task generation');

      // No warnings, proceed with task generation
      await generateTasksAfterWarnings();

    } catch (error) {
      console.error('Failed to check warnings:', error);
      setSaveStatus({
        type: 'error',
        message: error.message || 'Failed to check warnings'
      });
      setTimeout(() => setSaveStatus(null), 5000);
      setGenerating(false);
    }
  };

  const handleCreateTripFromWarning = () => {
    setWarningState({ type: 'none' });
    setDateModalOpen(true);
  };

  const handleDateConfirm = (date) => {
    addShoppingTrip({
      shopping_date: date,
      scheduled_meal_ids: []
    });
    setDateModalOpen(false);
    // Generation STOPS here to let user add meals
  };

  const handleContinueAnyway = () => {
    setWarningState({ type: 'none' });
    proceedToRoundingCheck(); // Ignore warning and continue
  };

  const generateTasksAfterWarnings = async (enableRounding = true) => {
    try {
      setGenerating(true);
      setSaveStatus(null);
      setWarningModalOpen(false);

      const mealPlan = getMealPlanJSON();

      // If ENV token is set, backend will use it automatically
      // Otherwise, we need to provide token from sessionStorage
      const todoistToken = hasEnvToken ? 'env' : sessionStorage.getItem('todoist_token');

      if (!todoistToken) {
        setSaveStatus({
          type: 'error',
          message: 'Todoist token not set. Please configure in settings.'
        });
        setTimeout(() => setSaveStatus(null), 5000);
        return;
      }

      const response = await tasksAPI.generate({
        meal_plan: mealPlan,
        todoist_token: todoistToken,
        enable_ingredient_rounding: enableRounding
      });

      setSaveStatus({
        type: 'success',
        message: `Created ${response.tasks_created} tasks in Todoist!`
      });
      setTimeout(() => setSaveStatus(null), 5000);

    } catch (error) {
      console.error('Failed to generate tasks:', error);
      setSaveStatus({
        type: 'error',
        message: error.message || 'Failed to generate tasks'
      });
      setTimeout(() => setSaveStatus(null), 5000);
    } finally {
      setGenerating(false);
      setWarningModalOpen(false);
    }
  };

  return (
    <>
      <style>{`
        .action-btn:not(:disabled):hover {
          background-color: var(--btn-bg-hover) !important;
        }
        .icon-btn:hover {
          background-color: var(--btn-bg-hover) !important;
          color: var(--btn-text-hover) !important;
        }
        .menu-item:hover {
          background-color: var(--hover-color);
        }
      `}</style>
      <div className="flex items-center gap-2 justify-end w-full relative">
        {/* Status Info (Hidden on mobile) */}
        <div className="hidden md:block text-sm mr-auto truncate" style={{ color: colors.subtext1 }}>
          {getMealCountText(scheduledMeals.length)}
          {shoppingTrips.length > 0 && ` · ${getShoppingCountText(shoppingTrips.length)}`}
        </div>

        {/* Hidden file input for loading */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* --- Desktop Buttons --- */}
        <div className="hidden md:flex items-center gap-2">
          {/* Load Button */}
          <button
            onClick={handleLoad}
            className="px-4 py-2 rounded transition-colors text-sm font-medium flex items-center gap-2 action-btn"
            style={{
              '--btn-bg': colors.lavender,
              '--btn-bg-hover': colors.text,
              '--btn-text': colors.base,
              backgroundColor: colors.lavender,
              color: colors.base
            }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            {t('load')}
          </button>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={scheduledMeals.length === 0}
            className="px-4 py-2 rounded transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed action-btn"
            style={{
              '--btn-bg': colors.blue,
              '--btn-bg-hover': colors.sapphire,
              '--btn-text': colors.base,
              backgroundColor: colors.blue,
              color: colors.base
            }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
            {t('save')}
          </button>
        </div>

        {/* Generate Tasks Button (Always visible, icon only on mobile) */}
        <button
          onClick={handleGenerateTasks}
          disabled={generating || scheduledMeals.length === 0}
          className="px-3 md:px-4 py-2 rounded transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed action-btn"
          style={{
            '--btn-bg': colors.green,
            '--btn-bg-hover': colors.teal,
            '--btn-text': colors.base,
            backgroundColor: colors.green,
            color: colors.base
          }}
          title={t('generate_tasks')}
        >
          {generating ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          )}
          <span className="hidden md:inline">{generating ? t('generate_tasks') + '...' : t('generate_tasks')}</span>
        </button>

        {/* Desktop: Language, Theme, Settings */}
        <div className="hidden md:flex items-center gap-1">
          {/* Language Toggle */}
          <button
            onClick={() => setLanguage(language === 'polish' ? 'english' : 'polish')}
            className="px-3 py-2 rounded transition-colors font-medium text-sm icon-btn"
            style={{
              '--btn-bg-hover': colors.surface0,
              '--btn-text-hover': colors.text,
              color: colors.subtext1,
              backgroundColor: 'transparent'
            }}
            title={language === 'polish' ? 'Switch to English' : 'Przełącz na polski'}
          >
            {language === 'polish' ? 'EN' : 'PL'}
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="px-3 py-2 rounded transition-colors icon-btn"
            style={{
              '--btn-bg-hover': colors.surface0,
              '--btn-text-hover': colors.text,
              color: colors.subtext1,
              backgroundColor: 'transparent'
            }}
            title={theme === 'latte' ? 'Switch to dark mode' : 'Switch to light mode'}
          >
            {theme === 'latte' ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </button>

          {/* Settings Button */}
          <button
            onClick={() => setSettingsOpen(true)}
            className="px-3 py-2 rounded transition-colors icon-btn"
            style={{
              '--btn-bg-hover': colors.surface0,
              '--btn-text-hover': colors.text,
              color: colors.subtext1,
              backgroundColor: 'transparent'
            }}
            title="Settings"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>

        {/* Mobile Menu Button - 3 dots */}
        <div className="md:hidden relative" ref={mobileMenuRef}>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg transition-colors"
            style={{ color: colors.text, backgroundColor: mobileMenuOpen ? colors.surface0 : 'transparent' }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </button>

          {/* Mobile Menu Dropdown */}
          {mobileMenuOpen && (
            <div
              className="absolute right-0 top-full mt-2 w-48 rounded-lg shadow-xl py-2 z-50 border"
              style={{
                backgroundColor: colors.base,
                borderColor: colors.surface0
              }}
            >
              <div className="px-4 py-2 text-xs border-b mb-1 truncate" style={{ color: colors.subtext1, borderColor: colors.surface0 }}>
                {getMealCountText(scheduledMeals.length)}
                {shoppingTrips.length > 0 && ` · ${getShoppingCountText(shoppingTrips.length)}`}
              </div>

              <button
                onClick={handleLoad}
                className="w-full text-left px-4 py-2 text-sm flex items-center gap-3 menu-item"
                style={{ color: colors.text, '--hover-color': colors.surface0 }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                {t('load')}
              </button>

              <button
                onClick={handleSave}
                disabled={scheduledMeals.length === 0}
                className="w-full text-left px-4 py-2 text-sm flex items-center gap-3 disabled:opacity-50 menu-item"
                style={{ color: colors.text, '--hover-color': colors.surface0 }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                {t('save')}
              </button>

              <div className="my-1 border-t" style={{ borderColor: colors.surface0 }}></div>

              <button
                onClick={() => setSettingsOpen(true)}
                className="w-full text-left px-4 py-2 text-sm flex items-center gap-3 menu-item"
                style={{ color: colors.text, '--hover-color': colors.surface0 }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {t('settings')}
              </button>

              <button
                onClick={() => setLanguage(language === 'polish' ? 'english' : 'polish')}
                className="w-full text-left px-4 py-2 text-sm flex items-center gap-3 menu-item"
                style={{ color: colors.text, '--hover-color': colors.surface0 }}
              >
                <span className="w-4 text-center font-bold text-[10px]">{language === 'polish' ? 'EN' : 'PL'}</span>
                {language === 'polish' ? 'Switch to English' : 'Przełącz na polski'}
              </button>

              <button
                onClick={toggleTheme}
                className="w-full text-left px-4 py-2 text-sm flex items-center gap-3 menu-item"
                style={{ color: colors.text, '--hover-color': colors.surface0 }}
              >
                {theme === 'latte' ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                    Dark Mode
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                    Light Mode
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Save Status - positioned absolute to not shift layout */}
        {saveStatus && (
          <div
            className={`absolute top-full right-0 mt-2 text-sm px-3 py-1 rounded shadow-lg z-50 whitespace-nowrap ${saveStatus.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-200'
              : 'bg-red-100 text-red-800 border border-red-200'
              }`}
          >
            {saveStatus.message}
          </div>
        )}

        {/* Settings Modal - Always available for accessibility settings */}
        <SettingsModal
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
        />

        {/* Task Generation Warning Modal */}
        <TaskGenerationWarningModal
          isOpen={warningState.type !== 'none'}
          onClose={() => setWarningState({ type: 'none' })}
          warningType={warningState.type}
          unassignedCount={warningState.count}
          onCreateTrip={handleCreateTripFromWarning}
          onContinue={handleContinueAnyway}
        />

        {/* Date Selection Modal (for create trip from warning) */}
        <ShoppingTripDateModal
          isOpen={dateModalOpen}
          onClose={() => setDateModalOpen(false)}
          onConfirm={handleDateConfirm}
        />

        {/* Rounding Warning Modal */}
        <RoundingWarningModal
          isOpen={warningModalOpen}
          onClose={() => {
            setWarningModalOpen(false);
            setGenerating(false);
          }}
          onContinue={generateTasksAfterWarnings}
          warnings={roundingWarnings}
        />
      </div>
    </>
  );
}
