/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // DMO Green Palette
        primary: {
          50: '#E8F5E9',
          100: '#C8E6C9',
          200: '#A5D6A7',
          300: '#81C784',
          400: '#66BB6A',
          500: '#4CAF50',
          600: '#43A047',
          700: '#388E3C',
          800: '#2E7D32',
          900: '#006400', // Official DMO dark green
        },
        // Neutral palette
        neutral: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#EEEEEE',
          300: '#E0E0E0',
          400: '#BDBDBD',
          500: '#9E9E9E',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121',
        },
        // Dark theme colors
        dark: {
          bg: '#0D1117',
          surface: '#161B22',
          elevated: '#21262D',
          border: '#30363D',
          text: '#E6EDF3',
          'text-secondary': '#8B949E',
        },
        // Semantic colors
        success: {
          DEFAULT: '#2DA44E',
          light: '#DAFBE1',
        },
        error: {
          DEFAULT: '#CF222E',
          light: '#FFEBE9',
        },
        warning: {
          DEFAULT: '#BF8700',
          light: '#FFF8C5',
        },
        info: {
          DEFAULT: '#0969DA',
          light: '#DDF4FF',
        },
      },
      fontFamily: {
        sans: ['Poppins', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'focus': '0 0 0 3px rgba(0, 100, 0, 0.3)',
      },
    },
  },
  plugins: [],
}
