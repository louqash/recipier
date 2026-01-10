/**
 * SettingsModal - Modal for configuring Todoist API token
 */
import { useState, useEffect } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';
import { useTranslation } from '../../hooks/useTranslation';
import { configAPI } from '../../api/client';

export default function SettingsModal({ isOpen, onClose }) {
  const { todoistToken, updateTodoistToken, fontSize, updateFontSize } = useMealPlan();
  const { t } = useTranslation();
  const [token, setToken] = useState('');
  const [currentFontSize, setCurrentFontSize] = useState('medium');
  const [saved, setSaved] = useState(false);
  const [hasEnvToken, setHasEnvToken] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setToken(todoistToken || '');
      setCurrentFontSize(fontSize || 'medium');
      setSaved(false);

      // Check if ENV token is set
      configAPI.getStatus().then(status => {
        setHasEnvToken(status.has_env_token);
      }).catch(err => {
        console.error('Failed to check ENV token:', err);
      });
    }
  }, [isOpen, todoistToken, fontSize]);

  const handleSave = () => {
    updateTodoistToken(token);
    updateFontSize(currentFontSize);
    setSaved(true);
    setTimeout(() => {
      onClose();
    }, 1000);
  };

  const handleCancel = () => {
    setToken(todoistToken || '');
    setCurrentFontSize(fontSize || 'medium');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full m-4">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">{t('settings_title')}</h2>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Todoist Token Input - Only show if no token exists (neither ENV nor session) */}
          {!hasEnvToken && !todoistToken && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('todoist_token_label')}
              </label>
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder={t('todoist_token_placeholder')}
                className="input-field w-full"
              />
              <p className="text-xs text-gray-500 mt-2">
                {t('get_token_instructions')}{' '}
                <a
                  href="https://todoist.com/app/settings/integrations/developer"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {t('todoist_developer_settings')}
                </a>
              </p>
            </div>
          )}

          {/* Font Size Control */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('font_size_label')}
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setCurrentFontSize('small')}
                className={`flex-1 px-4 py-2 rounded border transition-colors ${
                  currentFontSize === 'small'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {t('font_size_small')}
              </button>
              <button
                type="button"
                onClick={() => setCurrentFontSize('medium')}
                className={`flex-1 px-4 py-2 rounded border transition-colors ${
                  currentFontSize === 'medium'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {t('font_size_medium')}
              </button>
              <button
                type="button"
                onClick={() => setCurrentFontSize('large')}
                className={`flex-1 px-4 py-2 rounded border transition-colors ${
                  currentFontSize === 'large'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {t('font_size_large')}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {t('font_size_description')}
            </p>
          </div>

          {/* Saved Indicator */}
          {saved && (
            <div className="bg-green-100 text-green-800 border border-green-200 rounded p-3 text-sm">
              {t('settings_saved')}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
          >
            {t('cancel')}
          </button>
          <button
            onClick={handleSave}
            disabled={saved}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {saved ? `${t('save')}d!` : t('save')}
          </button>
        </div>
      </div>
    </div>
  );
}
