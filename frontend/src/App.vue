<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const isMobileMenuOpen = ref(false)
const route = useRoute()
const auth = useAuthStore()

// Close mobile menu on route change
watch(() => route.path, () => {
  isMobileMenuOpen.value = false
})

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const handleLogout = () => {
  auth.logout()
}

onMounted(() => {
  auth.checkAuth()
})
</script>

<template>
  <div class="flex flex-col lg:flex-row h-screen bg-[#11110f] overflow-hidden">
    
    <!-- Mobile Header -->
    <div v-if="auth.isAuthenticated" class="lg:hidden flex items-center justify-between p-4 border-b border-stone-800 bg-[#11110f]/80 backdrop-blur-xl sticky top-0 z-30">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 flex items-center justify-center">
          <img src="@/assets/Logo_white.svg" alt="JARL Logo" class="w-9 h-9 object-contain" />
        </div>
        <h1 class="text-xl font-black tracking-normal text-stone-50">JARL</h1>
      </div>
      <button @click="toggleMobileMenu" class="p-2 text-stone-400 hover:text-stone-50 transition-colors">
        <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
        </svg>
        <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Mobile Full Menu Overlay -->
    <transition name="fade">
      <div v-if="isMobileMenuOpen" class="fixed inset-0 z-20 bg-[#11110f]/95 lg:hidden flex flex-col pt-20">
        <nav class="flex-1 px-8 space-y-6 flex flex-col justify-center text-center">
          <RouterLink to="/" class="mobile-nav-link">Games</RouterLink>
          <RouterLink to="/platforms" class="mobile-nav-link">Platforms</RouterLink>
          <RouterLink to="/scan" class="mobile-nav-link">Jobs</RouterLink>
          <button @click="handleLogout" class="mobile-nav-link text-red-500">Logout</button>
        </nav>
      </div>
    </transition>

    <!-- Sidebar (Desktop) -->
    <aside v-if="auth.isAuthenticated" class="hidden lg:flex w-72 glass-panel flex-col z-20 border-r border-stone-800">
      <!-- Logo Section -->
      <div class="p-6 flex items-center gap-4 border-b border-stone-700/70">
        <div class="w-10 h-10 flex items-center justify-center">
          <img src="@/assets/Logo_white.svg" alt="JARL Logo" class="w-10 h-10 object-contain" />
        </div>
        <div>
          <h1 class="text-2xl font-black tracking-normal text-stone-50">JARL</h1>
          <p class="text-[10px] uppercase tracking-widest text-stone-500 font-bold">ROM archive</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-4 space-y-2 mt-4 flex flex-col">
        <RouterLink to="/" class="nav-link" active-class="active">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          Games
        </RouterLink>
        <RouterLink to="/platforms" class="nav-link" active-class="active">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Platforms
        </RouterLink>
        <RouterLink to="/scan" class="nav-link" active-class="active">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          Jobs
        </RouterLink>
        <div class="pt-8 px-4">
          <div class="h-px bg-white/5"></div>
        </div>
        <RouterLink to="/scraper-test" class="nav-link" active-class="active">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Checks
        </RouterLink>
        
        <button @click="handleLogout" class="nav-link w-full text-left text-red-400/70 hover:text-red-400 hover:bg-red-400/5 mt-auto mb-4">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Logout
        </button>
      </nav>

      <!-- Footer Info -->
      <div class="p-6">
        <div class="glass-card p-4">
          <p class="text-[10px] text-stone-500 uppercase tracking-widest mb-1">Backend</p>
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
            <span class="text-xs font-bold text-stone-300">Connected</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 relative overflow-y-auto overflow-x-hidden custom-scrollbar">
      <div class="absolute inset-0 pointer-events-none opacity-[0.045] bg-[linear-gradient(0deg,transparent_24px,#fff_25px),linear-gradient(90deg,transparent_24px,#fff_25px)] bg-[length:25px_25px]"></div>
      <div class="circuit-trace pointer-events-none absolute inset-x-0 top-0 h-40 opacity-50"></div>
      <div class="relative z-10 p-4 lg:p-8 max-w-7xl mx-auto" :class="auth.isAuthenticated ? 'mb-16 lg:mb-0' : ''">
        <RouterView v-slot="{ Component }">
          <transition 
            name="fade-slide" 
            mode="out-in"
          >
            <component :is="Component" />
          </transition>
        </RouterView>
      </div>
    </main>

    <!-- Mobile Tab Bar -->
    <div v-if="auth.isAuthenticated" class="lg:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#11110f]/90 backdrop-blur-2xl border-t border-stone-800/50 flex items-center justify-around px-4 z-30">
      <RouterLink to="/" class="mobile-tab" active-class="active">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      </RouterLink>
      <RouterLink to="/platforms" class="mobile-tab" active-class="active">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </RouterLink>
      <RouterLink to="/scan" class="mobile-tab" active-class="active">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
      </RouterLink>
    </div>
  </div>
</template>

<style>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.mobile-nav-link {
  @apply text-4xl font-black text-stone-500 hover:text-amber-400 transition-all italic tracking-tighter;
}

.mobile-nav-link.router-link-active {
  @apply text-stone-50 scale-110;
}

.mobile-tab {
  @apply p-3 text-stone-500 transition-all rounded-xl;
}

.mobile-tab.active {
  @apply text-amber-400 bg-amber-400/10;
}

.circuit-trace {
  background:
    linear-gradient(90deg, transparent 0%, rgba(226,184,87,0.35) 18%, transparent 40%),
    linear-gradient(180deg, rgba(111,179,143,0.18), transparent);
  -webkit-mask-image: repeating-linear-gradient(90deg, transparent 0 28px, #000 28px 30px, transparent 30px 58px);
  mask-image: repeating-linear-gradient(90deg, transparent 0 28px, #000 28px 30px, transparent 30px 58px);
  animation: trace-drift 8s ease-in-out infinite;
}

@keyframes trace-drift {
  0%, 100% {
    transform: translateX(-4%);
    opacity: 0.25;
  }
  50% {
    transform: translateX(4%);
    opacity: 0.7;
  }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
