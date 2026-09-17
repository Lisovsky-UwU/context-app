<script setup lang="ts">
import { onMounted, ref } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"

import { ApiError } from "../api/client"
import { useAuthStore } from "../stores/auth"

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref("")
const displayName = ref("")
const password = ref("")
const inviteCode = ref("")
const busy = ref(false)
const error = ref("")

onMounted(() => {
  const code = route.query.code
  if (typeof code === "string") inviteCode.value = code.toUpperCase()
})

async function submit() {
  busy.value = true
  error.value = ""
  try {
    await auth.register({
      username: username.value.trim(),
      display_name: displayName.value.trim() || undefined,
      password: password.value,
      invite_code: inviteCode.value.trim().toUpperCase(),
    })
    router.push({ name: "places" })
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Регистрация не удалась"
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="gate">
    <div class="gate__card">
      <span class="gate__tab">Новая карточка</span>
      <h1>Заводим аккаунт</h1>
      <p class="muted gate__lead">Код приглашения даёт любой, кто уже в компании.</p>

      <form @submit.prevent="submit">
        <p v-if="error" class="error-note">{{ error }}</p>

        <label class="field">
          <span>Код приглашения</span>
          <input v-model="inviteCode" class="input code" type="text" required maxlength="32" />
        </label>

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
            minlength="3"
            maxlength="32"
            pattern="[A-Za-z0-9_.\-]+"
          />
          <small class="muted hint">Латиница и цифры — с ним вы входите.</small>
        </label>

        <label class="field">
          <span>Имя</span>
          <input v-model="displayName" class="input" type="text" maxlength="80" placeholder="Как вас зовут" />
          <small class="muted hint">Его видят друзья в списках и походах. Можно поменять в профиле.</small>
        </label>

        <label class="field">
          <span>Пароль, от 6 символов</span>
          <input
            v-model="password"
            class="input"
            type="password"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </label>

        <button class="btn btn--primary btn--wide" type="submit" :disabled="busy">
          {{ busy ? "Создаём…" : "Создать аккаунт" }}
        </button>
      </form>

      <p class="muted gate__switch">
        Уже заходили?
        <RouterLink :to="{ name: 'login' }">Войти</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.code {
  font-family: var(--font-display);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hint {
  font-size: var(--tiny);
  line-height: 1.4;
}
</style>
