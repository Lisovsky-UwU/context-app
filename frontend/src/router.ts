import { createRouter, createWebHistory } from "vue-router"

import { useAuthStore } from "./stores/auth"

export const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: (_to, _from, saved) => saved ?? { top: 0 },
  routes: [
    { path: "/", name: "places", component: () => import("./pages/PlacesPage.vue") },
    { path: "/roulette", name: "roulette", component: () => import("./pages/RoulettePage.vue") },
    { path: "/places/new", name: "place-new", component: () => import("./pages/PlaceFormPage.vue") },
    { path: "/places/:id", name: "place", component: () => import("./pages/PlacePage.vue") },
    { path: "/places/:id/edit", name: "place-edit", component: () => import("./pages/PlaceFormPage.vue") },
    { path: "/settings", name: "settings", component: () => import("./pages/SettingsPage.vue") },
    {
      path: "/login",
      name: "login",
      component: () => import("./pages/LoginPage.vue"),
      meta: { guest: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("./pages/RegisterPage.vue"),
      meta: { guest: true },
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) await auth.bootstrap()

  if (!auth.user && !to.meta.guest) {
    return { name: "login", query: to.fullPath === "/" ? undefined : { next: to.fullPath } }
  }
  if (auth.user && to.meta.guest) return { name: "places" }
  return true
})
