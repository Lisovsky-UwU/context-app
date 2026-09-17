<script setup lang="ts">
import { ref } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"

import { ApiError } from "../api/client"
import { useAuthStore } from "../stores/auth"

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref("")
const password = ref("")
const busy = ref(false)
const error = ref("")

async function submit() {
  busy.value = true
  error.value = ""
  try {
    await auth.login(username.value.trim(), password.value)
    router.push((route.query.next as string) ?? { name: "places" })
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Вход не удался"
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="gate">
    <div class="gate__card">
      <span class="gate__tab">Контекст</span>
      <h1>Куда идём в этот раз</h1>
      <p class="muted gate__lead">
        Общая картотека мест: что уже посмотрели, что ещё ждёт своей субботы.
      </p>

      <form @submit.prevent="submit">
        <p v-if="error" class="error-note">{{ error }}</p>

        <label class="field">
          <span>Имя пользователя</span>
          <input
            v-model="username"
            class="input"
            type="text"
            autocomplete="username"
            autocapitalize="off"
            spellcheck="false"
            required
          />
        </label>

        <label class="field">
          <span>Пароль</span>
          <input
            v-model="password"
            class="input"
            type="password"
            autocomplete="current-password"
            required
          />
        </label>

        <button class="btn btn--primary btn--wide" type="submit" :disabled="busy">
          {{ busy ? "Входим…" : "Войти" }}
        </button>
      </form>

      <p class="muted gate__switch">
        Есть код приглашения?
        <RouterLink :to="{ name: 'register' }">Заведите аккаунт</RouterLink>
      </p>
    </div>
  </div>
</template>
