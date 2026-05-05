<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useScanStore } from '@/stores/scan'
import { startScrape as apiStartScrape, getScrapeStatus as apiGetScrapeStatus, stopScrape as apiStopScrape, type ScrapeStatus } from '@/api/scrape'
import { getPlatforms, type Platform } from '@/api/platforms'

const scanStore = useScanStore()
const scanning = ref(false)
const scrapeStatus = ref<ScrapeStatus | null>(null)
const scraping = ref(false)
const scrapePolling = ref<number | null>(null)
const platforms = ref<Platform[]>([])
const selectedPlatform = ref<string>('')

// Live Log implementation
const liveLog = ref<{msg: string, type: 'info' | 'error' | 'success'}[]>([])
const logEnd = ref<HTMLElement | null>(null)

const addLog = (msg: string, type: 'info' | 'error' | 'success' = 'info') => {
  liveLog.value.push({ msg, type })
  if (liveLog.value.length > 1000) liveLog.value.shift()
}

let lastRenderedScanEvent = 0

watch(() => scanStore.scanEvents[scanStore.scanEvents.length - 1]?.sequence ?? 0, (latestSequence) => {
  if (latestSequence === 0) {
    lastRenderedScanEvent = 0
    return
  }

  const nextEvents = scanStore.scanEvents.filter((event) => event.sequence > lastRenderedScanEvent)

  for (const event of nextEvents) {
    const type = event.type === 'error'
      ? 'error'
      : event.type === 'success'
        ? 'success'
        : 'info'
    const prefix = event.type === 'file' ? 'Scanning' : 'Scanner'
    addLog(`${prefix}: ${event.message}`, type)
    lastRenderedScanEvent = event.sequence
  }
})

watch(() => scrapeStatus.value?.current_file, (newVal) => {
  if (newVal) addLog(`Scraping: ${newVal}`, 'success')
})

const handleStartScan = async (full: boolean = false) => {
  scanning.value = true
  addLog(`Starting ${full ? 'Full' : 'Quick'} Scan...`, 'info')
  try {
    await scanStore.startScan(full)
  } catch (e: any) {
    addLog(`Scan failed to start: ${e.message}`, 'error')
  } finally {
    scanning.value = false
  }
}

const handleStartScrape = async (onlyMissing: boolean = true) => {
  scraping.value = true
  addLog(`Starting Scraper (Only Missing: ${onlyMissing})...`, 'info')
  try {
    await apiStartScrape(selectedPlatform.value || undefined, onlyMissing)
    startScrapePolling()
  } catch (e: any) {
    addLog(`Scraper failed to start: ${e.message}`, 'error')
  } finally {
    scraping.value = false
  }
}

const startScrapePolling = () => {
  if (scrapePolling.value) return
  const poll = async () => {
    try {
      const status = await apiGetScrapeStatus()
      scrapeStatus.value = status
      if (status.status !== 'running') stopScrapePolling()
    } catch (e) {
      console.error('Failed to poll scrape status:', e)
    }
  }
  poll()
  scrapePolling.value = window.setInterval(poll, 2000)
}

const stopScrapePolling = () => {
  if (scrapePolling.value) {
    clearInterval(scrapePolling.value)
    scrapePolling.value = null
  }
}

const handleStopScrape = async () => {
  try {
    await apiStopScrape()
    addLog('Scraper stop requested.', 'info')
  } catch (e) {
    console.error('Failed to stop scrape:', e)
  }
}

const formatTime = (dateString: string | null): string => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  scanStore.attachCurrentScan()
  
  getPlatforms().then(res => platforms.value = res)

  const checkScrape = async () => {
    const status = await apiGetScrapeStatus()
    scrapeStatus.value = status
    if (status.status === 'running') startScrapePolling()
  }
  checkScrape()
})

onUnmounted(() => {
  scanStore.stopPolling()
  stopScrapePolling()
})
</script>

