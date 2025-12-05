/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'mochi-bg': '#0f1014',
        'mochi-sidebar': '#0f1014',
        'mochi-card': '#1a1b20',
        'mochi-hover': '#2d2e35',
        'mochi-green': '#00dc82',
        'mochi-pink': '#e91e63',
        'mochi-blue': '#3b82f6',
        'mochi-text-sub': '#9ca3af',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}