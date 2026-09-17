<script setup lang="ts">
import { ref } from "vue"

import { api, ApiError } from "../api/client"
import type { Photo } from "../api/types"
import { useAuthStore } from "../stores/auth"

const props = defineProps<{ visitId: number }>()
const emit = defineEmits<{ (event: "uploaded", photos: Photo[]): void }>()

const auth = useAuthStore()
const input = ref<HTMLInputElement | null>(null)
const busy = ref(false)
const error = ref("")

async function onPick(event: Event) {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files ?? [])
  if (!files.length) return

  busy.value = true
  error.value = ""
  try {
    emit("uploaded", await api.uploadPhotos(props.visitId, files))
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Не получилось загрузить"
  } finally {
    busy.value = false
    target.value = ""
  }
}
</script>

<template>
  <div class="uploader">
    <button class="btn btn--ghost" type="button" :disabled="busy" @click="input?.click()">
      {{ busy ? "Загружаем…" : "Добавить фотографии" }}
    </button>
    <input
      ref="input"
      class="visually-hidden"
      type="file"
      accept="image/*"
      multiple
      @change="onPick"
    />
    <p v-if="error" class="error-note">{{ error }}</p>
    <p v-else class="muted limit">До {{ auth.config?.max_upload_mb ?? 15 }} МБ на снимок</p>
  </div>
</template>

<style scoped>
.uploader {
  display: grid;
  gap: 0.4rem;
  justify-items: start;
}

.limit {
  margin: 0;
  font-size: var(--tiny);
}
</style>
