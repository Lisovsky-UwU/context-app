<script setup lang="ts">
import { ref, watch } from "vue"

import { api } from "../api/client"
import type { GeoSuggestion } from "../api/types"
import { useAuthStore } from "../stores/auth"

const props = defineProps<{ address: string; lat: number | null; lon: number | null }>()
const emit = defineEmits<{
  (event: "update", value: { address: string; lat: number | null; lon: number | null }): void
}>()

const auth = useAuthStore()
const suggestions = ref<GeoSuggestion[]>([])
const open = ref(false)
const searching = ref(false)
const hint = ref("")
let timer: number | undefined

watch(
  () => props.address,
  () => {
    hint.value = ""
  },
)

function onInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  emit("update", { address: value, lat: null, lon: null })

  window.clearTimeout(timer)
  if (!auth.config?.geocoder_enabled || value.trim().length < 3) {
    suggestions.value = []
    open.value = false
    return
  }
  timer = window.setTimeout(() => void search(value), 350)
}

async function search(value: string) {
  searching.value = true
  try {
    suggestions.value = await api.geoSuggest(value)
    open.value = suggestions.value.length > 0
    hint.value = suggestions.value.length ? "" : "Ничего не нашлось — можно оставить адрес как есть"
  } catch {
    hint.value = "Подсказки сейчас недоступны, введите адрес вручную"
    open.value = false
  } finally {
    searching.value = false
  }
}

function pick(suggestion: GeoSuggestion) {
  emit("update", { address: suggestion.address, lat: suggestion.lat, lon: suggestion.lon })
  suggestions.value = []
  open.value = false
  hint.value = suggestion.lat ? "" : "У этого адреса нет координат — карта покажет поиск по названию"
}
</script>

<template>
  <div class="wrap">
    <label class="field">
      <span>Адрес</span>
      <input
        class="input"
        :value="address"
        type="text"
        autocomplete="off"
        placeholder="Улица и дом"
        @input="onInput"
        @focus="open = suggestions.length > 0"
      />
    </label>

    <ul v-if="open" class="list sheet">
      <li v-for="(suggestion, index) in suggestions" :key="index">
        <button type="button" @click="pick(suggestion)">
          <span class="value">{{ suggestion.address }}</span>
        </button>
      </li>
    </ul>

    <p class="note muted">
      <span v-if="searching">Ищем адрес…</span>
      <span v-else-if="hint">{{ hint }}</span>
      <span v-else-if="lat && lon">Координаты найдены — карта покажет точку</span>
      <span v-else-if="!auth.config?.geocoder_enabled">
        Подсказки адресов выключены: добавьте ключ DaData на сервере
      </span>
    </p>
  </div>
</template>

<style scoped>
.wrap {
  position: relative;
}

.field {
  margin-bottom: 0.25rem;
}

.list {
  position: absolute;
  z-index: 12;
  left: 0;
  right: 0;
  margin: 0;
  padding: 0.25rem;
  list-style: none;
  box-shadow: var(--shadow-lift);
  max-height: 260px;
  overflow: auto;
}

.list button {
  width: 100%;
  padding: 0.5rem 0.6rem;
  border: 0;
  border-radius: 7px;
  background: transparent;
  text-align: left;
  font-size: var(--small);
  cursor: pointer;
}

.list button:hover {
  background: var(--paper-deep);
}

.note {
  min-height: 1.25rem;
  margin: 0 0 0.75rem;
  font-size: var(--tiny);
}
</style>
