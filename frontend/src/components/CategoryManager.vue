<script setup lang="ts">
import { onMounted, ref } from "vue"

import { ApiError } from "../api/client"
import type { Category } from "../api/types"
import { ACCENTS, accentVar } from "../lib/labels"
import { useCategoriesStore } from "../stores/categories"
import { usePlacesStore } from "../stores/places"

const categories = useCategoriesStore()
const places = usePlacesStore()

const editingColor = ref<number | null>(null)
const removing = ref<Category | null>(null)
const moveTo = ref<number>(0)
const newName = ref("")
const newColor = ref(ACCENTS[0].value)
const adding = ref(false)
const error = ref("")

function report(exception: unknown, fallback: string) {
  error.value = exception instanceof ApiError ? exception.message : fallback
}

async function rename(category: Category, event: Event) {
  const value = (event.target as HTMLInputElement).value.trim()
  if (!value || value === category.name) {
    ;(event.target as HTMLInputElement).value = category.name
    return
  }
  error.value = ""
  try {
    await categories.update(category.id, { name: value })
    await places.load()
  } catch (exception) {
    ;(event.target as HTMLInputElement).value = category.name
    report(exception, "Не удалось переименовать")
  }
}

async function recolor(category: Category, color: string) {
  editingColor.value = null
  error.value = ""
  try {
    await categories.update(category.id, { color })
    await places.load()
  } catch (exception) {
    report(exception, "Не удалось поменять цвет")
  }
}

function askRemove(category: Category) {
  removing.value = category
  moveTo.value = 0
  error.value = ""
}

async function confirmRemove() {
  if (!removing.value) return
  const category = removing.value
  try {
    await categories.remove(category.id, category.place_count ? moveTo.value : undefined)
    removing.value = null
    await Promise.all([categories.load(true), places.load()])
  } catch (exception) {
    report(exception, "Не удалось удалить категорию")
  }
}

async function create() {
  if (!newName.value.trim()) return
  error.value = ""
  try {
    await categories.create({ name: newName.value.trim(), color: newColor.value })
    newName.value = ""
    adding.value = false
  } catch (exception) {
    report(exception, "Не удалось создать категорию")
  }
}

onMounted(() => categories.load(true))
</script>

<template>
  <div>
    <p v-if="error" class="error-note">{{ error }}</p>

    <ul class="rows">
      <li v-for="category in categories.items" :key="category.id">
        <div class="row">
          <button
            type="button"
            class="dot"
            :style="{ background: accentVar(category.color) }"
            :title="`Цвет категории «${category.name}»`"
            @click="editingColor = editingColor === category.id ? null : category.id"
          >
            <span class="visually-hidden">Поменять цвет</span>
          </button>

          <input
            class="input name"
            type="text"
            maxlength="40"
            :value="category.name"
            @blur="rename(category, $event)"
            @keydown.enter="($event.target as HTMLInputElement).blur()"
          />

          <span class="count muted">{{ category.place_count }}</span>

          <button class="btn btn--quiet" type="button" @click="askRemove(category)">Удалить</button>
        </div>

        <div v-if="editingColor === category.id" class="colors">
          <button
            v-for="accent in ACCENTS"
            :key="accent.value"
            type="button"
            class="swatch"
            :class="{ 'swatch--on': category.color === accent.value }"
            :style="{ background: accentVar(accent.value) }"
            :title="accent.label"
            @click="recolor(category, accent.value)"
          >
            <span class="visually-hidden">{{ accent.label }}</span>
          </button>
        </div>

        <div v-if="removing?.id === category.id" class="confirm">
          <template v-if="category.place_count">
            <p class="muted small">
              В категории {{ category.place_count }} мест. Куда их перенести?
            </p>
            <select v-model="moveTo" class="select">
              <option :value="0">Оставить без категории</option>
              <option
                v-for="option in categories.items.filter((item) => item.id !== category.id)"
                :key="option.id"
                :value="option.id"
              >
                {{ option.name }}
              </option>
            </select>
          </template>
          <p v-else class="muted small">Удалить категорию «{{ category.name }}»?</p>

          <div class="confirm__actions">
            <button class="btn btn--quiet" type="button" @click="removing = null">Отмена</button>
            <button class="btn btn--quiet danger" type="button" @click="confirmRemove">
              Удалить
            </button>
          </div>
        </div>
      </li>
    </ul>

    <div v-if="adding" class="add">
      <input
        v-model="newName"
        class="input"
        type="text"
        maxlength="40"
        placeholder="Название категории"
        @keydown.enter.prevent="create"
      />
      <div class="colors">
        <button
          v-for="accent in ACCENTS"
          :key="accent.value"
          type="button"
          class="swatch"
          :class="{ 'swatch--on': newColor === accent.value }"
          :style="{ background: accentVar(accent.value) }"
          :title="accent.label"
          @click="newColor = accent.value"
        >
          <span class="visually-hidden">{{ accent.label }}</span>
        </button>
      </div>
      <div class="confirm__actions">
        <button class="btn btn--quiet" type="button" @click="adding = false">Отмена</button>
        <button class="btn btn--ghost" type="button" @click="create">Добавить</button>
      </div>
    </div>

    <button v-else class="btn btn--ghost" type="button" @click="adding = true">
      Новая категория
    </button>
  </div>
</template>

<style scoped>
.rows {
  display: grid;
  gap: 0.5rem;
  margin: 0 0 1rem;
  padding: 0;
  list-style: none;
}

.row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.dot {
  width: 28px;
  height: 28px;
  flex: none;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
}

.name {
  flex: 1;
  min-width: 0;
  min-height: 40px;
}

.count {
  min-width: 1.5rem;
  text-align: right;
  font-size: var(--small);
}

.colors {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 0.5rem 0 0.25rem 2.2rem;
}

.swatch {
  width: 28px;
  height: 28px;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
}

.swatch--on {
  border-color: var(--ink);
}

.confirm {
  display: grid;
  gap: 0.5rem;
  margin: 0.5rem 0 0.25rem 2.2rem;
  padding: 0.75rem;
  border: 1px solid var(--edge);
  border-radius: var(--radius-field);
  background: var(--card);
}

.confirm p {
  margin: 0;
}

.small {
  font-size: var(--small);
}

.confirm__actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.danger {
  color: var(--pomegranate);
}

.add {
  display: grid;
  gap: 0.5rem;
  padding: 0.85rem;
  border: 1px solid var(--edge);
  border-radius: var(--radius-card);
  background: var(--card);
}
</style>
