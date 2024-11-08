/** @type {import('tailwindcss').Config} */
module.exports = {
  purge:[
    './templates/**/*.html',
  ],
  content: [
    'node_modules/preline/dist/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'brand-darkgreen': '#1b074e',
        'brand-darkblue': '#010149',
        'brand-pink': '#de007e',
        'brand-green': '#8ec152',
        'brand-orange': '#f18958',
        'brand-teal': '#4cbbb8',
        'brand-yellow': '#fdc41f',
        'brand-blue': '#4cb4e7',
        'brand-lilac': '#b293c4',
        'brand-red': '#e84242'
      },
      fontFamily: {
        'brand-light': ['light'],
        'brand-medium': ['medium'],
        'brand-heavy': ['heavy'],
        'brand-extrabold': ['extrabold'],
      },
    },
  },
  plugins: [
    require('preline/plugin'),
  ],
}

