/**
 * TaskGenerationWarningModal
 * Warns about missing shopping trips or unassigned meals
 */
import { useTranslation } from '../../hooks/useTranslation';
import { useTheme } from '../../hooks/useTheme';

export default function TaskGenerationWarningModal({
    isOpen,
    onClose,
    warningType, // 'no_trips' | 'unassigned_meals'
    unassignedCount,
    onCreateTrip,
    onContinue
}) {
    const { t } = useTranslation();
    const { colors } = useTheme();

    if (!isOpen) return null;

    const getTitle = () => {
        if (warningType === 'no_trips') return t('warning_no_shopping_trips_title');
        if (warningType === 'unassigned_meals') return t('warning_unassigned_meals_title');
        return '';
    };

    const getDescription = () => {
        if (warningType === 'no_trips') return t('warning_no_shopping_trips_desc');
        if (warningType === 'unassigned_meals') {
            return t('warning_unassigned_meals_desc').replace('{count}', unassignedCount);
        }
        return '';
    };

    return (
        <div className="modal-overlay">
            <div
                className="rounded-lg p-6 w-full max-w-md shadow-xl"
                style={{ backgroundColor: colors.base }}
            >
                {/* Warning Icon & Title */}
                <div className="flex items-start gap-3 mb-4">
                    <div className="text-3xl">⚠️</div>
                    <div>
                        <h3 className="text-xl font-semibold" style={{ color: colors.text }}>
                            {getTitle()}
                        </h3>
                        <p className="mt-2 text-sm" style={{ color: colors.subtext0 }}>
                            {getDescription()}
                        </p>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col gap-2 mt-6">
                    <button
                        onClick={onCreateTrip}
                        className="w-full px-4 py-2 rounded font-medium transition-colors"
                        style={{
                            backgroundColor: colors.green,
                            color: colors.base
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.teal}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.green}
                    >
                        {t('create_shopping_trip')}
                    </button>

                    <button
                        onClick={onContinue}
                        className="w-full px-4 py-2 rounded font-medium transition-colors"
                        style={{
                            backgroundColor: colors.surface0,
                            color: colors.text
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.surface1}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.surface0}
                    >
                        {t('continue_anyway')}
                    </button>

                    <button
                        onClick={onClose}
                        className="w-full px-4 py-2 rounded font-medium transition-colors text-sm"
                        style={{
                            color: colors.subtext0
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.color = colors.text}
                        onMouseLeave={(e) => e.currentTarget.style.color = colors.subtext0}
                    >
                        {t('cancel')}
                    </button>
                </div>
            </div>
        </div>
    );
}
