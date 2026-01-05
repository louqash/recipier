/**
 * SettingsModal - Modal for configuring Todoist API token
 */
import { useState, useEffect } from 'react';
import { useMealPlan } from '../../hooks/useMealPlan.jsx';
import { useTranslation } from '../../hooks/useTranslation';

export default function SettingsModal({ isOpen, onClose }) {
  const { todoistToken, updateTodoistToken } = useMealPlan();
  const { t } = useTranslation();
  const [token, setToken] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setToken(todoistToken || '');
      setSaved(false);
    }
  }, [isOpen, todoistToken]);

  const handleSave = () => {
    updateTodoistToken(token);
    setSaved(true);
    setTimeout(() => {
      onClose();
    }, 1000);
  };

  const handleCancel = () => {
    setToken(todoistToken || '');
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
          {/* Todoist Token Input */}
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

          {/* Saved Indicator */}
          {saved && (
            <div className="bg-green-100 text-green-800 border border-green-200 rounded p-3 text-sm">
              {t('todoist_token_label')} {t('save').toLowerCase()}d!
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
