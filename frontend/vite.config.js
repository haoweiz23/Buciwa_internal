import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
    allowedHosts: ['nonjuristic-unrevokable-keith.ngrok-free.dev', '.trycloudflare.com', 'internal.buciwa.com'],
    hmr: {
      host: '0.0.0.0',
      protocol: 'ws'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
)
