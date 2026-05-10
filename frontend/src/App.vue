<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const isMobileMenuOpen = ref(false)
const route = useRoute()
const auth = useAuthStore()

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
  <div class="flex flex-col lg:flex-row h-screen overflow-hidden" style="background-color: var(--bg-base)">

    <!-- Mobile Header -->
    <div v-if="auth.isAuthenticated" class="lg:hidden flex items-center justify-between p-4 sticky top-0 z-30 backdrop-blur-xl" style="background: rgba(6,4,15,0.9); border-bottom: 1px solid rgba(255,184,0,0.1);">
      <div class="flex items-center gap-3">
        <img src="@/assets/Logo_white.svg" alt="JARL Logo" class="w-8 h-8 object-contain" style="filter: drop-shadow(0 0 6px rgba(255,184,0,0.7))" />
        <span style="font-family: 'Press Start 2P', monospace; font-size: 0.85rem; color: var(--neon-cyan); text-shadow: 0 0 10px rgba(255,184,0,0.6)">JARL</span>
      </div>
      <button @click="toggleMobileMenu" class="p-2 transition-colors" style="color: var(--text-muted)">
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
      <div v-if="isMobileMenuOpen" class="fixed inset-0 z-20 lg:hidden flex flex-col pt-20" style="background: rgba(6,4,15,0.97)">
        <!-- scanline overlay -->
        <div class="absolute inset-0 pointer-events-none" style="background: repeating-linear-gradient(0deg, rgba(255,184,0,0.015) 0 1px, transparent 1px 4px)"></div>
        <nav class="relative flex-1 px-8 space-y-8 flex flex-col justify-center text-center">
          <RouterLink to="/" class="mobile-nav-link">Games</RouterLink>
          <RouterLink to="/platforms" class="mobile-nav-link">Platforms</RouterLink>
          <RouterLink to="/scan" class="mobile-nav-link">Jobs</RouterLink>
          <RouterLink to="/settings" class="mobile-nav-link">Settings</RouterLink>
          <button @click="handleLogout" class="mobile-nav-link" style="color: var(--neon-pink); text-shadow: 0 0 10px rgba(255,53,32,0.5)">Logout</button>
        </nav>
      </div>
    </transition>

    <!-- Sidebar (Desktop) -->
    <aside v-if="auth.isAuthenticated" class="hidden lg:flex w-72 glass-panel flex-col z-20">

      <!-- Logo -->
      <div class="p-6 flex items-center gap-4" style="border-bottom: 1px solid rgba(255,184,0,0.1);">
        <div class="relative">
          <img src="@/assets/Logo_white.svg" alt="JARL Logo" class="w-10 h-10 object-contain relative z-10"
               style="filter: drop-shadow(0 0 8px rgba(255,184,0,0.7))" />
          <div class="absolute inset-0 rounded-full animate-neon-pulse" style="background: radial-gradient(circle, rgba(255,184,0,0.15), transparent 70%)"></div>
        </div>
        <div>
          <div class="logo-glyph" style="font-family: 'Press Start 2P', monospace; font-size: 1.1rem; color: var(--neon-cyan); text-shadow: 0 0 12px rgba(255,184,0,0.65), 0 0 30px rgba(255,184,0,0.2); letter-spacing: 0.05em; cursor: default;"
               @mouseenter="($event.target as HTMLElement).classList.add('glitch-run')"
               @animationend="($event.target as HTMLElement).classList.remove('glitch-run')">
            JARL
          </div>
          <p style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; letter-spacing: 0.16em; color: var(--text-muted); text-transform: uppercase; margin-top: 4px;">ROM ARCHIVE</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 mt-5 flex flex-col gap-1">
        <RouterLink to="/" class="nav-link" active-class="active">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          Games
        </RouterLink>
        <RouterLink to="/platforms" class="nav-link" active-class="active">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Platforms
        </RouterLink>
        <RouterLink to="/scan" class="nav-link" active-class="active">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          Jobs
        </RouterLink>

        <div class="my-3 mx-2" style="height:1px; background: linear-gradient(90deg, transparent, rgba(255,184,0,0.15), transparent)"></div>

        <RouterLink to="/scraper-test" class="nav-link" active-class="active">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Checks
        </RouterLink>

        <RouterLink to="/settings" class="nav-link" active-class="active">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Settings
        </RouterLink>


        <div class="flex-1"></div>

        <button @click="handleLogout" class="nav-link w-full text-left mb-2" style="color: rgba(255,53,32,0.55);"
                onmouseenter="this.style.color='var(--neon-pink)';this.style.textShadow='0 0 8px rgba(255,53,32,0.5)';"
                onmouseleave="this.style.color='rgba(255,53,32,0.55)';this.style.textShadow='none';">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Logout
        </button>
      </nav>

      <!-- Status Footer -->
      <div class="p-4" style="border-top: 1px solid rgba(255,184,0,0.08);">
        <div class="rounded-md p-3" style="background: rgba(0,0,0,0.35); border: 1px solid rgba(255,184,0,0.08);">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full animate-pulse" style="background: var(--neon-green); box-shadow: 0 0 6px var(--neon-green)"></div>
            <span style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.12em; color: var(--neon-green); text-shadow: 0 0 6px rgba(0,255,136,0.5); text-transform: uppercase;">Online</span>
          </div>
          <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em;">Backend Connected</p>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 relative overflow-y-auto overflow-x-hidden custom-scrollbar">
      <!-- Grid overlay -->
      <div class="absolute inset-0 pointer-events-none opacity-[0.03]"
           style="background-image: linear-gradient(0deg,transparent 24px,rgba(255,184,0,1) 25px),linear-gradient(90deg,transparent 24px,rgba(255,184,0,1) 25px); background-size: 25px 25px;"></div>
      <!-- Circuit trace -->
      <div class="circuit-trace pointer-events-none absolute inset-x-0 top-0 h-40 opacity-40"></div>
      <div class="relative z-10 p-4 lg:p-8 max-w-7xl mx-auto" :class="auth.isAuthenticated ? 'mb-16 lg:mb-0' : ''">
        <RouterView v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <Suspense>
              <template #default>
                <component :is="Component" />
              </template>
              <template #fallback>
                <div class="flex flex-col items-center justify-center py-32 gap-5">
                  <div class="chip-loader"></div>
                  <p style="font-family:'Orbitron',sans-serif;font-size:0.6rem;font-weight:700;letter-spacing:0.2em;color:var(--text-muted);text-transform:uppercase;">Loading</p>
                </div>
              </template>
            </Suspense>
          </transition>
        </RouterView>
      </div>
    </main>

    <!-- Mobile Tab Bar -->
    <div v-if="auth.isAuthenticated" class="lg:hidden fixed bottom-0 left-0 right-0 h-16 flex items-center justify-around px-4 z-30 backdrop-blur-2xl"
         style="background: rgba(6,4,15,0.92); border-top: 1px solid rgba(255,184,0,0.1);">
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
/* ── Page Transitions ── */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(16px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}

