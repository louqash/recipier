/**
 * Theme hook with Catppuccin color schemes
 * Supports Latte (light) and Mocha (dark) themes
 */
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext(null);

// Catppuccin Latte (Light) colors
export const latteColors = {
  // Base colors
  base: '#eff1f5',
  mantle: '#e6e9ef',
  crust: '#dce0e8',

  // Surface colors
  surface0: '#ccd0da',
  surface1: '#bcc0cc',
  surface2: '#acb0be',

  // Overlay colors
  overlay0: '#9ca0b0',
  overlay1: '#8c8fa1',
  overlay2: '#7c7f93',

  // Text colors
  text: '#4c4f69',
  subtext1: '#5c5f77',
  subtext0: '#6c6f85',

  // Accent colors
  rosewater: '#dc8a78',
  flamingo: '#dd7878',
  pink: '#ea76cb',
  mauve: '#8839ef',
  red: '#d20f39',
  maroon: '#e64553',
  peach: '#fe640b',
  yellow: '#df8e1d',
  green: '#40a02b',
  teal: '#179299',
  sky: '#04a5e5',
  sapphire: '#209fb5',
  blue: '#1e66f5',
  lavender: '#7287fd',
};

// Catppuccin Mocha (Dark) colors
export const mochaColors = {
  // Base colors
  base: '#1e1e2e',
  mantle: '#181825',
  crust: '#11111b',

  // Surface colors
  surface0: '#313244',
  surface1: '#45475a',
  surface2: '#585b70',

  // Overlay colors
  overlay0: '#6c7086',
  overlay1: '#7f849c',
  overlay2: '#9399b2',

  // Text colors
  text: '#cdd6f4',
  subtext1: '#bac2de',
  subtext0: '#a6adc8',

  // Accent colors
  rosewater: '#f5e0dc',
  flamingo: '#f2cdcd',
  pink: '#f5c2e7',
  mauve: '#cba6f7',
  red: '#f38ba8',
  maroon: '#eba0ac',
  peach: '#fab387',
  yellow: '#f9e2af',
  green: '#a6e3a1',
  teal: '#94e2d5',
  sky: '#89dceb',
  sapphire: '#74c7ec',
  blue: '#89b4fa',
  lavender: '#b4befe',
};

// Meal type colors for Catppuccin themes
export const mealTypeColors = {
  latte: {
    breakfast: '#df8e1d',         // Yellow - warm morning
    second_breakfast: '#179299',  // Teal - refreshing
    dinner: '#ea76cb',            // Pink - main meal
    supper: '#40a02b',            // Green - evening healthy
  },
  mocha: {
    breakfast: '#fab387',         // Peach - warm morning
    second_breakfast: '#94e2d5',  // Teal - refreshing
    dinner: '#f38ba8',            // Red - main meal
    supper: '#a6e3a1',            // Green - evening healthy
  }
};

export function ThemeProvider({ children }) {
  // Detect system theme preference
  const getSystemTheme = () => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'mocha' : 'latte';
    }
    return 'latte';
  };

  // Initialize theme from localStorage or system preference
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('recipier-theme');
    return saved || getSystemTheme();
  });

  // Apply theme class to document
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-latte', 'theme-mocha');
    root.classList.add(`theme-${theme}`);
    localStorage.setItem('recipier-theme', theme);
  }, [theme]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      // Only auto-switch if user hasn't manually set a preference
      const saved = localStorage.getItem('recipier-theme');
      if (!saved) {
        setTheme(e.matches ? 'mocha' : 'latte');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'latte' ? 'mocha' : 'latte');
  };

  const colors = theme === 'mocha' ? mochaColors : latteColors;
  const mealColors = mealTypeColors[theme];

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, colors, mealColors }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
