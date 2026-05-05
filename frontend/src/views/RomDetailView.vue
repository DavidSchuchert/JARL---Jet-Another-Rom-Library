<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRom, deleteRom as apiDeleteRom, type Rom } from '@/api/roms'
import { getScrapeStatus, rescrapeRom, type ScrapeStatus } from '@/api/scrape'
import PlatformBadge from '@/components/PlatformBadge.vue'

const route = useRoute()
const router = useRouter()
const rom = ref<Rom | null>(null)
const loading = ref(true)
const deleting = ref(false)
const scraping = ref(false)
const scrapeMessage = ref<string | null>(null)
const scrapeStatus = ref<ScrapeStatus | null>(null)
let scrapePoll: ReturnType<typeof setInterval> | null = null

const fetchRom = async () => {
  loading.value = true
  try {
    const id = parseInt(route.params.id as string)
    rom.value = await getRom(id)
  } catch (e) {
    console.error('Failed to fetch ROM details:', e)
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (!rom.value) return
  if (confirm(`Are you sure you want to delete ${rom.value.title}?`)) {
    deleting.value = true
    try {
      await apiDeleteRom(rom.value.id)
      router.push('/')
    } catch (e) {
      console.error('Failed to delete ROM:', e)
      alert('Failed to delete ROM.')
    } finally {
      deleting.value = false
    }
  }
}

const handleRescrape = async () => {
  if (!rom.value) return
  scraping.value = true
  scrapeMessage.value = null
  try {
    await rescrapeRom(rom.value.id)
    scrapeMessage.value = 'Scrape running...'
    await pollScrapeStatus()
    startScrapePolling()
  } catch (e: any) {
    scrapeMessage.value = e?.response?.data?.detail || 'Failed to start scrape.'
  } finally {
    scraping.value = false
  }
}

const pollScrapeStatus = async () => {
  const status = await getScrapeStatus()
  scrapeStatus.value = status

  if (status.status === 'running') {
    scrapeMessage.value = `Scraping ${status.done}/${status.total}${status.current_file ? `: ${status.current_file}` : ''}`
    return
  }

  if (scrapePoll) {
    clearInterval(scrapePoll)
    scrapePoll = null
  }

  if (status.status === 'completed') {
    scrapeMessage.value = status.success > 0 ? 'Scrape complete. Metadata refreshed.' : 'Scrape finished, no metadata found.'
    await fetchRom()
  } else if (status.status === 'failed') {
    scrapeMessage.value = status.errors[0] || 'Scrape failed.'
  }
}

const startScrapePolling = () => {
  if (scrapePoll) return
  scrapePoll = setInterval(() => {
    pollScrapeStatus().catch((e) => {
      console.error('Failed to poll scrape status:', e)
    })
  }, 1000)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(fetchRom)
onUnmounted(() => {
  if (scrapePoll) clearInterval(scrapePoll)
})
</script>

<template>
  <div v-if="loading" class="flex flex-col items-center justify-center min-h-[60vh] gap-4">
    <div class="w-12 h-12 border-4 border-nebula-purple/20 border-t-nebula-purple rounded-full animate-spin"></div>
    <p class="text-slate-500 font-bold uppercase tracking-widest text-xs">Loading Archives...</p>
  </div>

  <div v-else-if="rom" class="relative">
    <!-- Back Button -->
    <button 
      @click="router.back()" 
      class="sticky lg:fixed top-4 lg:top-8 left-0 lg:left-80 z-30 p-3 rounded-xl glass-card text-slate-400 hover:text-white hover:bg-white/5 transition-all group mb-4 lg:mb-0"
    >
      <svg class="w-6 h-6 transform group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>

    <!-- Immersive Backdrop -->
    <div class="fixed inset-0 z-0">
      <img 
        v-if="rom.cover_url" 
        :src="rom.cover_url" 
        class="w-full h-full object-cover opacity-20 blur-[100px] saturate-150 scale-110"
      />
      <div class="absolute inset-0 bg-nebula-base/60"></div>
    </div>

    <!-- Main Content -->
    <div class="relative z-10 grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-12 pt-4">
      
      <!-- Left Column: Poster -->
      <div class="space-y-6">
        <div class="poster-card w-full cursor-default hover:translate-y-0 shadow-2xl">
          <img 
            v-if="rom.cover_url" 
            :src="rom.cover_url" 
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-slate-800 flex items-center justify-center">
            <svg class="w-24 h-24 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <div class="glass-card p-6 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs text-slate-500 font-bold uppercase tracking-widest">Library ID</span>
            <span class="text-xs font-mono text-nebula-purple">#{{ rom.id }}</span>
          </div>
          <div class="h-px bg-white/5"></div>
          <button 
            @click="handleRescrape"
            :disabled="scraping"
            class="w-full btn-nebula-primary"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M5 19a8 8 0 0013-3M19 5A8 8 0 006 8" />
            </svg>
            {{ scraping ? 'Starting...' : 'Rescrape Metadata' }}
          </button>
          <p v-if="scrapeMessage" class="text-xs text-stone-400 leading-relaxed">
            {{ scrapeMessage }}
          </p>
          <div v-if="scrapeStatus?.status === 'running'" class="space-y-2">
            <div class="h-2 bg-stone-950 rounded-full overflow-hidden border border-stone-700">
              <div
                class="h-full bg-amber-400 transition-all duration-300"
                :style="{ width: `${scrapeStatus.percent}%` }"
              ></div>
            </div>
            <div class="flex justify-between text-[10px] uppercase tracking-widest text-stone-500 font-bold">
              <span>{{ scrapeStatus.percent }}%</span>
              <span>{{ scrapeStatus.done }} / {{ scrapeStatus.total }}</span>
            </div>
          </div>
          <button 
            @click="handleDelete"
            :disabled="deleting"
            class="w-full btn-nebula-secondary !bg-red-500/10 !text-red-400 !border-red-500/20 hover:!bg-red-500 hover:!text-white"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            {{ deleting ? 'Deleting...' : 'Remove from Library' }}
          </button>
        </div>
      </div>

      <!-- Right Column: Content -->
      <div class="space-y-8 lg:space-y-10 py-4">
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <PlatformBadge :platformSlug="rom.platform_slug" size="md" />
            <span v-if="rom.region" class="px-2.5 py-0.5 rounded bg-nebula-purple/20 text-nebula-purple text-[10px] font-black uppercase tracking-widest border border-nebula-purple/30">
              {{ rom.region }}
            </span>
          </div>
          <h1 class="text-4xl lg:text-6xl font-black text-white tracking-tighter">{{ rom.title }}</h1>
          <div class="flex flex-wrap items-center gap-4 lg:gap-6">
            <div class="flex items-center gap-2 text-slate-400 font-medium">
              <svg class="w-5 h-5 text-nebula-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {{ rom.year || 'Released Unknown' }}
            </div>
            <div class="flex items-center gap-2 text-slate-400 font-medium">
              <svg class="w-5 h-5 text-nebula-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              {{ rom.players || 'Single Player' }}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="glass-card p-4 bg-white/5 border-white/5">
            <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Genre</p>
            <p class="font-bold text-white">{{ rom.genre || 'Unknown' }}</p>
          </div>
          <div class="glass-card p-4 bg-white/5 border-white/5">
            <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Developer</p>
            <p class="font-bold text-white truncate" :title="rom.developer || undefined">{{ rom.developer || 'Unknown' }}</p>
          </div>
          <div class="glass-card p-4 bg-white/5 border-white/5">
            <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Publisher</p>
            <p class="font-bold text-white truncate" :title="rom.publisher || undefined">{{ rom.publisher || 'Unknown' }}</p>
          </div>
          <div class="glass-card p-4 bg-white/5 border-white/5">
            <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Size</p>
            <p class="font-bold text-white">{{ formatFileSize(rom.size) }}</p>
          </div>
        </div>

        <div v-if="rom.description" class="space-y-4">
          <h2 class="text-2xl font-bold text-white flex items-center gap-3">
            Synopsis
            <div class="h-0.5 flex-1 bg-gradient-to-r from-nebula-purple/50 to-transparent"></div>
          </h2>
          <p class="text-slate-400 text-lg leading-relaxed font-medium">
            {{ rom.description }}
          </p>
        </div>

        <div class="space-y-4">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-[0.2em]">File Information</h2>
          <div class="glass-card p-6 bg-black/20 border-white/5 space-y-4">
            <div>
              <p class="text-[10px] text-slate-600 uppercase font-bold mb-1">Physical Path</p>
              <p class="font-mono text-sm text-slate-400 break-all">{{ rom.path }}</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/5">
              <div>
                <p class="text-[10px] text-slate-600 uppercase font-bold mb-1">Added to Library</p>
                <p class="text-sm text-slate-400">{{ formatDate(rom.created_at) }}</p>
              </div>
              <div v-if="rom.hash_sha1">
                <p class="text-[10px] text-slate-600 uppercase font-bold mb-1">SHA1 Fingerprint</p>
                <p class="font-mono text-[10px] text-nebula-purple/60 truncate">{{ rom.hash_sha1 }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>

  <div v-else class="glass-card p-16 text-center">
    <h2 class="text-2xl font-bold text-white">ROM not found</h2>
    <RouterLink to="/" class="btn-nebula-primary mt-6 inline-flex">Return to Library</RouterLink>
  </div>
</template>
