<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue"
import { RouterLink } from "vue-router"

import { api } from "../api/client"
import type { Place, Visit } from "../api/types"
import EmptyNote from "../components/EmptyNote.vue"
import VisitPlanner from "../components/VisitPlanner.vue"
import { categoryLabel } from "../lib/labels"
import { useCategoriesStore } from "../stores/categories"
import { usePlacesStore } from "../stores/places"

const ITEM_HEIGHT = 72
const SPIN_MS = 2600

const placesStore = usePlacesStore()
const categories = useCategoriesStore()

const pool = ref<Place[]>([])
const loading = ref(true)
const category = ref<number>(0)
const strip = ref<Place[]>([])
const offset = ref(0)
const spinning = ref(false)
const running = ref(false)
const winner = ref<Place | null>(null)
const planning = ref(false)
const planned = ref<Visit | null>(null)
const manualOpen = ref(false)

// Настройку читаем в момент прокрута: если её переключили, приложение подхватит это без перезагрузки.
const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches
const transition = computed(() =>
  spinning.value ? `transform ${SPIN_MS}ms cubic-bezier(0.12, 0.72, 0.1, 1)` : "none",
)
const sortedPool = computed(() => [...pool.value].sort((a, b) => a.title.localeCompare(b.title, "ru")))

async function loadPool() {
  loading.value = true
  try {
    pool.value = await api.roulettePool({ category_id: category.value || undefined })
    resetReel()
  } finally {
    loading.value = false
  }
}

const randomPlace = () => pool.value[Math.floor(Math.random() * pool.value.length)]

/** Случайное место, отличное от перечисленных, — чтобы соседние строки не повторялись. */
function randomOther(...exclude: (Place | undefined)[]): Place {
  const banned = new Set(exclude.filter(Boolean).map((place) => place!.id))
  const options = pool.value.filter((place) => !banned.has(place.id))
  const source = options.length ? options : pool.value
  return source[Math.floor(Math.random() * source.length)]
}

/** В окне видно три строки, выбранная всегда посередине. */
function showStill(place: Place) {
  const above = randomOther(place)
  strip.value = [above, place, randomOther(place, above)]
  offset.value = 0
}

function resetReel() {
  winner.value = null
  planned.value = null
  if (pool.value.length) showStill(randomPlace())
  else {
    strip.value = []
    offset.value = 0
  }
}

/** Место, которое многие хотят, выпадает чуть чаще: каждый голос — лишний билет. */
function pickWeighted(candidates: Place[]): Place {
  const tickets: Place[] = []
  candidates.forEach((place) => {
    const weight = 1 + Math.min(place.interest_count, 4)
    for (let index = 0; index < weight; index += 1) tickets.push(place)
  })
  return tickets[Math.floor(Math.random() * tickets.length)]
}

const nextFrame = () =>
  new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))

async function spin() {
  if (!pool.value.length || running.value) return

  const candidates = winner.value ? pool.value.filter((item) => item.id !== winner.value?.id) : pool.value
  const target = pickWeighted(candidates.length ? candidates : pool.value)

  running.value = true
  planned.value = null
  winner.value = null

  if (prefersReducedMotion()) {
    showStill(target)
    winner.value = target
    running.value = false
    return
  }

  // Лента начинается с тех строк, что сейчас в окне, — иначе барабан дёргается на старте.
  const head = strip.value.slice(0, 2)

  // Дальше случайные названия, выпавшее место стоит на известной позиции.
  // Соседние строки не повторяются, иначе барабан выглядит сломанным.
  const filler: Place[] = []
  const length = Math.max(18, pool.value.length * 3)
  while (filler.length < length) {
    const previous = filler.at(-1) ?? head.at(-1)
    const isLast = filler.length === length - 1
    filler.push(randomOther(previous, isLast ? target : undefined))
  }
  const after = randomOther(target)

  const targetIndex = head.length + filler.length
  strip.value = [...head, ...filler, target, after, randomOther(after)]

  // Сначала ставим ленту в начало без плавности…
  spinning.value = false
  offset.value = 0
  await nextTick()
  await nextFrame()

  // …и только следующим кадром включаем её и запускаем прокрутку.
  spinning.value = true
  await nextTick()
  offset.value = (targetIndex - 1) * ITEM_HEIGHT

  window.setTimeout(() => {
    spinning.value = false
    winner.value = target
    running.value = false
  }, SPIN_MS)
}

function choose(place: Place) {
  winner.value = place
  planned.value = null
  manualOpen.value = false
  showStill(place)
}

async function onPlanned(visit: Visit) {
  planning.value = false
  planned.value = visit
  await Promise.all([placesStore.load(), placesStore.loadUpcoming()])
  pool.value = pool.value.filter((place) => place.id !== visit.place.id)
}

onMounted(async () => {
  await Promise.all([loadPool(), categories.load()])
})
</script>

