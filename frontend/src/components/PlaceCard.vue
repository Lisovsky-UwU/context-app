<script setup lang="ts">
import { computed } from "vue"
import { RouterLink } from "vue-router"

import type { Place } from "../api/types"
import { plural, categoryLabel } from "../lib/labels"
import StatusStamp from "./StatusStamp.vue"

const props = defineProps<{ place: Place }>()

const meta = computed(() => {
  const parts = [categoryLabel(props.place.category)]
  if (props.place.address) parts.push(props.place.address.replace(/^Россия,\s*/, ""))
  return parts.join(" — ")
})

const photoNote = computed(() =>
  props.place.photo_count
    ? `${props.place.photo_count} ${plural(props.place.photo_count, "фото", "фото", "фото")}`
    : "",
)
</script>

<template>
  <RouterLink :to="{ name: 'place', params: { id: place.id } }" class="card" :class="`card--${place.category}`">
    <span class="rail" aria-hidden="true" />

    <span class="body">
      <span class="title">{{ place.title }}</span>
      <span class="meta">{{ meta }}</span>

      <span class="marks">
        <span v-if="place.interest_count" class="mark">
          {{ place.interest_count }} {{ plural(place.interest_count, "хочет", "хотят", "хотят") }}
        </span>
        <span v-if="place.average_score" class="mark">{{ place.average_score }} из 5</span>
        <span v-if="photoNote" class="mark">{{ photoNote }}</span>
      </span>
    </span>

    <img v-if="place.cover_url" class="cover" :src="place.cover_url" alt="" loading="lazy" />
    <StatusStamp :place="place" />
  </RouterLink>
</template>

<style scoped>
.card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.85rem 1rem 0.85rem 1.4rem;
  background: var(--card);
  border: 1px solid var(--edge);
  border-radius: var(--radius-card);
  text-decoration: none;
  overflow: hidden;
}

.card:hover {
  border-color: var(--edge-strong);
}

.rail {
  position: absolute;
  inset: 0 auto 0 0;
  width: var(--rail);
  background: var(--cat-other);
}

.card--bar .rail { background: var(--cat-bar); }
.card--cafe .rail { background: var(--cat-cafe); }
.card--restaurant .rail { background: var(--cat-restaurant); }
.card--culture .rail { background: var(--cat-culture); }
.card--activity .rail { background: var(--cat-activity); }
.card--nature .rail { background: var(--cat-nature); }

.body {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
  flex: 1;
}

.title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--step-1);
  letter-spacing: -0.02em;
  overflow-wrap: anywhere;
}

.meta {
  font-size: var(--small);
  color: var(--ink-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.marks {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 0.2rem;
  font-size: var(--tiny);
  color: var(--ink-faint);
}

.cover {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--edge);
}

@media (max-width: 480px) {
  .cover {
    width: 52px;
    height: 52px;
  }
}
</style>
