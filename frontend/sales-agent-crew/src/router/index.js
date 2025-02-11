import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../views/MainLayout.vue'

const routes = [
  {
    path: '/:id?',
    name: 'home',
    component: MainLayout,
  },
  // Add other routes here
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
