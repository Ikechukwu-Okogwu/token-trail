import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
     ...(mode === 'test' ? [] : [tailwindcss()])
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
  test: {
    environment: 'jsdom'
  }
}))
