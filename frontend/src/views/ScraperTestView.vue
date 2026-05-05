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
      <h1 class="text-4xl font-black text-white tracking-tighter mb-2 italic">DIAGNOSTICS</h1>
      <p class="text-slate-500 font-bold uppercase tracking-widest text-xs">Verify external uplink connections</p>
    </header>

    <div class="flex justify-center">
      <button 
        @click="runTest" 
        :disabled="loading"
        class="btn-nebula-primary !px-12 !py-4 text-lg"
      >
        <svg v-if="loading" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ loading ? 'Synchronizing...' : 'Start Connection Test' }}
      </button>
    </div>

    <div v-if="results" class="grid md:grid-cols-2 gap-8">
      <!-- ScreenScraper Result -->
      <div class="glass-card flex flex-col group hover:border-nebula-purple/30 transition-all duration-500">
        <div class="p-6 bg-white/5 border-b border-white/5 flex items-center justify-between">
          <h2 class="text-xl font-black text-white tracking-tight">ScreenScraper.fr</h2>
          <div 
            class="w-3 h-3 rounded-full shadow-[0_0_10px]"
            :class="results.screenscraper.status === 'success' ? 'bg-green-500 shadow-green-500/50' : 'bg-red-500 shadow-red-500/50'"
          ></div>
        </div>

        <div class="p-8 space-y-6 flex-1">
          <div class="space-y-2">
            <p class="text-[10px] text-slate-500 uppercase font-black tracking-widest">Uplink Message</p>
            <p class="text-slate-300 font-mono text-sm leading-relaxed p-4 bg-black/40 rounded-xl border border-white/5">
              {{ results.screenscraper.message }}
            </p>
          </div>

          <div v-if="results.screenscraper.user" class="space-y-1">
            <p class="text-[10px] text-slate-500 uppercase font-black tracking-widest">User ID</p>
            <p class="text-white font-bold">{{ results.screenscraper.user }}</p>
          </div>

          <div v-if="results.screenscraper.details" class="space-y-2 mt-4">
            <p class="text-[10px] text-slate-500 uppercase font-black tracking-widest">Raw Response</p>
            <div class="bg-black/60 p-4 rounded-xl text-[10px] font-mono text-nebula-purple/80 overflow-auto max-h-48 custom-scrollbar">
              <pre>{{ JSON.stringify(results.screenscraper.details.response, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- IGDB Result -->
      <div class="glass-card flex flex-col group hover:border-nebula-blue/30 transition-all duration-500">
        <div class="p-6 bg-white/5 border-b border-white/5 flex items-center justify-between">
          <h2 class="text-xl font-black text-white tracking-tight">IGDB (Twitch)</h2>
          <div 
            class="w-3 h-3 rounded-full shadow-[0_0_10px]"
            :class="results.igdb.status === 'success' ? 'bg-green-500 shadow-green-500/50' : 'bg-red-500 shadow-red-500/50'"
          ></div>
        </div>

        <div class="p-8 space-y-6 flex-1">
          <div class="space-y-2">
            <p class="text-[10px] text-slate-500 uppercase font-black tracking-widest">Uplink Message</p>
            <p class="text-slate-300 font-mono text-sm leading-relaxed p-4 bg-black/40 rounded-xl border border-white/5">
              {{ results.igdb.message }}
            </p>
          </div>

          <div v-if="results.igdb.client_id" class="space-y-1">
            <p class="text-[10px] text-slate-500 uppercase font-black tracking-widest">Client Key</p>
            <p class="text-white font-bold font-mono">{{ results.igdb.client_id }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="results" class="glass-card p-8 border-dashed border-white/10 bg-transparent">
      <h3 class="text-sm font-black text-white uppercase tracking-[0.2em] mb-4">Fix Protocol</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-2">
          <p class="text-[10px] text-red-500 uppercase font-black tracking-widest">Error 403 / 401</p>
          <p class="text-sm text-slate-400 leading-relaxed">
            Verify credentials in <code class="text-white bg-white/10 px-1.5 py-0.5 rounded">docker/.env</code>. 
            Ensure no trailing spaces or special shell characters are unmasked.
          </p>
        </div>
        <div class="space-y-2">
          <p class="text-[10px] text-nebula-blue uppercase font-black tracking-widest">Re-Sync</p>
          <p class="text-sm text-slate-400 leading-relaxed">
            After editing the <code class="text-white">.env</code>, always execute: <br/>
            <code class="text-nebula-blue font-mono">docker compose up -d</code>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
