/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        theme: {
          bg: {
            primary: 'var(--color-bg-primary)',
            secondary: 'var(--color-bg-secondary)',
          },
          accent: {
            primary: 'var(--color-accent-primary)',
            secondary: 'var(--color-accent-secondary)',
          },
          text: {
            primary: 'var(--color-text-primary)',
            secondary: 'var(--color-text-secondary)',
          },
          border: 'var(--color-border)',
          surface: {
            hover: 'var(--color-surface-hover)',
          },
          success: 'var(--color-success)',
          warning: 'var(--color-warning)',
          danger: 'var(--color-danger)',
        },
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          900: '#14532d',
        },
        earth: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          500: '#78716c',
          700: '#44403c',
          900: '#1c1917',
        },
      },
      borderRadius: {
        'card': '1rem',
        'button': '0.75rem',
      },
      boxShadow: {
        'theme-sm': '0 1px 2px 0 var(--color-border)',
        'theme-md': '0 4px 6px -1px var(--color-border)',
      }
    },
  },
  plugins: [],
}
