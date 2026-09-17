<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue"

import { api, ApiError } from "../api/client"
import type { Visit } from "../api/types"
import { useAuthStore } from "../stores/auth"

const props = defineProps<{ placeId: number; placeTitle: string; visit?: Visit | null }>()
const emit = defineEmits<{ (event: "close"): void; (event: "saved", visit: Visit): void }>()

const auth = useAuthStore()
const today = new Date().toISOString().slice(0, 10)

const date = ref(props.visit?.scheduled_date ?? today)
const time = ref(props.visit?.scheduled_time?.slice(0, 5) ?? "")
const note = ref(props.visit?.note ?? "")
const participants = ref<number[]>(
  props.visit?.participants.map((user) => user.id) ?? (auth.user ? [auth.user.id] : []),
)
const saving = ref(false)
const error = ref("")

const title = computed(() => (props.visit ? "Меняем поход" : "Идём в это место"))

function toggle(id: number) {
  participants.value = participants.value.includes(id)
    ? participants.value.filter((item) => item !== id)
    : [...participants.value, id]
}

async function save() {
  if (!date.value) {
    error.value = "Выберите дату"
    return
  }
  saving.value = true
  error.value = ""
  try {
    const payload = {
      scheduled_date: date.value,
      scheduled_time: time.value ? `${time.value}:00` : null,
      note: note.value,
      participant_ids: participants.value,
    }
    const saved = props.visit
      ? await api.updateVisit(props.visit.id, payload)
      : await api.createVisit({ place_id: props.placeId, ...payload })
    emit("saved", saved)
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Не удалось сохранить"
  } finally {
    saving.value = false
  }
}

function onKey(event: KeyboardEvent) {
  if (event.key === "Escape") emit("close")
}

onMounted(() => document.addEventListener("keydown", onKey))
onUnmounted(() => document.removeEventListener("keydown", onKey))
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="dialog sheet" role="dialog" aria-modal="true" :aria-label="title">
      <header>
        <h2>{{ title }}</h2>
        <p class="muted">{{ placeTitle }}</p>
      </header>

      <p v-if="error" class="error-note">{{ error }}</p>

      <div class="row">
        <label class="field">
          <span>Дата</span>
          <input v-model="date" class="input" type="date" :min="today" />
        </label>
        <label class="field">
          <span>Время, если известно</span>
          <input v-model="time" class="input" type="time" />
        </label>
      </div>

      <fieldset class="field">
        <span>Кто идёт</span>
        <div class="people">
          <button
            v-for="member in auth.members"
            :key="member.id"
            type="button"
            class="person"
            :class="{ 'person--on': participants.includes(member.id) }"
            @click="toggle(member.id)"
          >
            {{ member.display_name }}
          </button>
        </div>
      </fieldset>

      <label class="field">
        <span>Заметка для всех</span>
        <textarea v-model="note" class="textarea" rows="3" placeholder="Например: бронь на фамилию Сергея" />
      </label>

      <footer>
        <button class="btn btn--ghost" type="button" @click="emit('close')">Отмена</button>
        <button class="btn btn--primary" type="button" :disabled="saving" @click="save">
          {{ saving ? "Сохраняем…" : "Сохранить поход" }}
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: grid;
  place-items: end center;
  padding: 0;
  background: color-mix(in srgb, var(--paper-deep) 70%, transparent);
  backdrop-filter: blur(3px);
}

.dialog {
  width: min(520px, 100%);
  max-height: 92vh;
  overflow: auto;
  padding: 1.25rem;
  border-radius: var(--radius-card) var(--radius-card) 0 0;
  box-shadow: var(--shadow-lift);
  animation: rise 0.22s ease-out;
}

@keyframes rise {
  from {
    transform: translateY(18px);
    opacity: 0;
  }
}

header {
  margin-bottom: 1rem;
}

header p {
  margin: 0.2rem 0 0;
  font-size: var(--small);
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

fieldset {
  border: 0;
  padding: 0;
  margin: 0 0 1rem;
}

fieldset > span {
  display: block;
  margin-bottom: 0.4rem;
  font-size: var(--small);
  color: var(--ink-soft);
}

.people {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.person {
  min-height: 38px;
  padding: 0 0.8rem;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-pill);
  background: transparent;
  font-size: var(--small);
  cursor: pointer;
}

.person--on {
  background: var(--pomegranate);
  border-color: var(--pomegranate);
  color: #fff;
}

:root[data-theme="dark"] .person--on {
  color: #24101a;
}

footer {
  display: flex;
  gap: 0.6rem;
}

footer .btn {
  flex: 1;
}

@media (min-width: 640px) {
  .overlay {
    place-items: center;
    padding: 1rem;
  }

  .dialog {
    border-radius: var(--radius-card);
  }
}
</style>
