<script setup lang="ts">
import { computed } from "vue"

import type { Place } from "../api/types"
import { relativeDay, stampDate } from "../lib/format"

const props = defineProps<{ place: Place }>()

const stamp = computed(() => {
  if (props.place.status === "visited" && props.place.last_visit_date) {
    return { kind: "visited", title: "были", detail: stampDate(props.place.last_visit_date) }
  }
  if (props.place.status === "planned" && props.place.next_visit) {
    return { kind: "planned", title: "идём", detail: relativeDay(props.place.next_visit.scheduled_date) }
  }
  return null
})
</script>

<template>
  <span v-if="stamp" class="stamp" :class="`stamp--${stamp.kind}`">
    <span class="stamp__title">{{ stamp.title }}</span>
    <span class="stamp__detail">{{ stamp.detail }}</span>
  </span>
</template>

<style scoped>
.stamp {
  display: inline-grid;
  justify-items: center;
  gap: 0.05rem;
  padding: 0.3rem 0.6rem;
  border: 2px solid currentColor;
  border-radius: 5px;
  font-family: var(--font-display);
  font-weight: 600;
  line-height: 1.1;
  transform: rotate(-3deg);
  white-space: nowrap;
}

.stamp--visited {
  color: var(--mint);
  background: var(--mint-soft);
}

.stamp--planned {
  color: var(--amber);
  background: var(--amber-soft);
  transform: rotate(2deg);
}

.stamp__title {
  font-size: var(--tiny);
  letter-spacing: 0.08em;
}

.stamp__detail {
  font-size: 0.7rem;
  font-weight: 500;
  opacity: 0.85;
}
</style>
