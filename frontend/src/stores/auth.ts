import { defineStore } from "pinia"
import { ref } from "vue"

import { api } from "../api/client"
import type { AppConfig, UserMe, UserPublic } from "../api/types"

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserMe | null>(null)
  const members = ref<UserPublic[]>([])
  const config = ref<AppConfig | null>(null)
  const ready = ref(false)

  async function bootstrap() {
    config.value = await api.config().catch(() => null)
    try {
      user.value = await api.me()
      members.value = await api.users()
    } catch {
      user.value = null
    }
    ready.value = true
  }

  async function login(username: string, password: string) {
    user.value = await api.login(username, password)
    members.value = await api.users()
  }

  async function register(data: { username: string; password: string; invite_code: string }) {
    user.value = await api.register(data)
    members.value = await api.users()
  }

  async function logout() {
    await api.logout()
    user.value = null
    members.value = []
  }

  async function rename(display_name: string) {
    user.value = await api.updateProfile({ display_name })
    members.value = await api.users()
  }

  return { user, members, config, ready, bootstrap, login, register, logout, rename }
})
