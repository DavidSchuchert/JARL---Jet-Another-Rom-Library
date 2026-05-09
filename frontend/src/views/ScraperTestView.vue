<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'

interface TestResult {
  status: 'success' | 'failed' | 'error'
  message: string
  http_code?: number
  user?: string
  client_id?: string
  details?: any
}

const results = ref<Record<string, TestResult> | null>(null)
const loading = ref(false)

const runTest = async () => {
  loading.value = true
  try {
    const response = await api.get('/scrape/test-auth')
    results.value = response.data
  } catch (e) {
    console.error('Failed to run scraper test:', e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-10">
    <header>
      <p style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.18em; color: var(--neon-cyan); text-transform: uppercase; text-shadow: 0 0 8px rgba(255,184,0,0.5); margin-bottom: 8px;">
        &#9658; External Uplinks
      </p>
      <h1 style="font-family: 'Press Start 2P', monospace; font-size: 1.2rem; color: var(--text-main); line-height: 1.5;">DIAGNOSTICS</h1>
      <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted); margin-top: 8px;">Verify external scraper API connections.</p>
    </header>

    <div class="flex justify-center">
      <button @click="runTest" :disabled="loading" class="btn-nebula-primary !px-10 !py-3.5" style="font-size: 0.7rem;">
        <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ loading ? 'SYNCHRONIZING...' : 'RUN CONNECTION TEST' }}
      </button>
    </div>

    <div v-if="results" class="grid md:grid-cols-2 gap-6">
      <!-- ScreenScraper -->
      <div class="glass-card flex flex-col transition-all duration-300"
           :style="results.screenscraper.status === 'success'
             ? 'border-color: rgba(0,255,136,0.2); box-shadow: 0 0 20px rgba(0,255,136,0.06)'
             : 'border-color: rgba(255,27,141,0.2); box-shadow: 0 0 20px rgba(255,27,141,0.06)'">
        <div class="p-5 flex items-center justify-between" style="background: rgba(0,0,0,0.3); border-bottom: 1px solid rgba(255,255,255,0.04);">
          <h2 style="font-family: 'Orbitron', sans-serif; font-size: 0.8rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.04em;">ScreenScraper.fr</h2>
          <div class="w-3 h-3 rounded-full"
               :style="results.screenscraper.status === 'success'
                 ? 'background: var(--neon-green); box-shadow: 0 0 10px rgba(0,255,136,0.7)'
                 : 'background: var(--neon-pink); box-shadow: 0 0 10px rgba(255,27,141,0.7)'"></div>
        </div>
        <div class="p-6 space-y-5 flex-1">
          <div class="space-y-2">
            <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;">Uplink Message</p>
            <p class="p-4 rounded-md" style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--text-muted); line-height: 1.6; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,184,0,0.05);">
              {{ results.screenscraper.message }}
            </p>
          </div>
          <div v-if="results.screenscraper.user" class="space-y-1">
            <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;">User ID</p>
            <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--neon-green); font-weight: bold;">{{ results.screenscraper.user }}</p>
          </div>
          <div v-if="results.screenscraper.details" class="space-y-2">
            <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;">Raw Response</p>
            <div class="p-4 rounded-md overflow-auto max-h-48 custom-scrollbar" style="background: rgba(0,0,0,0.7); border: 1px solid rgba(191,95,255,0.12);">
              <pre style="font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: rgba(191,95,255,0.7);">{{ JSON.stringify(results.screenscraper.details.response, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- IGDB -->
      <div class="glass-card flex flex-col transition-all duration-300"
           :style="results.igdb.status === 'success'
             ? 'border-color: rgba(255,184,0,0.2); box-shadow: 0 0 20px rgba(255,184,0,0.06)'
             : 'border-color: rgba(255,27,141,0.2); box-shadow: 0 0 20px rgba(255,27,141,0.06)'">
        <div class="p-5 flex items-center justify-between" style="background: rgba(0,0,0,0.3); border-bottom: 1px solid rgba(255,255,255,0.04);">
          <h2 style="font-family: 'Orbitron', sans-serif; font-size: 0.8rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.04em;">IGDB (Twitch)</h2>
          <div class="w-3 h-3 rounded-full"
               :style="results.igdb.status === 'success'
                 ? 'background: var(--neon-cyan); box-shadow: 0 0 10px rgba(255,184,0,0.7)'
                 : 'background: var(--neon-pink); box-shadow: 0 0 10px rgba(255,27,141,0.7)'"></div>
        </div>
        <div class="p-6 space-y-5 flex-1">
          <div class="space-y-2">
            <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;">Uplink Message</p>
            <p class="p-4 rounded-md" style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--text-muted); line-height: 1.6; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,184,0,0.05);">
              {{ results.igdb.message }}
            </p>
          </div>
          <div v-if="results.igdb.client_id" class="space-y-1">
            <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;">Client Key</p>
            <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--neon-cyan); font-weight: bold;">{{ results.igdb.client_id }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Fix Protocol -->
    <div v-if="results" class="rounded-lg p-6" style="background: transparent; border: 1px dashed rgba(255,184,0,0.1);">
      <h3 style="font-family: 'Orbitron', sans-serif; font-size: 0.65rem; font-weight: 800; letter-spacing: 0.16em; color: var(--text-main); text-transform: uppercase; margin-bottom: 16px;">Fix Protocol</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-2">
          <p style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.12em; color: var(--neon-pink); text-transform: uppercase;">Error 403 / 401</p>
          <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--text-muted); line-height: 1.7;">
            Verify credentials in <code style="color: var(--text-main); background: rgba(255,184,0,0.06); padding: 2px 6px; border-radius: 3px;">docker/.env</code>.
            Check for trailing spaces or special characters.
          </p>
        </div>
        <div class="space-y-2">
          <p style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.12em; color: var(--neon-cyan); text-transform: uppercase;">Re-Sync</p>
          <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--text-muted); line-height: 1.7;">
            After editing <code style="color: var(--text-main); background: rgba(255,184,0,0.06); padding: 2px 6px; border-radius: 3px;">.env</code>, always run:<br/>
            <code style="color: var(--neon-cyan); font-size: 0.78rem;">docker compose up -d</code>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
