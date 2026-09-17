<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"

import { api } from "../api/client"
import type { Invite } from "../api/types"
import CategoryManager from "../components/CategoryManager.vue"
import { formatDate } from "../lib/format"
import { useAuthStore } from "../stores/auth"
import { useThemeStore } from "../stores/theme"

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()

const name = ref(auth.user?.display_name ?? "")
const savingName = ref(false)
const nameSaved = ref(false)
const invites = ref<Invite[]>([])
const creating = ref(false)
const copied = ref<string | null>(null)

const registerLink = (code: string) => `${window.location.origin}/register?code=${code}`

async function saveName() {
  if (!name.value.trim()) return
  savingName.value = true
  nameSaved.value = false
  try {
    await auth.rename(name.value.trim())
    nameSaved.value = true
  } finally {
    savingName.value = false
  }
}

async function createInvite() {
  creating.value = true
  try {
    invites.value = [await api.createInvite(), ...invites.value]
  } finally {
    creating.value = false
  }
}

async function copy(code: string) {
  try {
    await navigator.clipboard.writeText(registerLink(code))
    copied.value = code
    window.setTimeout(() => {
      if (copied.value === code) copied.value = null
    }, 2500)
  } catch {
    copied.value = null
  }
}

async function logout() {
  await auth.logout()
  router.push({ name: "login" })
}

onMounted(async () => {
  invites.value = await api.invites()
})
</script>

<template>
  <div class="page narrow">
    <h1>Профиль</h1>

    <section class="block">
      <h2>Имя для друзей</h2>
      <div class="row">
        <input v-model="name" class="input" type="text" maxlength="80" />
        <button class="btn btn--ghost" type="button" :disabled="savingName" @click="saveName">
          Сохранить
        </button>
      </div>
      <p v-if="nameSaved" class="muted small">Готово, друзья увидят новое имя.</p>
      <p class="muted small">Вход по имени {{ auth.user?.username }}</p>
    </section>

    <section class="block">
      <h2>Тема</h2>
      <div class="themes">
        <button
          class="theme"
          :class="{ 'theme--on': theme.theme === 'light' }"
          type="button"
          @click="theme.theme === 'dark' && theme.toggle()"
        >
          Светлая
        </button>
        <button
          class="theme"
          :class="{ 'theme--on': theme.theme === 'dark' }"
          type="button"
          @click="theme.theme === 'light' && theme.toggle()"
        >
          Тёмная
        </button>
      </div>
    </section>

    <section class="block">
      <h2>Категории</h2>
      <p class="muted small hint">
        Название и цвет меняются на месте. Цвет подбирается из палитры, чтобы категории одинаково
        читались в светлой и тёмной теме.
      </p>
      <CategoryManager />
    </section>

    <section class="block">
      <h2>Приглашения</h2>
      <p class="muted small">
        Код одноразовый: по нему заводит аккаунт один человек. Ссылку можно отправить в чат.
      </p>

      <button class="btn btn--primary" type="button" :disabled="creating" @click="createInvite">
        {{ creating ? "Создаём…" : "Создать код" }}
      </button>

      <ul v-if="invites.length" class="invites">
        <li v-for="invite in invites" :key="invite.id" :class="{ used: invite.used_at }">
          <span class="code">{{ invite.code }}</span>
          <span v-if="invite.used_by" class="muted small">
            занял {{ invite.used_by.display_name }}
          </span>
          <span v-else class="muted small">создан {{ formatDate(invite.created_at.slice(0, 10)) }}</span>
          <button
            v-if="!invite.used_at"
            class="btn btn--quiet"
            type="button"
            @click="copy(invite.code)"
          >
            {{ copied === invite.code ? "Ссылка скопирована" : "Копировать ссылку" }}
          </button>
        </li>
      </ul>
    </section>

    <button class="btn btn--ghost logout" type="button" @click="logout">Выйти</button>
  </div>
</template>

<style scoped>
.narrow {
  max-width: 560px;
}

h1 {
  font-size: var(--step-3);
  margin-bottom: 1.25rem;
}

.block {
  padding-top: 1.25rem;
  margin-bottom: 1.75rem;
  border-top: 1px solid var(--edge);
}

.block h2 {
  margin-bottom: 0.75rem;
}

.row {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
}

.small {
  font-size: var(--small);
  margin: 0.2rem 0 0;
}

.hint {
  margin-bottom: 0.9rem;
}

.themes {
  display: flex;
  gap: 0.5rem;
}

.theme {
  min-height: 44px;
  padding: 0 1.1rem;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-field);
  background: transparent;
  font-size: var(--small);
  cursor: pointer;
}

.theme--on {
  border-color: var(--pomegranate);
  background: var(--pomegranate-soft);
  color: var(--pomegranate);
  font-weight: 600;
}

.invites {
  display: grid;
  gap: 0.5rem;
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
}

.invites li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--edge);
  border-radius: var(--radius-field);
  background: var(--card);
}

.invites li.used {
  opacity: 0.6;
}

.code {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.12em;
}

.invites .btn {
  margin-left: auto;
}

.logout {
  margin-top: 1rem;
}
</style>
