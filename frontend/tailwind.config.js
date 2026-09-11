/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        base: '#0a0a0b',
        surface: '#141416',
        elevated: '#1b1b1e',
        border: '#26262a',
        brand: {
          DEFAULT: '#1ed760',
          dark: '#128f3c',
          subtle: '#0e3a22'
        },
        accent: '#7c3aed'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif']
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.25rem'
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' }
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' }
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' }
        },
        equalize: {
          '0%, 100%': { height: '20%' },
          '50%': { height: '100%' }
        }
      },
      animation: {
        fadeIn: 'fadeIn 0.3s ease',
        slideUp: 'slideUp 0.4s ease',
        pulse: 'pulse 2s ease-in-out infinite'
      }
    }
  },
  plugins: []
}