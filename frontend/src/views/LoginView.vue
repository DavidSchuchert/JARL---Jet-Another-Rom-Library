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
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-md space-y-8">
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-24 h-24 mb-6">
          <img src="@/assets/Logo_white.svg" alt="JARL Logo" class="w-full h-full object-contain" />
        </div>
        <h1 class="text-4xl font-black text-white tracking-tighter italic">JARL</h1>
        <p class="mt-2 text-stone-500 font-bold uppercase tracking-widest text-xs">Secure Access Protocol</p>
      </div>

      <div class="glass-card p-8 space-y-6">
        <div v-if="error" class="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-bold flex items-center gap-3 animate-shake">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div class="space-y-2">
            <label class="text-[10px] text-stone-500 uppercase font-black tracking-widest ml-1">Username</label>
            <input 
              v-model="username"
              type="text" 
              class="input-nebula w-full"
              placeholder="Identification"
              required
            />
          </div>

          <div class="space-y-2">
            <label class="text-[10px] text-stone-500 uppercase font-black tracking-widest ml-1">Password</label>
            <input 
              v-model="password"
              type="password" 
              class="input-nebula w-full"
              placeholder="Encryption Key"
              required
            />
          </div>

          <button 
            type="submit"
            :disabled="auth.loading"
            class="w-full btn-nebula-primary !py-4 text-lg mt-4 group"
          >
            <span v-if="!auth.loading" class="flex items-center justify-center gap-3">
              Authorize
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </span>
            <span v-else class="flex items-center justify-center gap-3">
              <div class="w-5 h-5 border-2 border-stone-900/20 border-t-stone-900 rounded-full animate-spin"></div>
              Verifying...
            </span>
          </button>
        </form>
      </div>

      <p class="text-center text-[10px] text-stone-600 uppercase font-bold tracking-[0.2em]">
        JetAnotherRomLibrary v1.0.0
      </p>
    </div>
  </div>
</template>

<style scoped>
.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>
