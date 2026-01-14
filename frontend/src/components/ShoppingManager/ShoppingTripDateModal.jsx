/**
 * ShoppingTripDateModal
 * Shared modal for selecting a date for a new shopping trip
 */
import { useState } from 'react';
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme';

export default function ShoppingTripDateModal({ isOpen, onClose, onConfirm }) {
    const { t } = useTranslation();
    const { colors, theme } = useTheme();
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        onConfirm(date);
        // Reset date to today for next time
        setDate(new Date().toISOString().split('T')[0]);
    };

    return (
        <div className="modal-overlay">
            <div
                className="rounded-lg p-6 w-full max-w-md shadow-xl"
                style={{ backgroundColor: colors.base }}
            >
                <h3 className="text-xl font-semibold mb-4" style={{ color: colors.text }}>
                    {t('select_date_title')}
                </h3>

                <form onSubmit={handleSubmit}>
                    <div className="mb-6">
                        <label className="block text-sm font-medium mb-2" style={{ color: colors.subtext0 }}>
                            {t('shopping_date')}
                        </label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2"
                            style={{
                                backgroundColor: colors.surface0,
                                borderColor: colors.surface1,
                                color: colors.text,
                                borderWidth: '1px',
                                borderStyle: 'solid',
                                colorScheme: theme === 'latte' ? 'light' : 'dark'
                            }}
                            required
                        />
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded transition-colors"
                            style={{
                                color: colors.subtext0,
                                '--hover-bg': colors.surface0
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        >
                            {t('cancel')}
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 rounded font-medium transition-colors"
                            style={{
                                backgroundColor: colors.blue,
                                color: colors.base
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.sapphire}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.blue}
                        >
                            {t('add')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
