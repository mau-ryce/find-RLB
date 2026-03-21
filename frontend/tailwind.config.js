/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // UEFA-inspired color palette
        primary: {
          50: '#f0f4f8',
          100: '#d9e4f0',
          300: '#7a98c7',
          500: '#003f7f', // Deep blue
          700: '#001a3d', // Metal black-blue
          900: '#000a14'  // Metal black
        },
        secondary: {
          50: '#faf7f5',
          300: '#d4a5a5',
          500: '#a83030', // Brick red
          700: '#7a1f1f'
        },
        accent: {
          50: '#f9f9f9',
          300: '#d4d4d4',
          500: '#c0c0c0', // Silver
          700: '#808080'  // Metal black
        },
        slate: {
          300: '#cbd5e1',
          400: '#94a3b8',
          700: '#334155',
          900: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
      boxShadow: {
        premium: '0 10px 40px rgba(0, 0, 0, 0.2)',
        card: '0 4px 20px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
};