.fade-enter-active,
.fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from,
.fade-leave-to     { opacity: 0; }

/* ── Mobile Nav ── */
.mobile-nav-link {
  font-family: 'Press Start 2P', monospace;
  font-size: 1.1rem;
  color: var(--text-muted);
  transition: all 0.2s;
  display: block;
  line-height: 2;
}
.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  color: var(--neon-cyan);
  text-shadow: 0 0 14px rgba(0, 245, 255, 0.7);
}

.mobile-tab {
  padding: 0.75rem;
  color: var(--text-muted);
  transition: all 0.2s;
  border-radius: 0.75rem;
}
.mobile-tab.active {
  color: var(--neon-cyan);
  background: rgba(0, 245, 255, 0.08);
  filter: drop-shadow(0 0 4px rgba(0, 245, 255, 0.5));
}

/* ── Circuit Trace ── */
.circuit-trace {
  background:
    linear-gradient(90deg, transparent 0%, rgba(255,184,0,0.22) 20%, transparent 45%),
    linear-gradient(180deg, rgba(255,96,0,0.08), transparent);
  -webkit-mask-image: repeating-linear-gradient(90deg, transparent 0 26px, #000 26px 28px, transparent 28px 54px);
  mask-image: repeating-linear-gradient(90deg, transparent 0 26px, #000 26px 28px, transparent 28px 54px);
  animation: trace-drift 8s ease-in-out infinite;
}
@keyframes trace-drift {
  0%, 100% { transform: translateX(-4%); opacity: 0.2; }
  50%       { transform: translateX(4%);  opacity: 0.65; }
}

/* ── Custom Scrollbar ── */
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 245, 255, 0.12);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 245, 255, 0.28);
}

/* ── Glitch Animation for Logo ── */
.glitch-run {
  animation: glitch 0.4s ease-in-out;
}
</style>
