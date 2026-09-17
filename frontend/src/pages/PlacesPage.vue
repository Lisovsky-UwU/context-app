<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { RouterLink } from "vue-router"

import EmptyNote from "../components/EmptyNote.vue"
import PlaceCard from "../components/PlaceCard.vue"
import type { PlaceStatus } from "../api/types"
import { formatDateTime, relativeDay } from "../lib/format"
import { useCategoriesStore } from "../stores/categories"
import { usePlacesStore } from "../stores/places"

const places = usePlacesStore()
const categories = useCategoriesStore()
const tab = ref<PlaceStatus>("wish")

const TABS: { value: PlaceStatus; label: string }[] = [
  { value: "wish", label: "Хотим" },
  { value: "planned", label: "Идём" },
  { value: "visited", label: "Были" },
]

const visible = computed(() => places.byStatus(tab.value))
const nextOuting = computed(() => places.upcoming[0] ?? null)

const emptyCopy: Record<PlaceStatus, { title: string; hint: string }> = {
  wish: {
    title: "Список пуст",
    hint: "Добавьте первое место — потом рулетка сама выберет, куда идти.",
  },
  planned: {
    title: "Ничего не запланировано",
    hint: "Покрутите рулетку или откройте место и назначьте дату.",
  },
  visited: {
    title: "Пока не отмечено ни одного похода",
    hint: "После похода отметьте его в карточке места и добавьте фотографии.",
  },
}

let timer: number | undefined
watch(
  () => places.query,
  () => {
    window.clearTimeout(timer)
    timer = window.setTimeout(() => void places.load(), 300)
  },
)
watch(() => places.category, () => void places.load())

onMounted(async () => {
  await Promise.all([places.load(), places.loadUpcoming(), categories.load()])
})
</script>

<template>
  <div class="page">
    <section v-if="nextOuting" class="next">
      <div class="next__when">
        <span class="next__day">{{ relativeDay(nextOuting.scheduled_date) }}</span>
        <span class="next__exact">{{ formatDateTime(nextOuting.scheduled_date, nextOuting.scheduled_time) }}</span>
      </div>
      <RouterLink class="next__place" :to="{ name: 'place', params: { id: nextOuting.place.id } }">
        {{ nextOuting.place.title }}
      </RouterLink>
      <p v-if="nextOuting.participants.length" class="next__who muted">
        {{ nextOuting.participants.map((person) => person.display_name).join(", ") }}
      </p>
    </section>

    <div class="tabs" role="tablist">
      <button
        v-for="item in TABS"
        :key="item.value"
        class="tab"
        :class="{ 'tab--on': tab === item.value }"
        role="tab"
        :aria-selected="tab === item.value"
        type="button"
        @click="tab = item.value"
      >
        {{ item.label }}
        <span class="tab__count">{{ places.counts[item.value] }}</span>
      </button>
    </div>

    <div class="filters">
      <input
        v-model="places.query"
        class="input search"
        type="search"
        placeholder="Поиск по названию или адресу"
      />
      <select v-model="places.category" class="select kind">
        <option :value="0">Все категории</option>
        <option v-for="option in categories.items" :key="option.id" :value="option.id">
          {{ option.name }}
        </option>
      </select>
    </div>

    <p v-if="places.loading" class="muted status">Собираем картотеку…</p>

    <ul v-else-if="visible.length" class="list">
      <li v-for="place in visible" :key="place.id">
        <PlaceCard :place="place" />
      </li>
    </ul>

    <EmptyNote
      v-else
      :title="emptyCopy[tab].title"
      :hint="emptyCopy[tab].hint"
    >
      <RouterLink class="btn btn--primary" :to="{ name: 'place-new' }">Добавить место</RouterLink>
    </EmptyNote>
  </div>
</template>

<style scoped>
.next {
  display: grid;
  gap: 0.2rem;
  padding: 1rem 1.1rem;
  margin-bottom: 1.5rem;
  border: 1px solid var(--amber);
  border-left-width: 5px;
  border-radius: var(--radius-card);
  background: var(--amber-soft);
}

.next__when {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.next__day {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--amber);
}

.next__exact {
  font-size: var(--tiny);
  color: var(--ink-soft);
}

.next__place {
  font-family: var(--font-display);
  font-size: var(--step-2);
  font-weight: 600;
  letter-spacing: -0.02em;
  text-decoration: none;
}

.next__who {
  margin: 0;
  font-size: var(--small);
}

.tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 1px solid var(--edge-strong);
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.9rem;
  margin-bottom: -1px;
  border: 1px solid transparent;
  border-bottom: 0;
  border-radius: 8px 8px 0 0;
  background: transparent;
  font-family: var(--font-display);
  font-size: var(--small);
  font-weight: 500;
  color: var(--ink-soft);
  cursor: pointer;
}

.tab--on {
  background: var(--card);
  border-color: var(--edge-strong);
  color: var(--ink);
}

.tab__count {
  font-family: var(--font-text);
  font-size: var(--tiny);
  color: var(--ink-faint);
}

.filters {
  display: flex;
  gap: 0.6rem;
  margin: 1rem 0 1.25rem;
}

.search {
  flex: 1;
}

.kind {
  width: auto;
  min-width: 150px;
}

.status {
  padding: 2rem 0;
}

.list {
  display: grid;
  gap: 0.6rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

@media (max-width: 520px) {
  .filters {
    flex-direction: column;
  }

  .kind {
    width: 100%;
  }
}
</style>
