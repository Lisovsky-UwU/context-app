import { defineStore } from "pinia"
import { computed, ref } from "vue"

import { api } from "../api/client"
import type { Category, CategoryInput } from "../api/types"

export const useCategoriesStore = defineStore("categories", () => {
  const items = ref<Category[]>([])
  const loaded = ref(false)

  const byId = computed(
    () => new Map(items.value.map((category) => [category.id, category] as const)),
  )

  async function load(force = false) {
    if (loaded.value && !force) return
    items.value = await api.categories()
    loaded.value = true
  }

  async function create(data: CategoryInput): Promise<Category> {
    const category = await api.createCategory(data)
    items.value = [...items.value, category]
    return category
  }

  async function update(id: number, data: Partial<CategoryInput>) {
    const category = await api.updateCategory(id, data)
    items.value = items.value.map((item) => (item.id === id ? category : item))
    return category
  }

  async function remove(id: number, moveTo?: number | null) {
    await api.deleteCategory(id, moveTo)
    items.value = items.value.filter((item) => item.id !== id)
  }

  return { items, loaded, byId, load, create, update, remove }
})
