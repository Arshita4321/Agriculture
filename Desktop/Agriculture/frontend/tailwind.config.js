/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        forest: { 50: '#f1f7f3', 100: '#dcebe1', 500: '#2f7d5b', 600: '#256b4c', 700: '#1d573d', 800: '#16422f', 900: '#0f2e21' },
        paper: '#f7f8f5',
        risk: { low: '#2f9e6b', moderate: '#e8a317', high: '#e2661f', veryHigh: '#c62d2d' },
      },
      fontFamily: { sans: ['"Public Sans"', 'system-ui', 'sans-serif'] },
      boxShadow: { card: '0 1px 2px rgba(15,46,33,.06), 0 1px 3px rgba(15,46,33,.04)' },
    },
  },
  plugins: [],
};
