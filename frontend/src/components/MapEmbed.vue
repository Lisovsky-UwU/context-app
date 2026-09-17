<script setup lang="ts">
import { computed } from "vue"

import { gisUrl, widgetUrl, yandexUrl } from "../lib/maps"

const props = defineProps<{ address: string; lat: number | null; lon: number | null }>()

const target = computed(() => ({ address: props.address, lat: props.lat, lon: props.lon }))
const embed = computed(() => widgetUrl(target.value))
</script>

<template>
  <section class="map">
    <div v-if="embed" class="frame">
      <iframe
        :src="embed"
        :title="`Карта: ${address}`"
        loading="lazy"
        allowfullscreen
        referrerpolicy="no-referrer-when-downgrade"
      />
    </div>
    <p v-else class="empty muted">Адрес не указан — добавьте его, и место появится на карте.</p>

    <div v-if="address" class="links">
      <a class="btn btn--ghost" :href="yandexUrl(target)" target="_blank" rel="noreferrer noopener">
        Яндекс.Карты
      </a>
      <a class="btn btn--ghost" :href="gisUrl(target)" target="_blank" rel="noreferrer noopener">
        2ГИС
      </a>
    </div>
  </section>
</template>

<style scoped>
.map {
  display: grid;
  gap: 0.6rem;
}

.frame {
  position: relative;
  aspect-ratio: 16 / 10;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-card);
  overflow: hidden;
  background: var(--paper-deep);
}

.frame iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}

.empty {
  margin: 0;
  padding: 1rem;
  border: 1px dashed var(--edge-strong);
  border-radius: var(--radius-card);
  font-size: var(--small);
}

.links {
  display: flex;
  gap: 0.5rem;
}

.links .btn {
  flex: 1;
  text-decoration: none;
}

@media (min-width: 640px) {
  .frame {
    aspect-ratio: 16 / 7;
  }
}
</style>
