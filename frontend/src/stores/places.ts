import { defineStore } from "pinia"
import { computed, ref } from "vue"

import { api } from "../api/client"
import type { Place, PlaceStatus, Visit } from "../api/types"

export const usePlacesStore = defineStore("places", () => {
  const items = ref<Place[]>([])
  const upcoming = ref<Visit[]>([])
  const loading = ref(false)
  const query = ref("")
  const category = ref<number>(0)

  const counts = computed(() => ({
    wish: items.value.filter((place) => place.status === "wish").length,
    planned: items.value.filter((place) => place.status === "planned").length,
    visited: items.value.filter((place) => place.status === "visited").length,
  }))

  function byStatus(status: PlaceStatus) {
    return items.value.filter((place) => place.status === status)
  }

  async function load() {
    loading.value = true
    try {
      items.value = await api.places({
        q: query.value.trim() || undefined,
        category_id: category.value || undefined,
      })
    } finally {
      loading.value = false
    }
  }

  async function loadUpcoming() {
    upcoming.value = await api.visits({ upcoming: true })
  }

  function patch(place: Place) {
    const index = items.value.findIndex((item) => item.id === place.id)
    if (index >= 0) items.value[index] = { ...items.value[index], ...place }
  }

  return { items, upcoming, loading, query, category, counts, byStatus, load, loadUpcoming, patch }
})
