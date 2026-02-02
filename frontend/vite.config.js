import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'supplementally-nonrelieving-anette.ngrok-free.dev', // Add the specific host here
      // You can also add other hosts if needed
    ],
    host: true,      // Required for Docker
    strictPort: true,
    port: 5173,
    watch: {
      usePolling: true, // Required for Windows
    }
  }
})