<script setup lang="ts">
import { ref } from "vue"

import { api } from "../api/client"
import type { Photo } from "../api/types"

const props = defineProps<{ photos: Photo[]; canDelete?: boolean }>()
const emit = defineEmits<{ (event: "removed", id: number): void }>()

const active = ref<Photo | null>(null)
const removing = ref<number | null>(null)

async function remove(photo: Photo) {
  removing.value = photo.id
  try {
    await api.deletePhoto(photo.id)
    if (active.value?.id === photo.id) active.value = null
    emit("removed", photo.id)
  } finally {
    removing.value = null
  }
}
</script>

<template>
  <div>
    <ul class="strip">
      <li v-for="(photo, index) in photos" :key="photo.id" :style="{ '--tilt': `${((index % 3) - 1) * 1.1}deg` }">
        <button type="button" class="shot" @click="active = photo">
          <img :src="photo.thumb_url" :alt="photo.caption || 'Фотография с посещения'" loading="lazy" />
        </button>
      </li>
    </ul>

    <div v-if="active" class="lightbox" @click.self="active = null">
      <img :src="active.url" :alt="active.caption || 'Фотография с посещения'" />
      <div class="lightbox__bar">
        <span class="lightbox__caption">
          {{ active.caption || active.uploaded_by?.display_name || "" }}
        </span>
        <button
          v-if="canDelete"
          class="btn btn--quiet"
          type="button"
          :disabled="removing === active.id"
          @click="remove(active)"
        >
          Удалить
        </button>
        <button class="btn btn--quiet" type="button" @click="active = null">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.shot {
  padding: 5px 5px 16px;
  border: 1px solid var(--edge);
  border-radius: 3px;
  background: var(--card);
  box-shadow: var(--shadow-stamp);
  transform: rotate(var(--tilt, 0deg));
  cursor: pointer;
}

.shot img {
  display: block;
  width: 116px;
  height: 92px;
  object-fit: cover;
  border-radius: 1px;
}

.lightbox {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(12, 8, 18, 0.92);
}

.lightbox img {
  justify-self: center;
  align-self: center;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

.lightbox__bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: flex-end;
  color: #f4eef9;
}

.lightbox__caption {
  margin-right: auto;
  font-size: var(--small);
}

.lightbox .btn--quiet {
  color: #f4eef9;
}
</style>
