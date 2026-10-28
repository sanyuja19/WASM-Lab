/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#111114',
          sidebar: '#17171C',
          surface: '#1C1C22',
          hover: '#24232B',
          border: '#2B2A33',
        },
        text: {
          primary: '#E9E8EE',
          secondary: '#8E8B9B',
        },
        lavender: {
          muted: '#B6A4FF',
          strong: '#9D84FF',
          glow: 'rgba(182, 164, 255, 0.15)',
        },
        mint: {
          success: '#82D9B2',
          glow: 'rgba(130, 217, 178, 0.15)',
        },
        red: {
          error: '#F08F9B',
          glow: 'rgba(240, 143, 155, 0.15)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
