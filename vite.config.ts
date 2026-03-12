import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Caché fuera de node_modules para evitar EBUSY en entornos tipo Railway (npm ci no bloquea .vite)
  cacheDir: '.vite',
  server: {
    port: 3000,
    open: true,
    https: false
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled'],
          router: ['react-router-dom']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@mui/material', '@mui/icons-material']
  },
  define: {
    // PWA environment variables
    __PWA_ENABLED__: JSON.stringify(true),
    __PWA_VERSION__: JSON.stringify('1.0.0')
  }
})
