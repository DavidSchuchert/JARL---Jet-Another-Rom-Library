<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="flex h-screen bg-[#11110f] overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-72 glass-panel flex flex-col z-20">
      <!-- Logo Section -->
      <div class="p-6 flex items-center gap-4 border-b border-stone-700/70">
        <div class="w-10 h-10 rounded-md bg-amber-400 text-stone-950 flex items-center justify-center shadow-[inset_0_-3px_0_rgba(0,0,0,0.22)]">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 7h12v10H6z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 10h2m-1-1v2m5-1h.01M17 12h.01" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-black tracking-normal text-stone-50">JARL</h1>
          <p class="text-[10px] uppercase tracking-widest text-stone-500 font-bold">ROM archive</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-4 space-y-2 mt-4">
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
      <div class="absolute inset-0 pointer-events-none opacity-[0.035] bg-[linear-gradient(0deg,transparent_24px,#fff_25px),linear-gradient(90deg,transparent_24px,#fff_25px)] bg-[length:25px_25px]"></div>
      <div class="relative z-10 p-6 lg:p-8 max-w-7xl mx-auto">
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
