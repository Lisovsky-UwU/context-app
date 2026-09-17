<script setup lang="ts">
import L from "leaflet"
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { RouterLink } from "vue-router"

import type { Place, PlaceStatus } from "../api/types"
import { relativeDay, stampDate } from "../lib/format"
import { accentVar, categoryLabel } from "../lib/labels"
import { useAuthStore } from "../stores/auth"
import { usePlacesStore } from "../stores/places"
import { useThemeStore } from "../stores/theme"

import "leaflet/dist/leaflet.css"

const places = usePlacesStore()
const auth = useAuthStore()
const theme = useThemeStore()

const container = ref<HTMLElement | null>(null)
const filter = ref<PlaceStatus | "all">("all")
const selected = ref<Place | null>(null)

let map: L.Map | null = null
let tiles: L.TileLayer | null = null
let layer: L.LayerGroup | null = null

const TABS: { value: PlaceStatus | "all"; label: string }[] = [
  { value: "all", label: "Все" },
  { value: "wish", label: "Хотим" },
  { value: "planned", label: "Идём" },
  { value: "visited", label: "Были" },
]

const onMap = computed(() =>
  places.items.filter(
    (place) =>
      typeof place.lat === "number" &&
      typeof place.lon === "number" &&
      (filter.value === "all" || place.status === filter.value),
  ),
)
const withoutAddress = computed(
  () => places.items.filter((place) => typeof place.lat !== "number").length,
)

function tileUrl(): string {
  const style = theme.theme === "dark" ? "dark_all" : "light_all"
  return `https://{s}.basemaps.cartocdn.com/${style}/{z}/{x}/{y}{r}.png`
}

/** Метка: точка в цвете категории, ободок — состояние места. */
function markerIcon(place: Place): L.DivIcon {
  const ring =
    place.status === "visited" ? "var(--mint)" : place.status === "planned" ? "var(--amber)" : "transparent"
  return L.divIcon({
    className: "pin",
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    html: `<span class="pin__dot" style="background:${accentVar(place.category?.color)};box-shadow:0 0 0 3px ${ring}"></span>`,
  })
}

function draw() {
  if (!map || !layer) return
  layer.clearLayers()

  onMap.value.forEach((place) => {
    const marker = L.marker([place.lat as number, place.lon as number], {
      icon: markerIcon(place),
      title: place.title,
      keyboard: true,
      alt: place.title,
    })
    marker.on("click", () => {
      selected.value = place
    })
    layer?.addLayer(marker)
  })

  if (onMap.value.length) {
    const bounds = L.latLngBounds(
      onMap.value.map((place) => [place.lat as number, place.lon as number] as [number, number]),
    )
    map.fitBounds(bounds, { padding: [48, 48], maxZoom: 15 })
  }
}

