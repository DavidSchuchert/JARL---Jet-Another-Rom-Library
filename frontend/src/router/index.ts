import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true }
    },
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
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue')
    }
  ]
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()
  
  if (!to.meta.public && !auth.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && auth.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
