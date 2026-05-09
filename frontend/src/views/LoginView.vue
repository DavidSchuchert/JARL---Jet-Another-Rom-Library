<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Please enter both username and password'
    return
  }
  try {
    await auth.login(username.value, password.value)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Authentication failed'
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
    <!-- Scanlines -->
    <div class="absolute inset-0 pointer-events-none" style="background: repeating-linear-gradient(0deg, rgba(255,184,0,0.018) 0 1px, transparent 1px 4px)"></div>

    <!-- Radial glow bg -->
    <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(ellipse 60% 50% at 50% 50%, rgba(255,184,0,0.05), transparent 70%)"></div>

    <!-- Corner decorations -->
    <div class="absolute top-8 left-8 w-12 h-12 pointer-events-none" style="border-top: 2px solid rgba(255,184,0,0.3); border-left: 2px solid rgba(255,184,0,0.3)"></div>
    <div class="absolute top-8 right-8 w-12 h-12 pointer-events-none" style="border-top: 2px solid rgba(255,184,0,0.3); border-right: 2px solid rgba(255,184,0,0.3)"></div>
    <div class="absolute bottom-8 left-8 w-12 h-12 pointer-events-none" style="border-bottom: 2px solid rgba(255,184,0,0.3); border-left: 2px solid rgba(255,184,0,0.3)"></div>
    <div class="absolute bottom-8 right-8 w-12 h-12 pointer-events-none" style="border-bottom: 2px solid rgba(255,184,0,0.3); border-right: 2px solid rgba(255,184,0,0.3)"></div>

    <div class="w-full max-w-sm space-y-8 relative z-10">
      <!-- Logo / Header -->
      <div class="text-center space-y-4">
        <div class="inline-flex items-center justify-center w-20 h-20 relative">
          <div class="absolute inset-0 rounded-full animate-pulse" style="background: radial-gradient(circle, rgba(255,184,0,0.2), transparent 65%)"></div>
          <img src="@/assets/Logo_white.svg" alt="JARL Logo" class="w-14 h-14 object-contain relative z-10"
               style="filter: drop-shadow(0 0 14px rgba(255,184,0,0.85))" />
        </div>

        <div>
          <h1 style="font-family: 'Press Start 2P', monospace; font-size: 1.6rem; color: var(--neon-cyan); text-shadow: 0 0 20px rgba(255,184,0,0.7), 0 0 50px rgba(255,184,0,0.25); letter-spacing: 0.06em;">
            JARL
          </h1>
          <div class="mt-3 flex items-center justify-center gap-2">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; letter-spacing: 0.18em; color: var(--text-muted); text-transform: uppercase;">
              Player 1 — Insert Credentials
            </span>
            <span class="animate-blink" style="color: var(--neon-cyan); font-size: 0.9rem; line-height: 1">_</span>
          </div>
        </div>
      </div>

      <!-- Card -->
      <div class="rounded-lg p-8 space-y-6" style="background: rgba(12,10,28,0.95); border: 1px solid rgba(255,184,0,0.18); box-shadow: 0 0 50px rgba(255,184,0,0.07), 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,184,0,0.07);">

        <!-- Error -->
        <div v-if="error" class="rounded-md p-4 flex items-center gap-3 login-error" style="background: rgba(255,53,32,0.08); border: 1px solid rgba(255,53,32,0.25); color: var(--neon-pink);">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem;">{{ error }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div class="space-y-2">
            <label style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; display: block;">
              &gt; Username
            </label>
            <input
              v-model="username"
              type="text"
              class="input-nebula w-full h-11"
              placeholder="player_one"
              required
              autocomplete="username"
            />
          </div>

          <div class="space-y-2">
            <label style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; display: block;">
              &gt; Password
            </label>
            <input
              v-model="password"
              type="password"
              class="input-nebula w-full h-11"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
          </div>

          <button
            type="submit"
            :disabled="auth.loading"
            class="btn-nebula-primary w-full !py-3.5 mt-2"
            style="font-size: 0.72rem;"
          >
            <span v-if="!auth.loading" class="flex items-center justify-center gap-3">
              START GAME
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </span>
            <span v-else class="flex items-center justify-center gap-3">
              <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin opacity-60"></div>
              LOADING...
            </span>
          </button>
        </form>
      </div>

      <p class="text-center" style="font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: var(--text-muted); letter-spacing: 0.08em;">
        © JARL v1.0 — JetAnotherRomLibrary
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-error {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>
