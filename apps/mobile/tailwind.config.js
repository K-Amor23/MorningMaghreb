/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        'morocco-red': '#C1272D',
        'morocco-green': '#006233',
        'morocco-gold': '#FFD700',
        'casablanca-blue': '#1E3A8A',
        'casablanca-light': '#F1F5F9',
      },
      fontFamily: {
        'sans': ['System', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 