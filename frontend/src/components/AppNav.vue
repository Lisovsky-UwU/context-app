<script setup lang="ts">
import { computed } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"

import { useAuthStore } from "../stores/auth"

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const initials = computed(() => auth.user?.display_name.slice(0, 1).toUpperCase() ?? "")

const links = [
  { name: "places", label: "Места" },
  { name: "map", label: "Карта" },
  { name: "roulette", label: "Рулетка" },
  { name: "settings", label: "Профиль" },
]

function isActive(name: string) {
  if (name === "places") return route.name === "places" || String(route.name).startsWith("place")
  return route.name === name
}

function goAdd() {
  router.push({ name: "place-new" })
}
</script>

<template>
  <header class="bar">
    <div class="bar__inner">
      <RouterLink :to="{ name: 'places' }" class="wordmark">
        Контекст<span aria-hidden="true">.</span>
      </RouterLink>

      <nav class="links" aria-label="Разделы">
        <RouterLink
          v-for="link in links"
          :key="link.name"
          :to="{ name: link.name }"
          class="link"
          :class="{ 'link--on': isActive(link.name) }"
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="tools">
        <button class="add" type="button" title="Добавить место" @click="goAdd">
          <span aria-hidden="true">+</span>
          <span class="add__word">Место</span>
          <span class="visually-hidden">Добавить место</span>
        </button>
        <RouterLink :to="{ name: 'settings' }" class="avatar" :title="auth.user?.display_name">
          {{ initials }}
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.bar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: color-mix(in srgb, var(--paper) 88%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--edge);
}

.bar__inner {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: 0.7rem var(--page-gutter);
}

.wordmark {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.03em;
  text-decoration: none;
}

.wordmark span {
  color: var(--pomegranate);
}

.links {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.link {
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-pill);
  font-size: var(--small);
  font-weight: 500;
  color: var(--ink-soft);
  text-decoration: none;
}

.link--on {
  background: var(--paper-deep);
  color: var(--ink);
}

.tools {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  height: 38px;
  padding: 0 0.85rem;
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--pomegranate);
  color: #fff;
  font-weight: 600;
  font-size: var(--small);
  cursor: pointer;
}

:root[data-theme="dark"] .add {
  color: #24101a;
}

.avatar {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-pill);
  background: var(--paper-deep);
  border: 1px solid var(--edge-strong);
  font-family: var(--font-display);
  font-size: var(--small);
  text-decoration: none;
}

@media (max-width: 640px) {
  .bar {
    position: fixed;
    inset: auto 0 0 0;
    top: auto;
    border-top: 1px solid var(--edge);
    border-bottom: 0;
    padding-bottom: env(safe-area-inset-bottom);
  }

  .bar__inner {
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
  }

  .wordmark,
  .avatar {
    display: none;
  }

  .links {
    margin: 0;
    flex: 1;
    gap: 0;
    justify-content: space-around;
  }

  .link {
    padding: 0.5rem 0.6rem;
  }

  .add {
    width: 38px;
    padding: 0;
    flex: none;
    justify-content: center;
    font-size: 1.15rem;
  }

  .add__word {
    display: none;
  }
}
</style>
