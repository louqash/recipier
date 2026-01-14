/**
 * RoundingWarningModal - Shows warnings about ingredient rounding before task generation
 */
import { useTheme } from '../../hooks/useTheme';
import { useTranslation } from '../../hooks/useTranslation';

export default function RoundingWarningModal({ isOpen, onClose, onContinue, warnings, viewOnly = false }) {
  const { colors } = useTheme();
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      style={{
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: colors.base,
          borderRadius: '8px',
          padding: '24px',
          maxWidth: '600px',
          width: '90%',
          maxHeight: '80vh',
          overflow: 'auto',
          border: `1px solid ${colors.surface0}`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ marginBottom: '20px' }}>
          <h2
            style={{
              color: colors.peach,
              fontSize: '1.5rem',
              fontWeight: 'bold',
              marginBottom: '8px',
            }}
          >
            ⚠️ {t('rounding_warning_title')}
          </h2>
          <p style={{ color: colors.text, fontSize: '0.95rem' }}>
            {t('rounding_warning_description')}
          </p>
        </div>

        {/* Warnings List */}
        <div
          style={{
            backgroundColor: colors.mantle,
            borderRadius: '6px',
            padding: '16px',
            marginBottom: '20px',
          }}
        >
          {warnings.map((warning, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: idx < warnings.length - 1 ? '16px' : 0,
                paddingBottom: idx < warnings.length - 1 ? '16px' : 0,
                borderBottom:
                  idx < warnings.length - 1 ? `1px solid ${colors.surface0}` : 'none',
              }}
            >
              <div
                style={{
                  color: colors.text,
                  fontWeight: 'bold',
                  marginBottom: '4px',
                }}
              >
                {warning.ingredient_name}
              </div>
              <div
                style={{
                  color: colors.subtext0,
                  fontSize: '0.9rem',
                  marginBottom: '4px',
                }}
              >
                {t('rounding_change')}: {Math.round(warning.percent_change * 100)}% ({Math.round(warning.original_quantity)}g → {Math.round(warning.rounded_quantity)}g)
                {warning.unit_size > 0 && (
                  <span style={{ color: colors.overlay0, fontSize: '0.85rem', marginLeft: '8px' }}>
                    📦 {Math.round(warning.unit_size)}g {t('package_size_label')}
                  </span>
                )}
              </div>

              {/* Show which meals use this ingredient */}
              {warning.meals && warning.meals.length > 0 && (
                <div
                  style={{
                    color: colors.subtext1,
                    fontSize: '0.85rem',
                    marginTop: '8px',
                    marginBottom: '8px',
                    backgroundColor: colors.surface0,
                    padding: '8px',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ fontWeight: '500', marginBottom: '4px', color: colors.text }}>
                    {t('rounding_used_in_meals')}:
                  </div>
                  {warning.meals.map((meal, mealIdx) => (
                    <div key={mealIdx} style={{ marginLeft: '8px', marginTop: '4px' }}>
                      • {meal.meal_name}: {meal.current_portions} {t('rounding_current_portions')}
                    </div>
                  ))}

                  {/* Show portion increase options */}
                  {(() => {
                    const hasIndividual = warning.meals.some(m => m.suggested_additional_portions > 0);
                    const hasCombined = warning.combined_increase > 0 && warning.meals.length > 1;
                    const hasAnySolution = hasIndividual || hasCombined;

                    if (hasAnySolution) {
                      return (
                        <div style={{ marginTop: '12px', paddingTop: '8px', borderTop: `1px solid ${colors.surface1}` }}>
                          <div style={{ fontWeight: '500', marginBottom: '6px', color: colors.blue }}>
                            💡 {t('rounding_options_header')}:
                          </div>
                          {warning.meals.map((meal, mealIdx) => (
                            meal.suggested_additional_portions > 0 && (
                              <div key={mealIdx} style={{ marginLeft: '8px', marginTop: '4px', color: colors.text }}>
                                • {t('rounding_option_individual')
                                  .replace('{{meal}}', meal.meal_name)
                                  .replace('{{count}}', meal.suggested_additional_portions)}
                              </div>
                            )
                          ))}
                          {hasCombined && (
                            <div style={{ marginLeft: '8px', marginTop: '4px', color: colors.green, fontWeight: '500' }}>
                              • {t('rounding_option_combined')
                                .replace('{{count}}', warning.combined_increase)
                                .replace('{{meals}}', warning.meals.length)}
                            </div>
                          )}
                        </div>
                      );
                    } else {
                      return (
                        <div style={{ marginTop: '12px', paddingTop: '8px', borderTop: `1px solid ${colors.surface1}` }}>
                          <div style={{ color: colors.overlay0, fontSize: '0.85rem', fontStyle: 'italic' }}>
                            ℹ️ {t('rounding_no_practical_solution')}
                          </div>
                        </div>
                      );
                    }
                  })()}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Info Note */}
        <div
          style={{
            backgroundColor: colors.surface0,
            borderRadius: '6px',
            padding: '12px',
            marginBottom: '20px',
          }}
        >
          <p style={{ color: colors.subtext1, fontSize: '0.9rem', margin: 0 }}>
            ℹ️ {t('rounding_calories_preserved')}
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
          {viewOnly ? (
            // View-only mode: just show a close button
            <button
              onClick={onClose}
              style={{
                padding: '10px 20px',
                backgroundColor: colors.blue,
                color: colors.base,
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: '500',
              }}
            >
              {t('close')}
            </button>
          ) : (
            // Task generation mode: show all options
            <>
              <button
                onClick={onClose}
                style={{
                  padding: '10px 20px',
                  backgroundColor: colors.surface0,
                  color: colors.text,
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  fontWeight: '500',
                }}
              >
                {t('cancel')}
              </button>
              <button
                onClick={() => onContinue(false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: colors.yellow,
                  color: colors.base,
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  fontWeight: '500',
                }}
              >
                {t('skip_rounding')}
              </button>
              <button
                onClick={() => onContinue(true)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: colors.green,
                  color: colors.base,
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  fontWeight: '500',
                }}
              >
                {t('continue_with_rounding')}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
