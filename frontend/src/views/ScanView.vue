<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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

const liveLog = ref<{msg: string, type: 'info' | 'error' | 'success'}[]>([])
const logEnd = ref<HTMLElement | null>(null)

const addLog = (msg: string, type: 'info' | 'error' | 'success' = 'info') => {
  liveLog.value.push({ msg, type })
  if (liveLog.value.length > 1000) liveLog.value.shift()
}

let lastRenderedScanEvent = 0

watch(() => scanStore.scanEvents[scanStore.scanEvents.length - 1]?.sequence ?? 0, (latestSequence) => {
  if (latestSequence === 0) { lastRenderedScanEvent = 0; return }
  const nextEvents = scanStore.scanEvents.filter((e) => e.sequence > lastRenderedScanEvent)
  for (const event of nextEvents) {
    const type = event.type === 'error' ? 'error' : event.type === 'success' ? 'success' : 'info'
    addLog(`${event.type === 'file' ? 'Scanning' : 'Scanner'}: ${event.message}`, type)
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
  if (scrapePolling.value) { clearInterval(scrapePolling.value); scrapePolling.value = null }
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
  return new Date(dateString).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const formatDuration = (seconds: number): string => {
  if (seconds < 0 || !isFinite(seconds)) return '--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${m}m ${s}s`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

const now = ref(Date.now())
let tickInterval: number | null = null

const startTick = () => {
  if (tickInterval) return
  tickInterval = window.setInterval(() => { now.value = Date.now() }, 1000)
}
const stopTick = () => {
  if (tickInterval) { clearInterval(tickInterval); tickInterval = null }
}

const scanEta = computed(() => {
  const p = scanStore.progress
  if (p.status !== 'running' || !p.started_at || !p.scanned_files || !p.total_files) return null
  const elapsed = (now.value - new Date(p.started_at).getTime()) / 1000
  const avgPerFile = elapsed / p.scanned_files
  const remaining = (p.total_files - p.scanned_files) * avgPerFile
  return { avgPerFile, remaining }
})

const scrapeEta = computed(() => {
  const s = scrapeStatus.value
  if (!s || s.status !== 'running' || !s.started_at || !s.done || !s.total) return null
  const elapsed = (now.value - new Date(s.started_at).getTime()) / 1000
  const avgPerGame = elapsed / s.done
  const remaining = (s.total - s.done) * avgPerGame
  return { avgPerGame, remaining }
})

onMounted(() => {
  startTick()
  scanStore.attachCurrentScan()
  getPlatforms().then(res => platforms.value = res)
  apiGetScrapeStatus().then(status => {
    scrapeStatus.value = status
    if (status.status === 'running') startScrapePolling()
  })
})

onUnmounted(() => {
  scanStore.stopPolling()
  stopScrapePolling()
  stopTick()
})
</script>

<template>
  <div class="space-y-8 pb-20">

    <!-- Header -->
    <header>
      <p style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.18em; color: var(--neon-cyan); text-transform: uppercase; text-shadow: 0 0 8px rgba(255,184,0,0.5); margin-bottom: 8px;">
        &#9658; Library Jobs
      </p>
      <h1 style="font-family: 'Press Start 2P', monospace; font-size: 1.2rem; color: var(--text-main); line-height: 1.5;">SCAN & METADATA</h1>
      <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted); margin-top: 8px;">Index files and fill missing artwork/details.</p>
    </header>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">

      <!-- Controls -->
      <div class="xl:col-span-2 space-y-6">

        <!-- Filesystem Scanner -->
        <section class="glass-card overflow-hidden">
          <div class="p-4 flex items-center justify-between" style="background: rgba(255,184,0,0.03); border-bottom: 1px solid rgba(255,184,0,0.08);">
            <h2 class="flex items-center gap-3" style="font-family: 'Orbitron', sans-serif; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.06em; color: var(--text-main); text-transform: uppercase;">
              <div class="w-1.5 h-5 rounded-sm" style="background: var(--neon-cyan); box-shadow: 0 0 8px rgba(255,184,0,0.5)"></div>
              Filesystem Scanner
            </h2>
            <div class="flex gap-3">
              <button @click="handleStartScan(false)" :disabled="scanning || scanStore.scanStatus === 'running'" class="btn-nebula-primary !py-1.5 !text-[0.62rem]">
                Quick Scan
              </button>
              <button @click="handleStartScan(true)" :disabled="scanning || scanStore.scanStatus === 'running'" class="btn-nebula-secondary !py-1.5 !text-[0.62rem]">
                Full Rescan
              </button>
            </div>
          </div>

          <div class="p-6 space-y-6">
            <div v-if="scanStore.scanStatus === 'idle'" class="text-center py-8">
              <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--text-muted);">Ready to scan.</p>
            </div>

            <div v-else class="space-y-5">
              <div class="flex justify-between items-end">
                <div>
                  <p style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">Indexing Progress</p>
                  <p style="font-family: 'Press Start 2P', monospace; font-size: 1.2rem; color: var(--text-main);">
                    {{ scanStore.progress.scanned_files }}
                    <span style="color: var(--text-muted); font-size: 0.8rem;"> / {{ scanStore.progress.total_files }}</span>
                  </p>
                </div>
                <div class="text-right space-y-2">
                  <div>
                    <p style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Started</p>
                    <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--text-main);">{{ formatTime(scanStore.progress.started_at) }}</p>
                  </div>
                  <div v-if="scanEta" class="flex gap-4 justify-end">
                    <div>
                      <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px;">Avg/File</p>
                      <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--neon-cyan);">{{ scanEta.avgPerFile.toFixed(2) }}s</p>
                    </div>
                    <div>
                      <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px;">ETA</p>
                      <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--neon-cyan);">{{ formatDuration(scanEta.remaining) }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="relative h-2 rounded-full overflow-hidden" style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,184,0,0.08);">
                <div class="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
                     :style="{ width: `${(scanStore.progress.scanned_files / (scanStore.progress.total_files || 1)) * 100}%`, background: 'var(--neon-cyan)', boxShadow: '0 0 8px rgba(255,184,0,0.6)' }">
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Metadata Scraper -->
        <section class="glass-card overflow-hidden">
          <div class="p-4 flex items-center justify-between" style="background: rgba(0,255,136,0.03); border-bottom: 1px solid rgba(0,255,136,0.08);">
            <h2 class="flex items-center gap-3" style="font-family: 'Orbitron', sans-serif; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.06em; color: var(--text-main); text-transform: uppercase;">
              <div class="w-1.5 h-5 rounded-sm" style="background: var(--neon-green); box-shadow: 0 0 8px rgba(0,255,136,0.5)"></div>
              Metadata Scraper
            </h2>
            <div class="flex gap-3">
              <button @click="handleStartScrape(true)" :disabled="scraping || scrapeStatus?.status === 'running'" class="btn-nebula-primary !py-1.5 !text-[0.62rem]">
                Scrape Missing
              </button>
              <button @click="handleStartScrape(false)" :disabled="scraping || scrapeStatus?.status === 'running'" class="btn-nebula-secondary !py-1.5 !text-[0.62rem]">
                Refresh All
              </button>
            </div>
          </div>

          <div class="p-6 space-y-6">
            <div class="flex flex-wrap items-center gap-6">
              <div class="space-y-2">
                <label style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; display: block; margin-left: 2px;">Target System</label>
                <select v-model="selectedPlatform" class="input-nebula w-64 !py-2 !text-sm"
                        :disabled="scraping || scrapeStatus?.status === 'running'">
                  <option value="">All Supported Systems</option>
                  <option v-for="p in platforms" :key="p.slug" :value="p.slug">{{ p.name }}</option>
                </select>
              </div>

              <div class="flex-1 min-w-[200px] grid grid-cols-3 gap-3">
                <div class="p-3 rounded-md text-center" style="background: rgba(0,255,136,0.05); border: 1px solid rgba(0,255,136,0.15);">
                  <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; color: rgba(0,255,136,0.5); text-transform: uppercase; margin-bottom: 4px;">Success</p>
                  <p style="font-family: 'Press Start 2P', monospace; font-size: 1.1rem; color: var(--neon-green);">{{ scrapeStatus?.success || 0 }}</p>
                </div>
                <div class="p-3 rounded-md text-center" style="background: rgba(255,53,32,0.05); border: 1px solid rgba(255,53,32,0.15);">
                  <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; color: rgba(255,53,32,0.5); text-transform: uppercase; margin-bottom: 4px;">Failed</p>
                  <p style="font-family: 'Press Start 2P', monospace; font-size: 1.1rem; color: var(--neon-pink);">{{ scrapeStatus?.failed || 0 }}</p>
                </div>
                <div class="p-3 rounded-md text-center" style="background: rgba(255,184,0,0.05); border: 1px solid rgba(255,184,0,0.12);">
                  <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Skipped</p>
                  <p style="font-family: 'Press Start 2P', monospace; font-size: 1.1rem; color: var(--text-muted);">{{ scrapeStatus?.skipped || 0 }}</p>
                </div>
              </div>
            </div>

            <div v-if="scrapeStatus?.status === 'running'" class="space-y-4">
              <!-- Live-Card: currently scraping ROM -->
              <div class="rounded-lg overflow-hidden flex gap-4 p-4 transition-all duration-500"
                   style="background: rgba(0,255,136,0.04); border: 1px solid rgba(0,255,136,0.15);">
                <!-- Cover thumbnail -->
                <div class="flex-shrink-0 w-16 h-20 rounded overflow-hidden flex items-center justify-center"
                     style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,184,0,0.1);">
                  <img v-if="scrapeStatus.current_cover"
                       :src="scrapeStatus.current_cover"
                       :key="scrapeStatus.current_cover"
                       class="w-full h-full object-cover"
                       style="animation: fadeInCover 0.4s ease"
                       @error="($event.target as HTMLImageElement).style.display='none'"
                  />
                  <svg v-else class="w-7 h-7 opacity-20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>

                <!-- Title + progress info -->
                <div class="flex-1 min-w-0 flex flex-col justify-between py-0.5">
                  <div>
                    <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.12em; color: var(--neon-green); text-transform: uppercase; margin-bottom: 4px;">Now Scraping</p>
                    <p class="truncate" style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--text-main); font-weight: 600;">
                      {{ scrapeStatus.current_title || scrapeStatus.current_file || '...' }}
                    </p>
                    <p class="truncate mt-1" style="font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: var(--text-muted);">
                      {{ scrapeStatus.current_file }}
                    </p>
                  </div>
                  <div class="flex items-center gap-3 mt-2 flex-wrap">
                    <span style="font-family: 'Press Start 2P', monospace; font-size: 0.7rem; color: var(--neon-green);">{{ scrapeStatus.done }}</span>
                    <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: var(--text-muted);">/ {{ scrapeStatus.total }}</span>
                    <span style="font-family: 'Orbitron', monospace; font-size: 0.65rem; color: var(--neon-green);">{{ scrapeStatus.percent.toFixed(1) }}%</span>
                    <template v-if="scrapeEta">
                      <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.6rem; color: var(--text-muted);">·</span>
                      <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.6rem; color: var(--neon-cyan);">{{ scrapeEta.avgPerGame.toFixed(1) }}s/game</span>
                      <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.6rem; color: var(--text-muted);">·</span>
                      <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.6rem; color: var(--neon-cyan);">ETA {{ formatDuration(scrapeEta.remaining) }}</span>
                    </template>
                  </div>
                </div>

                <button @click="handleStopScrape" class="flex-shrink-0 self-start mt-1"
                        style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; color: var(--neon-pink); text-transform: uppercase; padding: 4px 8px; border: 1px solid rgba(255,53,32,0.3); border-radius: 4px;"
                        onmouseenter="this.style.background='rgba(255,53,32,0.1)'"
                        onmouseleave="this.style.background='transparent'">
                  STOP
                </button>
              </div>

              <!-- Progress bar -->
              <div class="h-1.5 rounded-full overflow-hidden" style="background: rgba(0,0,0,0.5); border: 1px solid rgba(0,255,136,0.1);">
                <div class="h-full rounded-full transition-all duration-300"
                     :style="{ width: `${scrapeStatus.percent}%`, background: 'var(--neon-green)', boxShadow: '0 0 8px rgba(0,255,136,0.6)' }"></div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">

        <!-- Terminal Log -->
        <div class="glass-card flex flex-col" style="height: 480px;">
          <div class="p-3 flex items-center justify-between" style="background: rgba(0,0,0,0.4); border-bottom: 1px solid rgba(255,184,0,0.08);">
            <span class="flex items-center gap-2" style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase;">
              <div class="w-1.5 h-1.5 rounded-full animate-pulse" style="background: var(--neon-cyan); box-shadow: 0 0 4px var(--neon-cyan)"></div>
              Job Log
            </span>
            <!-- Terminal dots -->
            <div class="flex gap-1.5">
              <div class="w-2.5 h-2.5 rounded-full" style="background: rgba(255,53,32,0.35)"></div>
              <div class="w-2.5 h-2.5 rounded-full" style="background: rgba(255,229,0,0.35)"></div>
              <div class="w-2.5 h-2.5 rounded-full" style="background: rgba(0,255,136,0.35)"></div>
            </div>
          </div>
          <div class="flex-1 p-4 overflow-y-auto space-y-1.5 custom-scrollbar" style="background: rgba(2,1,8,0.95);">
            <div v-if="liveLog.length === 0" style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--text-muted); font-style: italic;">
              No job output yet_
            </div>
            <div v-for="(log, i) in liveLog" :key="i" class="flex gap-2 leading-relaxed">
              <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: rgba(255,184,0,0.25); flex-shrink: 0;">[{{ formatTime(new Date().toISOString()) }}]</span>
              <span :style="{
                fontFamily: '\'Share Tech Mono\', monospace',
                fontSize: '0.65rem',
                color: log.type === 'error' ? 'var(--neon-pink)' : log.type === 'success' ? 'var(--neon-green)' : 'rgba(255,184,0,0.7)',
                fontWeight: log.type === 'success' ? '700' : '400',
              }">{{ log.msg }}</span>
            </div>
            <div ref="logEnd"></div>
          </div>
        </div>

        <!-- Service Status -->
        <div class="rounded-lg p-5" style="background: rgba(12,10,28,0.92); border: 1px solid rgba(255,184,0,0.08);">
          <h3 style="font-family: 'Orbitron', sans-serif; font-size: 0.65rem; font-weight: 800; letter-spacing: 0.14em; color: var(--text-main); text-transform: uppercase; margin-bottom: 16px;">Service Status</h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase;">Backend</span>
              <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--neon-green); text-shadow: 0 0 6px rgba(0,255,136,0.4);">CONNECTED</span>
            </div>
            <div class="flex justify-between items-center">
              <span style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase;">Status</span>
              <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--text-muted);">Ready</span>
            </div>
            <div class="flex justify-between items-center pt-3" style="border-top: 1px solid rgba(255,184,0,0.07);">
              <span style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase;">Workers</span>
              <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--neon-cyan);">4 THREADS</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeInCover {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
</style>
