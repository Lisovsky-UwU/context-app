<script setup lang="ts">
import { onMounted, ref } from "vue"

import { ApiError } from "../api/client"
import { ACCENTS, accentVar } from "../lib/labels"
import { useCategoriesStore } from "../stores/categories"

const props = defineProps<{ modelValue: number | null }>()
const emit = defineEmits<{ (event: "update:modelValue", value: number | null): void }>()

const categories = useCategoriesStore()
const adding = ref(false)
const name = ref("")
const color = ref(ACCENTS[0].value)
const busy = ref(false)
const error = ref("")

function pick(id: number | null) {
  emit("update:modelValue", id)
}

function openForm() {
  adding.value = true
  error.value = ""
  color.value = ACCENTS[categories.items.length % ACCENTS.length].value
}

async function create() {
  if (!name.value.trim()) {
    error.value = "Впишите название"
    return
  }
  busy.value = true
  error.value = ""
  try {
    const category = await categories.create({ name: name.value.trim(), color: color.value })
    pick(category.id)
    name.value = ""
    adding.value = false
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Не удалось создать категорию"
  } finally {
    busy.value = false
  }
}

onMounted(() => categories.load())
</script>

<template>
  <div class="picker">
    <span class="label">Категория</span>

    <div class="chips">
      <button
        v-for="category in categories.items"
        :key="category.id"
        type="button"
        class="chip"
        :class="{ 'chip--on': modelValue === category.id }"
        :style="{ '--accent': accentVar(category.color) }"
        @click="pick(category.id)"
      >
        {{ category.name }}
      </button>

      <button
        type="button"
        class="chip chip--plain"
        :class="{ 'chip--on': modelValue === null }"
        @click="pick(null)"
      >
        Без категории
      </button>

      <button v-if="!adding" type="button" class="chip chip--add" @click="openForm">
        <span aria-hidden="true">+</span> Новая
      </button>
    </div>

    <div v-if="adding" class="form">
      <p v-if="error" class="error-note">{{ error }}</p>

      <input
        v-model="name"
        class="input"
        type="text"
        maxlength="40"
        placeholder="Например: Театр"
        @keydown.enter.prevent="create"
      />

      <div class="colors">
        <button
          v-for="accent in ACCENTS"
          :key="accent.value"
          type="button"
          class="swatch"
          :class="{ 'swatch--on': color === accent.value }"
          :style="{ background: accentVar(accent.value) }"
          :title="accent.label"
          @click="color = accent.value"
        >
          <span class="visually-hidden">{{ accent.label }}</span>
        </button>
      </div>

      <div class="form__actions">
        <button class="btn btn--quiet" type="button" @click="adding = false">Отмена</button>
        <button class="btn btn--ghost" type="button" :disabled="busy" @click="create">
          {{ busy ? "Создаём…" : "Добавить категорию" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.picker {
  margin-bottom: 1rem;
}

.label {
  display: block;
  margin-bottom: 0.4rem;
  font-size: var(--small);
  color: var(--ink-soft);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.chip {
  --accent: var(--edge-strong);
  min-height: 38px;
  padding: 0 0.85rem;
  border: 1px solid var(--edge-strong);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius-field);
  background: transparent;
  font-size: var(--small);
  cursor: pointer;
}

.chip--on {
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}

.chip--plain,
.chip--add {
  border-left-width: 1px;
  color: var(--ink-soft);
}

.chip--plain.chip--on {
  border-color: var(--ink-soft);
  color: var(--ink);
}

.chip--add {
  border-style: dashed;
}

.form {
  margin-top: 0.75rem;
  padding: 0.85rem;
  border: 1px solid var(--edge);
  border-radius: var(--radius-card);
  background: var(--card);
}

.colors {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 0.6rem 0;
}

.swatch {
  width: 30px;
  height: 30px;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
}

.swatch--on {
  border-color: var(--ink);
  transform: scale(1.08);
}

.form__actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
</style>
