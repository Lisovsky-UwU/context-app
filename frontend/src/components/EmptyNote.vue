<script setup lang="ts">
defineProps<{ title: string; hint?: string }>()
</script>

<template>
  <div class="note">
    <p class="title">{{ title }}</p>
    <p v-if="hint" class="muted hint">{{ hint }}</p>
    <slot />
  </div>
</template>

<style scoped>
.note {
  display: grid;
  justify-items: start;
  gap: 0.35rem;
  padding: 1.5rem;
  border: 1px dashed var(--edge-strong);
  border-radius: var(--radius-card);
}

.title {
  margin: 0;
  font-family: var(--font-display);
  font-size: var(--step-1);
}

.hint {
  margin: 0;
  font-size: var(--small);
}
</style>
