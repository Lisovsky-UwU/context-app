<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"

import { api, ApiError } from "../api/client"
import type { Photo, PlaceDetail, Visit } from "../api/types"
import MapEmbed from "../components/MapEmbed.vue"
import PhotoStrip from "../components/PhotoStrip.vue"
import PhotoUploader from "../components/PhotoUploader.vue"
import VisitPlanner from "../components/VisitPlanner.vue"
import { formatDate, formatDateTime, relativeDay } from "../lib/format"
import { categoryLabel, plural } from "../lib/labels"
import { useAuthStore } from "../stores/auth"
import { usePlacesStore } from "../stores/places"

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const placesStore = usePlacesStore()

const placeId = Number(route.params.id)
const place = ref<PlaceDetail | null>(null)
const visits = ref<Visit[]>([])
const loading = ref(true)
const error = ref("")
const planning = ref(false)
const editingVisit = ref<Visit | null>(null)
const score = ref(0)
const reviewText = ref("")
const savingReview = ref(false)
const confirmingDelete = ref(false)

const planned = computed(() => visits.value.filter((visit) => visit.status === "planned"))
const past = computed(() =>
  visits.value
    .filter((visit) => visit.status === "done")
    .sort((a, b) => b.scheduled_date.localeCompare(a.scheduled_date)),
)
const otherReviews = computed(
  () => place.value?.reviews.filter((review) => review.user.id !== auth.user?.id) ?? [],
)

async function load() {
  loading.value = true
  try {
    const [detail, visitList] = await Promise.all([
      api.place(placeId),
      api.visits({ place_id: placeId }),
    ])
    place.value = detail
    visits.value = visitList
    score.value = detail.my_review?.score ?? 0
    reviewText.value = detail.my_review?.text ?? ""
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Не удалось открыть место"
  } finally {
    loading.value = false
  }
}

async function refreshPlace() {
  place.value = await api.place(placeId)
  placesStore.patch(place.value)
  void placesStore.loadUpcoming()
}

async function toggleInterest() {
  if (!place.value) return
  place.value = await api.setInterest(place.value.id, !place.value.interested)
  placesStore.patch(place.value)
}

function closePlanner() {
  planning.value = false
  editingVisit.value = null
}

async function afterVisitChange(saved: Visit) {
  closePlanner()
  const index = visits.value.findIndex((visit) => visit.id === saved.id)
  if (index >= 0) visits.value[index] = saved
  else visits.value.push(saved)
  await refreshPlace()
}

async function markDone(visit: Visit) {
  const updated = await api.updateVisit(visit.id, { status: "done" })
  visits.value = visits.value.map((item) => (item.id === updated.id ? updated : item))
  await refreshPlace()
}

async function cancelVisit(visit: Visit) {
  await api.deleteVisit(visit.id)
  visits.value = visits.value.filter((item) => item.id !== visit.id)
  await refreshPlace()
}

function onUploaded(visit: Visit, photos: Photo[]) {
  visit.photos = [...visit.photos, ...photos]
  void refreshPlace()
}

function onPhotoRemoved(visit: Visit, id: number) {
  visit.photos = visit.photos.filter((photo) => photo.id !== id)
  void refreshPlace()
}

async function saveReview() {
  if (!place.value || !score.value) return
  savingReview.value = true
  try {
    place.value = await api.saveReview(place.value.id, score.value, reviewText.value)
    placesStore.patch(place.value)
  } finally {
    savingReview.value = false
  }
}

async function removePlace() {
  await api.deletePlace(placeId)
  await placesStore.load()
  router.push({ name: "places" })
}

onMounted(load)
</script>

