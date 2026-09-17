<script setup lang="ts">
import { computed } from "vue"
import { RouterView, useRoute } from "vue-router"

import AppNav from "./components/AppNav.vue"
import { useAuthStore } from "./stores/auth"
import { useThemeStore } from "./stores/theme"

const auth = useAuthStore()
const route = useRoute()
useThemeStore()

const showNav = computed(() => Boolean(auth.user) && !route.meta.guest)
</script>

<template>
  <AppNav v-if="showNav" />
  <main>
    <RouterView v-slot="{ Component }">
      <component :is="Component" />
    </RouterView>
  </main>
</template>