<template>
  <div class="space-y-8 pb-20">
    <header class="flex items-end justify-between">
      <div>
        <p class="text-xs uppercase tracking-widest text-amber-300 font-bold mb-2">Library jobs</p>
        <h1 class="text-3xl font-black text-stone-50">Scan & Metadata</h1>
        <p class="text-stone-500 text-sm mt-2">Index files and fill missing artwork/details.</p>
      </div>
    </header>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      
      <!-- Controls Panel -->
      <div class="xl:col-span-2 space-y-8">
        
        <!-- Filesystem Scan Card -->
        <section class="glass-card">
          <div class="p-5 bg-stone-900/50 flex items-center justify-between border-b border-stone-700/70">
            <h2 class="text-base font-bold text-stone-50 flex items-center gap-3">
              <div class="w-2 h-5 rounded-sm bg-amber-400"></div>
              Filesystem Scanner
            </h2>
            <div class="flex gap-3">
              <button 
                @click="handleStartScan(false)"
                :disabled="scanning || scanStore.scanStatus === 'running'"
                class="btn-nebula-primary !py-2 !text-xs"
              >
                Quick Scan
              </button>
              <button 
                @click="handleStartScan(true)"
                :disabled="scanning || scanStore.scanStatus === 'running'"
                class="btn-nebula-secondary !py-2 !text-xs"
              >
                Full Rescan
              </button>
            </div>
          </div>
          
          <div class="p-6 space-y-6">
            <div v-if="scanStore.scanStatus === 'idle'" class="text-center py-10">
              <p class="text-stone-500 font-medium">Ready to scan.</p>
            </div>
            
            <div v-else class="space-y-6">
              <div class="flex justify-between items-end">
                <div class="space-y-1">
                  <p class="text-[10px] text-stone-500 uppercase font-black tracking-widest">Indexing progress</p>
                  <p class="text-3xl font-black text-stone-50">{{ scanStore.progress.scanned_files }} <span class="text-stone-600 text-xl">/ {{ scanStore.progress.total_files }}</span></p>
                </div>
                <div class="text-right">
                  <p class="text-[10px] text-stone-500 uppercase font-black tracking-widest">Started</p>
                  <p class="text-sm font-bold text-stone-300">{{ formatTime(scanStore.progress.started_at) }}</p>
                </div>
              </div>
              
              <div class="relative h-3 bg-stone-950 rounded-full overflow-hidden border border-stone-700">
                <div 
                  class="absolute inset-y-0 left-0 bg-amber-400 transition-all duration-500"
                  :style="{ width: `${(scanStore.progress.scanned_files / (scanStore.progress.total_files || 1)) * 100}%` }"
                >
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Metadata Scraper Card -->
        <section class="glass-card">
          <div class="p-5 bg-stone-900/50 flex items-center justify-between border-b border-stone-700/70">
            <h2 class="text-base font-bold text-stone-50 flex items-center gap-3">
              <div class="w-2 h-5 rounded-sm bg-emerald-500"></div>
              Metadata Scraper
            </h2>
            <div class="flex gap-3">
              <button 
                @click="handleStartScrape(true)"
                :disabled="scraping || scrapeStatus?.status === 'running'"
                class="btn-nebula-primary !py-2 !text-xs"
              >
                Scrape Missing
              </button>
              <button 
                @click="handleStartScrape(false)"
                :disabled="scraping || scrapeStatus?.status === 'running'"
                class="btn-nebula-secondary !py-2 !text-xs"
              >
                Refresh All
              </button>
            </div>
          </div>

          <div class="p-6 space-y-8">
            <div class="flex flex-wrap items-center gap-6">
              <div class="space-y-2">
                <label class="text-[10px] text-stone-500 uppercase font-black tracking-widest ml-1">Target system</label>
                <select 
                  v-model="selectedPlatform"
                  class="input-nebula w-64 !py-2 !text-sm"
                  :disabled="scraping || scrapeStatus?.status === 'running'"
                >
                  <option value="">All Supported Systems</option>
                  <option v-for="p in platforms" :key="p.slug" :value="p.slug">
                    {{ p.name }}
                  </option>
                </select>
              </div>

              <div class="flex-1 min-w-[200px] grid grid-cols-3 gap-4">
                <div class="p-3 rounded-md bg-emerald-500/5 border border-emerald-500/20 text-center">
                  <p class="text-[10px] text-green-500/50 uppercase font-black mb-1">Success</p>
                  <p class="text-xl font-black text-green-400">{{ scrapeStatus?.success || 0 }}</p>
                </div>
                <div class="p-3 rounded-md bg-red-500/5 border border-red-500/20 text-center">
                  <p class="text-[10px] text-red-500/50 uppercase font-black mb-1">Failed</p>
                  <p class="text-xl font-black text-red-400">{{ scrapeStatus?.failed || 0 }}</p>
                </div>
                <div class="p-3 rounded-md bg-stone-500/5 border border-stone-500/20 text-center">
                  <p class="text-[10px] text-slate-500/50 uppercase font-black mb-1">Skipped</p>
                  <p class="text-xl font-black text-slate-400">{{ scrapeStatus?.skipped || 0 }}</p>
                </div>
              </div>
            </div>

            <div v-if="scrapeStatus?.status === 'running'" class="space-y-4">
              <div class="flex justify-between items-center text-sm">
                <span class="text-stone-400 font-bold">Processing</span>
                <button @click="handleStopScrape" class="text-red-400 hover:text-red-300 font-black uppercase text-[10px] tracking-widest">Stop</button>
              </div>
              <div class="h-2 bg-stone-950 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-emerald-500 transition-all duration-300"
                  :style="{ width: `${scrapeStatus.percent}%` }"
                ></div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Log/Status -->
      <div class="space-y-8">
        <!-- Live Terminal Log -->
        <div class="glass-card flex flex-col h-[500px]">
          <div class="p-4 bg-stone-900/70 flex items-center justify-between border-b border-stone-700/70">
            <span class="text-[10px] font-black text-stone-500 uppercase tracking-widest flex items-center gap-2">
              <div class="w-1.5 h-1.5 rounded-full bg-amber-400"></div>
              Job log
            </span>
            <div class="flex gap-1">
              <div class="w-2 h-2 rounded-full bg-red-500/20"></div>
              <div class="w-2 h-2 rounded-full bg-yellow-500/20"></div>
              <div class="w-2 h-2 rounded-full bg-green-500/20"></div>
            </div>
          </div>
          <div class="flex-1 p-5 font-mono text-[11px] overflow-y-auto space-y-2 bg-[#10100e] custom-scrollbar">
            <div v-if="liveLog.length === 0" class="text-stone-700 italic">No job output yet</div>
            <div v-for="(log, i) in liveLog" :key="i" class="flex gap-3">
              <span class="text-slate-700">[{{ formatTime(new Date().toISOString()) }}]</span>
              <span :class="{
                'text-amber-300': log.type === 'info',
                'text-red-400': log.type === 'error',
                'text-emerald-400 font-bold': log.type === 'success'
              }">{{ log.msg }}</span>
            </div>
            <div ref="logEnd"></div>
          </div>
        </div>

        <!-- System Summary -->
        <div class="glass-card p-6">
          <h3 class="text-sm font-black text-stone-50 uppercase tracking-widest mb-4">Service</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-xs text-stone-500 font-bold uppercase">Backend</span>
              <span class="text-xs text-green-400 font-mono">CONNECTED</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-xs text-stone-500 font-bold uppercase">Status</span>
              <span class="text-xs text-stone-300 font-mono">Ready</span>
            </div>
            <div class="flex justify-between items-center border-t border-stone-700/70 pt-4">
              <span class="text-xs text-stone-500 font-bold uppercase">Workers</span>
              <span class="text-xs text-amber-300 font-bold">4 threads</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