<template>
  <div class="page">
    <p v-if="loading" class="muted">Открываем карточку…</p>
    <p v-else-if="error" class="error-note">{{ error }}</p>

    <template v-else-if="place">
      <RouterLink class="back btn btn--quiet" :to="{ name: 'places' }">К списку</RouterLink>

      <header class="head">
        <div>
          <p class="kind" :class="`kind--${place.category}`">{{ categoryLabel(place.category) }}</p>
          <h1>{{ place.title }}</h1>
          <p v-if="place.address" class="muted address">{{ place.address }}</p>
        </div>

        <button
          class="want"
          :class="{ 'want--on': place.interested }"
          type="button"
          @click="toggleInterest"
        >
          <span aria-hidden="true">{{ place.interested ? "♥" : "♡" }}</span>
          {{ place.interested ? "Хочу сюда" : "Тоже хочу" }}
        </button>
      </header>

      <p v-if="place.interest_count" class="muted wanters">
        {{ place.interest_count }} {{ plural(place.interest_count, "голос", "голоса", "голосов") }}:
        {{ place.interested_by.map((person) => person.display_name).join(", ") }}
      </p>

      <p v-if="place.description" class="description">{{ place.description }}</p>

      <a
        v-if="place.website_url"
        class="site"
        :href="place.website_url"
        target="_blank"
        rel="noreferrer noopener"
      >
        Сайт заведения
      </a>

      <MapEmbed class="map" :address="place.address" :lat="place.lat" :lon="place.lon" />

      <section class="block">
        <div class="block__head">
          <h2>Походы</h2>
          <button class="btn btn--primary" type="button" @click="planning = true">
            Назначить дату
          </button>
        </div>

        <article v-for="visit in planned" :key="visit.id" class="visit visit--planned">
          <div class="visit__when">
            <strong>{{ relativeDay(visit.scheduled_date) }}</strong>
            <span class="muted small">
              {{ formatDateTime(visit.scheduled_date, visit.scheduled_time) }}
            </span>
          </div>
          <p v-if="visit.participants.length" class="muted small">
            Идут: {{ visit.participants.map((person) => person.display_name).join(", ") }}
          </p>
          <p v-if="visit.note" class="note">{{ visit.note }}</p>
          <div class="visit__actions">
            <button class="btn btn--ghost" type="button" @click="markDone(visit)">Сходили</button>
            <button class="btn btn--quiet" type="button" @click="editingVisit = visit">
              Перенести
            </button>
            <button class="btn btn--quiet" type="button" @click="cancelVisit(visit)">Отменить</button>
          </div>
        </article>

        <article v-for="visit in past" :key="visit.id" class="visit">
          <div class="visit__when">
            <strong>{{ formatDate(visit.scheduled_date, { year: true }) }}</strong>
            <span v-if="visit.participants.length" class="muted small">
              {{ visit.participants.map((person) => person.display_name).join(", ") }}
            </span>
          </div>
          <p v-if="visit.note" class="note">{{ visit.note }}</p>

          <PhotoStrip
            v-if="visit.photos.length"
            :photos="visit.photos"
            can-delete
            @removed="(id) => onPhotoRemoved(visit, id)"
          />
          <PhotoUploader :visit-id="visit.id" @uploaded="(photos) => onUploaded(visit, photos)" />
        </article>

        <p v-if="!planned.length && !past.length" class="muted small">
          Ещё не ходили. Назначьте дату — её увидят все.
        </p>
      </section>

      <section class="block">
        <h2>Впечатления</h2>

        <div class="rating">
          <button
            v-for="star in 5"
            :key="star"
            class="star"
            :class="{ 'star--on': star <= score }"
            type="button"
            :aria-label="`Оценка ${star} из 5`"
            @click="score = star"
          >
            ★
          </button>
          <span v-if="place.average_score" class="muted small">
            средняя {{ place.average_score }}
          </span>
        </div>

        <textarea
          v-model="reviewText"
          class="textarea"
          rows="3"
          placeholder="Как прошло? Что заказать в следующий раз?"
        />
        <button
          class="btn btn--ghost save"
          type="button"
          :disabled="!score || savingReview"
          @click="saveReview"
        >
          {{ savingReview ? "Сохраняем…" : "Сохранить отзыв" }}
        </button>

        <ul v-if="otherReviews.length" class="reviews">
          <li v-for="review in otherReviews" :key="review.id">
            <p class="review__head">
              <strong>{{ review.user.display_name }}</strong>
              <span class="muted small">{{ review.score }} из 5</span>
            </p>
            <p v-if="review.text" class="review__text">{{ review.text }}</p>
          </li>
        </ul>
      </section>

      <footer class="tools">
        <RouterLink class="btn btn--quiet" :to="{ name: 'place-edit', params: { id: place.id } }">
          Редактировать
        </RouterLink>
        <button
          v-if="!confirmingDelete"
          class="btn btn--quiet"
          type="button"
          @click="confirmingDelete = true"
        >
          Удалить место
        </button>
        <template v-else>
          <span class="muted small">Удалить вместе с фотографиями?</span>
          <button class="btn btn--quiet danger" type="button" @click="removePlace">
            Да, удалить
          </button>
          <button class="btn btn--quiet" type="button" @click="confirmingDelete = false">
            Оставить
          </button>
        </template>
      </footer>

      <VisitPlanner
        v-if="planning || editingVisit"
        :place-id="place.id"
        :place-title="place.title"
        :visit="editingVisit"
        @close="closePlanner"
        @saved="afterVisitChange"
      />
    </template>
  </div>
