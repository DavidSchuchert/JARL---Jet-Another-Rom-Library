import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/roms/:id',
      name: 'rom-detail',
      component: () => import('@/views/RomDetailView.vue')
    },
    {
      path: '/platforms',
      name: 'platforms',
      component: () => import('@/views/PlatformsView.vue')
    },
    {
      path: '/scan',
      name: 'scan',
      component: () => import('@/views/ScanView.vue')
    },
    {
      path: '/scraper-test',
      name: 'scraper-test',
      component: () => import('@/views/ScraperTestView.vue')
    }
  ]
})

export default router
