import { defineStore } from "pinia"
import { ref, watch } from "vue"

type Theme = "light" | "dark"
const STORAGE_KEY = "context-app-theme"

function initialTheme(): Theme {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === "light" || saved === "dark") return saved
  } catch {
    /* приватный режим — просто идём за системной темой */
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<Theme>(initialTheme())

  function apply() {
    document.documentElement.dataset.theme = theme.value
  }

  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark"
  }

  watch(theme, (value) => {
    apply()
    try {
      localStorage.setItem(STORAGE_KEY, value)
    } catch {
      /* без сохранения тема продержится до перезагрузки */
    }
  })

  apply()
  return { theme, toggle }
})