</template>

<style scoped>
.back {
  margin-left: -0.6rem;
  text-decoration: none;
}

.head {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin: 0.25rem 0 0.5rem;
}

.head > div {
  flex: 1;
  min-width: 0;
}

.kind {
  margin: 0 0 0.25rem;
  font-size: var(--tiny);
  font-weight: 600;
  color: var(--cat-other);
}

.kind--bar { color: var(--cat-bar); }
.kind--cafe { color: var(--cat-cafe); }
.kind--restaurant { color: var(--cat-restaurant); }
.kind--culture { color: var(--cat-culture); }
.kind--activity { color: var(--cat-activity); }
.kind--nature { color: var(--cat-nature); }

h1 {
  font-size: var(--step-3);
  overflow-wrap: anywhere;
}

.address {
  margin: 0.35rem 0 0;
  font-size: var(--small);
}

.want {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 40px;
  padding: 0 0.9rem;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-pill);
  background: transparent;
  font-size: var(--small);
  white-space: nowrap;
  cursor: pointer;
}

.want--on {
  border-color: var(--pomegranate);
  color: var(--pomegranate);
  background: var(--pomegranate-soft);
}

.wanters {
  margin: 0 0 1rem;
  font-size: var(--small);
}

.description {
  margin: 0 0 1rem;
  white-space: pre-line;
}

.site {
  display: inline-block;
  margin-bottom: 1.25rem;
  font-size: var(--small);
}

.map {
  margin-bottom: 1.75rem;
}

.block {
  padding-top: 1.25rem;
  margin-bottom: 1.75rem;
  border-top: 1px solid var(--edge);
}

.block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.visit {
  display: grid;
  gap: 0.5rem;
  padding: 0.9rem 1rem;
  margin-bottom: 0.75rem;
  border: 1px solid var(--edge);
  border-radius: var(--radius-card);
  background: var(--card);
}

.visit--planned {
  border-color: var(--amber);
  background: var(--amber-soft);
}

.visit__when {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  flex-wrap: wrap;
  font-family: var(--font-display);
}

.visit__actions {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.note {
  margin: 0;
  font-size: var(--small);
}

.small {
  font-size: var(--small);
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  margin-bottom: 0.6rem;
}

.star {
  padding: 0.1rem;
  border: 0;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--edge-strong);
  cursor: pointer;
}

.star--on {
  color: var(--amber);
}

.rating .small {
  margin-left: 0.5rem;
}

.save {
  margin-top: 0.6rem;
}

.reviews {
  display: grid;
  gap: 0.75rem;
  margin: 1.25rem 0 0;
  padding: 0;
  list-style: none;
}

.review__head {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  margin: 0;
}

.review__text {
  margin: 0.1rem 0 0;
  font-size: var(--small);
}

.tools {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding-top: 1rem;
  border-top: 1px solid var(--edge);
}

.tools .btn {
  text-decoration: none;
}

.danger {
  color: var(--pomegranate);
}
</style>