onMounted(async () => {
  await places.load()

  const center = auth.config?.default_center ?? [55.751244, 37.618423]
  map = L.map(container.value as HTMLElement, {
    center: center as [number, number],
    zoom: 11,
    zoomControl: true,
    attributionControl: true,
  })
  tiles = L.tileLayer(tileUrl(), {
    maxZoom: 19,
    attribution: '© OpenStreetMap, © CARTO',
  }).addTo(map)
  layer = L.layerGroup().addTo(map)
  draw()
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

watch(filter, () => {
  selected.value = null
  draw()
})

watch(
  () => theme.theme,
  () => {
    tiles?.setUrl(tileUrl())
  },
)
</script>

<template>
  <div class="map-page">
    <div class="strip">
      <button
        v-for="tab in TABS"
        :key="tab.value"
        type="button"
        class="tab"
        :class="{ 'tab--on': filter === tab.value }"
        @click="filter = tab.value"
      >
        {{ tab.label }}
      </button>
      <span v-if="withoutAddress" class="muted missing">
        {{ withoutAddress }} без адреса
      </span>
    </div>

    <div ref="container" class="canvas" />

    <p v-if="!onMap.length" class="empty muted">
      Здесь пока пусто. Адрес места подставляет точку на карту — впишите его в карточке.
    </p>

    <aside v-if="selected" class="sheet">
      <button class="sheet__close" type="button" @click="selected = null">
        <span aria-hidden="true">×</span>
        <span class="visually-hidden">Закрыть</span>
      </button>

      <p class="sheet__kind" :style="{ color: accentVar(selected.category?.color) }">
        {{ categoryLabel(selected.category) }}
      </p>
      <h2>{{ selected.title }}</h2>
      <p v-if="selected.address" class="muted sheet__address">{{ selected.address }}</p>

      <p v-if="selected.status === 'planned' && selected.next_visit" class="sheet__state planned">
        Идём {{ relativeDay(selected.next_visit.scheduled_date) }}
      </p>
      <p v-else-if="selected.status === 'visited' && selected.last_visit_date" class="sheet__state visited">
        Были {{ stampDate(selected.last_visit_date) }}
      </p>
      <p v-else-if="selected.interested_by.length" class="sheet__state muted">
        Хотят: {{ selected.interested_by.map((person) => person.display_name).join(", ") }}
      </p>

      <RouterLink class="btn btn--primary" :to="{ name: 'place', params: { id: selected.id } }">
        Открыть карточку
      </RouterLink>
    </aside>
  </div>
</template>

<style scoped>
.map-page {
  position: relative;
  display: flex;
  flex-direction: column;
  height: calc(100dvh - var(--bar-height));
}

.strip {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem var(--page-gutter);
  border-bottom: 1px solid var(--edge);
}

.tab {
  padding: 0.4rem 0.8rem;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  font-family: var(--font-display);
  font-size: var(--small);
  font-weight: 500;
  color: var(--ink-soft);
  cursor: pointer;
}

.tab--on {
  background: var(--paper-deep);
  color: var(--ink);
}

.missing {
  margin-left: auto;
  font-size: var(--tiny);
}

.canvas {
  flex: 1;
  min-height: 0;
  background: var(--paper-deep);
}

.empty {
  position: absolute;
  left: 50%;
  top: 55%;
  z-index: 500;
  width: min(320px, calc(100% - 2rem));
  transform: translate(-50%, -50%);
  padding: 1rem;
  border: 1px dashed var(--edge-strong);
  border-radius: var(--radius-card);
  background: var(--card);
  font-size: var(--small);
  text-align: center;
}

.sheet {
  position: absolute;
  left: 50%;
  bottom: 1rem;
  z-index: 600;
  width: min(420px, calc(100% - 2rem));
  transform: translateX(-50%);
  padding: 1rem 1.1rem 1.1rem;
  background: var(--card);
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-lift);
}

.sheet__close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  font-size: 1.3rem;
  line-height: 1;
  color: var(--ink-soft);
  cursor: pointer;
}

.sheet__kind {
  margin: 0 0 0.15rem;
  font-size: var(--tiny);
  font-weight: 600;
}

.sheet h2 {
  font-size: var(--step-2);
  margin-bottom: 0.2rem;
}

.sheet__address {
  margin: 0 0 0.5rem;
  font-size: var(--small);
}

.sheet__state {
  margin: 0 0 0.75rem;
  font-size: var(--small);
}

.sheet__state.planned {
  color: var(--amber);
  font-weight: 600;
}

.sheet__state.visited {
  color: var(--mint);
  font-weight: 600;
}

.sheet .btn {
  text-decoration: none;
}

:deep(.pin__dot) {
  display: block;
  width: 14px;
  height: 14px;
  margin: 4px;
  border-radius: 50%;
  border: 2px solid var(--card);
}

:deep(.leaflet-container) {
  font-family: var(--font-text);
  background: var(--paper-deep);
}

:deep(.leaflet-control-attribution) {
  background: color-mix(in srgb, var(--card) 85%, transparent);
  color: var(--ink-faint);
  font-size: 10px;
}

:deep(.leaflet-control-attribution a) {
  color: var(--ink-soft);
}

:deep(.leaflet-bar a) {
  background: var(--card);
  color: var(--ink);
  border-bottom-color: var(--edge);
}

:deep(.leaflet-bar a:hover) {
  background: var(--paper-deep);
}
</style>
