import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,      // Required for Docker
    strictPort: true,
    port: 5173,
    watch: {
      usePolling: true, // Required for Windows
    }
  }
})
