/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      screens: {
        'xs': '480px',
      },
      colors: {
        arcade: {
          base:    '#06040f',
          surface: '#0c0a1c',
          card:    '#110e22',
          cyan:    '#00f5ff',
          pink:    '#ff1b8d',
          yellow:  '#ffe500',
          green:   '#00ff88',
          purple:  '#bf5fff',
          orange:  '#ff6b1a',
        }
      },
      fontFamily: {
        sans:     ['Inter', 'system-ui', 'sans-serif'],
        pixel:    ['"Press Start 2P"', 'monospace'],
        orbitron: ['Orbitron', 'sans-serif'],
        mono:     ['"Share Tech Mono"', 'monospace'],
      },
      animation: {
        'pulse-slow':  'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'neon-pulse':  'neon-pulse 2.5s ease-in-out infinite',
        'blink':       'blink 1s step-end infinite',
        'rgb-shift':   'rgb-shift 4s ease-in-out infinite',
        'glitch':      'glitch 0.4s ease-in-out',
        'scanline':    'scanline-move 6s linear infinite',
      },
    }
  },
  plugins: []
}
