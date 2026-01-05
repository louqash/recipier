/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        breakfast: '#FEF3C7',
        second_breakfast: '#DBEAFE',
        dinner: '#FECACA',
        supper: '#D1FAE5',
      }
    },
  },
  plugins: [],
}
