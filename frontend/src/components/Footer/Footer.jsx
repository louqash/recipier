import { useTheme } from '../../hooks/useTheme.jsx';
import { useTranslation } from '../../hooks/useTranslation';

export default function Footer() {
  const { colors } = useTheme();
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className="flex-shrink-0 py-1.5 px-4 border-t"
      style={{
        backgroundColor: colors.base,
        borderTopColor: colors.surface0
      }}
    >
      <div className="flex items-center justify-center gap-3 text-[10px]" style={{ color: colors.subtext0 }}>
        <span>© {currentYear} Recipier</span>
        <span>•</span>
        <span>{t('footer_version')} {typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : 'unknown'}</span>
        <span>•</span>
        <span>Made with <span style={{ color: colors.red }}>♥</span> by Lukasz Sroka</span>
      </div>
    </footer>
  );
}
