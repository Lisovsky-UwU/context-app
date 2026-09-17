<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { api, ApiError } from "../api/client"
import AddressField from "../components/AddressField.vue"
import CategoryPicker from "../components/CategoryPicker.vue"
import { usePlacesStore } from "../stores/places"

const route = useRoute()
const router = useRouter()
const placesStore = usePlacesStore()

const placeId = computed(() => (route.params.id ? Number(route.params.id) : null))
const editing = computed(() => placeId.value !== null)

const title = ref("")
const categoryId = ref<number | null>(null)
const description = ref("")
const address = ref("")
const lat = ref<number | null>(null)
const lon = ref<number | null>(null)
const website = ref("")
const saving = ref(false)
const error = ref("")

onMounted(async () => {
  if (!placeId.value) return
  try {
    const place = await api.place(placeId.value)
    title.value = place.title
    categoryId.value = place.category?.id ?? null
    description.value = place.description
    address.value = place.address
    lat.value = place.lat
    lon.value = place.lon
    website.value = place.website_url ?? ""
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Не удалось открыть место"
  }
})

function onAddress(value: { address: string; lat: number | null; lon: number | null }) {
  address.value = value.address
  lat.value = value.lat
  lon.value = value.lon
}

async function submit() {
  if (!title.value.trim()) {
    error.value = "Впишите название места"
    return
  }
  saving.value = true
  error.value = ""
  const payload = {
    title: title.value.trim(),
    category_id: categoryId.value,
    description: description.value.trim(),
    address: address.value.trim(),
    lat: lat.value,
    lon: lon.value,
    website_url: website.value.trim() || null,
  }
  try {
    const saved = placeId.value
      ? await api.updatePlace(placeId.value, payload)
      : await api.createPlace(payload)
    await placesStore.load()
    router.push({ name: "place", params: { id: saved.id } })
  } catch (exception) {
    error.value = exception instanceof ApiError ? exception.message : "Не удалось сохранить"
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page narrow">
    <h1>{{ editing ? "Правим карточку" : "Новое место" }}</h1>
    <p class="muted lead">
      Обязательно только название, остальное можно дописать позже — карточку видят все.
    </p>

    <form @submit.prevent="submit">
      <p v-if="error" class="error-note">{{ error }}</p>

      <label class="field">
        <span>Название</span>
        <input v-model="title" class="input" type="text" maxlength="160" required />
      </label>

      <CategoryPicker v-model="categoryId" />

      <AddressField :address="address" :lat="lat" :lon="lon" @update="onAddress" />

      <label class="field">
        <span>Что мы про него знаем</span>
        <textarea
          v-model="description"
          class="textarea"
          rows="5"
          placeholder="Чем интересно, что заказать, когда лучше идти"
        />
      </label>

      <label class="field">
        <span>Сайт или страница, если есть</span>
        <input v-model="website" class="input" type="url" placeholder="https://" />
      </label>

      <div class="actions">
        <button class="btn btn--ghost" type="button" @click="router.back()">Назад</button>
        <button class="btn btn--primary" type="submit" :disabled="saving">
          {{ saving ? "Сохраняем…" : editing ? "Сохранить" : "Добавить место" }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.narrow {
  max-width: 560px;
}

h1 {
  font-size: var(--step-3);
  margin-bottom: 0.3rem;
}

.lead {
  font-size: var(--small);
  margin-bottom: 1.5rem;
}

.actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 1.5rem;
}

.actions .btn {
  flex: 1;
}
</style>
