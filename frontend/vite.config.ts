import vue from "@vitejs/plugin-vue"
import { defineConfig } from "vite"

// Адрес бэкенда можно переопределить переменной окружения, если порт 8000 занят.
const apiTarget = process.env.VITE_API_TARGET ?? "http://127.0.0.1:8000"

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: apiTarget, changeOrigin: true },
      "/media": { target: apiTarget, changeOrigin: true },
    },
  },
})