<template>
  <div class="page">
    <header class="intro">
      <h1>Рулетка</h1>
      <p class="muted">
        Крутим только то, куда ещё не ходили. Не понравилось — крутите ещё раз или выберите сами.
      </p>
    </header>

    <div class="controls">
      <select v-model="category" class="select" @change="loadPool">
        <option :value="0">Любая категория</option>
        <option v-for="option in categories.items" :key="option.id" :value="option.id">
          {{ option.name }}
        </option>
      </select>
      <span class="muted count">{{ pool.length }} в барабане</span>
    </div>

    <p v-if="loading" class="muted">Заряжаем барабан…</p>

    <EmptyNote
      v-else-if="!pool.length"
      title="Крутить нечего"
      hint="Все места этой категории уже посещены или назначены. Добавьте новое — и рулетка оживёт."
    >
      <RouterLink class="btn btn--primary" :to="{ name: 'place-new' }">Добавить место</RouterLink>
    </EmptyNote>

    <template v-else>
      <div class="reel" :class="{ 'reel--live': spinning }">
        <div class="reel__window">
          <ul class="reel__strip" :style="{ transform: `translateY(-${offset}px)`, transition }">
            <li v-for="(place, index) in strip" :key="`${place.id}-${index}`" class="reel__item">
              <span class="reel__title">{{ place.title }}</span>
              <span class="reel__kind">{{ categoryLabel(place.category) }}</span>
            </li>
          </ul>
        </div>
        <span class="reel__line" aria-hidden="true" />
      </div>

      <div class="actions">
        <button class="btn btn--primary" type="button" :disabled="running" @click="spin">
          {{ winner ? "Крутить ещё" : "Крутить" }}
        </button>
        <button
          v-if="winner && !planned"
          class="btn btn--ghost"
          type="button"
          :disabled="running"
          @click="planning = true"
        >
          Идём сюда
        </button>
      </div>

      <section v-if="winner && !running" class="result">
        <p v-if="planned" class="done">
          Договорились: {{ winner.title }}. Дата уже видна всем в списке.
        </p>
        <RouterLink class="result__link" :to="{ name: 'place', params: { id: winner.id } }">
          Открыть карточку места
        </RouterLink>
      </section>

      <section class="manual">
        <button class="btn btn--quiet" type="button" @click="manualOpen = !manualOpen">
          {{ manualOpen ? "Свернуть список" : "Выбрать место самому" }}
        </button>
        <ul v-if="manualOpen" class="manual__list">
          <li v-for="place in sortedPool" :key="place.id">
            <button type="button" @click="choose(place)">
              <span>{{ place.title }}</span>
              <span class="muted">{{ categoryLabel(place.category) }}</span>
            </button>
          </li>
        </ul>
      </section>
    </template>

    <VisitPlanner
      v-if="planning && winner"
      :place-id="winner.id"
      :place-title="winner.title"
      @close="planning = false"
      @saved="onPlanned"
    />
  </div>
</template>

<style scoped>
.intro {
  margin-bottom: 1.25rem;
}

.intro h1 {
  font-size: var(--step-3);
  margin-bottom: 0.3rem;
}

.intro p {
  font-size: var(--small);
}

.controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.controls .select {
  width: auto;
  min-width: 180px;
}

.count {
  font-size: var(--small);
}

.reel {
  position: relative;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-card);
  background: var(--card);
  overflow: hidden;
}

.reel::before,
.reel::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  height: 56px;
  pointer-events: none;
  z-index: 2;
}

.reel::before {
  top: 0;
  background: linear-gradient(var(--card), transparent);
}

.reel::after {
  bottom: 0;
  background: linear-gradient(transparent, var(--card));
}

.reel__window {
  height: 216px;
  overflow: hidden;
}

.reel__strip {
  margin: 0;
  padding: 0;
  list-style: none;
  will-change: transform;
}

.reel__item {
  display: grid;
  align-content: center;
  gap: 0.15rem;
  height: 72px;
  padding: 0 1.25rem;
  text-align: center;
}

.reel__title {
  font-family: var(--font-display);
  font-size: var(--step-2);
  font-weight: 600;
  letter-spacing: -0.02em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reel__kind {
  font-size: var(--tiny);
  color: var(--ink-faint);
}

.reel--live .reel__title {
  filter: blur(0.4px);
}

.reel__line {
  position: absolute;
  inset: 72px 0 auto 0;
  height: 72px;
  border-top: 2px solid var(--pomegranate);
  border-bottom: 2px solid var(--pomegranate);
  pointer-events: none;
}

.actions {
  display: flex;
  gap: 0.6rem;
  margin: 1.25rem 0 0;
}

.actions .btn {
  flex: 1;
}

.result {
  display: grid;
  gap: 0.5rem;
  justify-items: start;
  margin-top: 1.25rem;
}

.done {
  margin: 0;
  padding: 0.7rem 0.85rem;
  border-left: 3px solid var(--mint);
  background: var(--mint-soft);
  border-radius: 0 var(--radius-field) var(--radius-field) 0;
  font-size: var(--small);
}

.result__link {
  font-size: var(--small);
}

.manual {
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--edge);
}

.manual__list {
  display: grid;
  gap: 0.25rem;
  margin: 0.75rem 0 0;
  padding: 0;
  list-style: none;
}

.manual__list button {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  min-height: 44px;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--edge);
  border-radius: var(--radius-field);
  background: var(--card);
  text-align: left;
  font-size: var(--small);
  cursor: pointer;
}

.manual__list button:hover {
  border-color: var(--edge-strong);
}
</style>
