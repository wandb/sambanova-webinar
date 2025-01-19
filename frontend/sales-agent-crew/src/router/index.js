import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../views/MainLayout.vue'
// Import other views as needed

const routes = [
  {
    path: '/',
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
