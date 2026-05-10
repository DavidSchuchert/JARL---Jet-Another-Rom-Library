<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRom, deleteRom as apiDeleteRom, updateRom, type Rom, type RomUpdatePayload } from '@/api/roms'
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

// Edit modal
const editOpen = ref(false)
const saving = ref(false)
const editForm = ref<RomUpdatePayload>({})

const parsedLanguages = computed<string[]>(() => {
  if (!rom.value?.languages) return []
  try { return JSON.parse(rom.value.languages) } catch { return [] }
})

const parsedScreenshots = computed<string[]>(() => {
  if (!rom.value?.screenshots) return []
  try { return JSON.parse(rom.value.screenshots) } catch { return [] }
})

const openEdit = () => {
  if (!rom.value) return
  editForm.value = {
    title: rom.value.title,
    description: rom.value.description ?? undefined,
    year: rom.value.year,
    release_date: rom.value.release_date,
    developer: rom.value.developer,
    publisher: rom.value.publisher,
    genre: rom.value.genre,
    players: rom.value.players,
    region: rom.value.region,
    cover_url: rom.value.cover_url,
    rating: rom.value.rating,
  }
  editOpen.value = true
}

const saveEdit = async () => {
  if (!rom.value) return
  saving.value = true
  try {
    rom.value = await updateRom(rom.value.id, editForm.value)
    editOpen.value = false
  } catch (e) {
    console.error('Failed to save edits:', e)
  } finally {
    saving.value = false
  }
}

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
  if (confirm(`Delete ${rom.value.title} from archive?`)) {
    deleting.value = true
    try {
      await apiDeleteRom(rom.value.id)
      router.push('/')
    } catch (e) {
      console.error('Failed to delete ROM:', e)
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
  if (scrapePoll) { clearInterval(scrapePoll); scrapePoll = null }
  if (status.status === 'completed') {
    scrapeMessage.value = status.success > 0 ? 'Scrape complete. Metadata refreshed.' : 'Finished — no metadata found.'
    await fetchRom()
  } else if (status.status === 'failed') {
    scrapeMessage.value = status.errors[0] || 'Scrape failed.'
  }
}

const startScrapePolling = () => {
  if (scrapePoll) return
  scrapePoll = setInterval(() => {
    pollScrapeStatus().catch(console.error)
  }, 1000)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

onMounted(fetchRom)
onUnmounted(() => { if (scrapePoll) clearInterval(scrapePoll) })
</script>

<template>
  <!-- Loading -->
  <div v-if="loading" class="flex flex-col items-center justify-center min-h-[60vh] gap-5">
    <div class="chip-loader"></div>
    <p style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.2em; color: var(--text-muted); text-transform: uppercase;">Loading Archives...</p>
  </div>

  <div v-else-if="rom" class="relative">
    <!-- Back Button -->
    <button
      @click="router.back()"
      class="sticky lg:fixed top-4 lg:top-8 left-0 lg:left-80 z-30 p-2.5 rounded-lg glass-card transition-all group mb-4 lg:mb-0"
      style="color: var(--text-muted);"
      onmouseenter="this.style.color='var(--neon-cyan)'"
      onmouseleave="this.style.color='var(--text-muted)'"
    >
      <svg class="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>

    <!-- Immersive Backdrop -->
    <div class="fixed inset-0 z-0 pointer-events-none">
      <img v-if="rom.cover_url" :src="rom.cover_url"
           class="w-full h-full object-cover opacity-10 blur-[80px] saturate-150 scale-110" />
      <div class="absolute inset-0" style="background: rgba(6,4,15,0.7)"></div>
    </div>

    <!-- Content -->
    <div class="relative z-10 grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-10 pt-4">

      <!-- Left: Poster + Actions -->
      <div class="space-y-5">
        <div class="poster-card w-full cursor-default shadow-2xl"
             style="border-color: rgba(255,184,0,0.2); box-shadow: 0 0 40px rgba(255,184,0,0.08), 0 20px 60px rgba(0,0,0,0.5);">
          <img v-if="rom.cover_url" :src="rom.cover_url" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center" style="background: var(--bg-card)">
            <svg class="w-20 h-20" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: rgba(255,184,0,0.15)">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <!-- Action card -->
        <div class="rounded-lg p-5 space-y-4" style="background: rgba(12,10,28,0.92); border: 1px solid rgba(255,184,0,0.12);">
          <div class="flex items-center justify-between">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;">Library ID</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--neon-purple);">#{{ rom.id }}</span>
          </div>
          <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,184,0,0.12), transparent)"></div>

          <button @click="openEdit" class="w-full btn-nebula-secondary" style="font-size: 0.7rem;">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit Metadata
          </button>

          <button @click="handleRescrape" :disabled="scraping" class="w-full btn-nebula-primary" style="font-size: 0.7rem;">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M5 19a8 8 0 0013-3M19 5A8 8 0 006 8" />
            </svg>
            {{ scraping ? 'Starting...' : 'Rescrape Metadata' }}
          </button>

          <p v-if="scrapeMessage" style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--text-muted); line-height: 1.6;">
            {{ scrapeMessage }}
          </p>

          <div v-if="scrapeStatus?.status === 'running'" class="space-y-2">
            <div class="h-1.5 rounded-full overflow-hidden" style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,184,0,0.1);">
              <div class="h-full transition-all duration-300 rounded-full"
                   :style="{ width: `${scrapeStatus.percent}%`, background: 'var(--neon-cyan)', boxShadow: '0 0 8px rgba(255,184,0,0.6)' }"></div>
            </div>
            <div class="flex justify-between" style="font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: var(--text-muted);">
              <span>{{ scrapeStatus.percent }}%</span>
              <span>{{ scrapeStatus.done }} / {{ scrapeStatus.total }}</span>
            </div>
          </div>

          <button @click="handleDelete" :disabled="deleting" class="w-full btn-nebula-secondary" style="color: var(--neon-pink); border-color: rgba(255,53,32,0.25); font-size: 0.7rem;">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            {{ deleting ? 'Deleting...' : 'Remove from Library' }}
          </button>
        </div>
      </div>

      <!-- Right: Metadata -->
      <div class="space-y-8 py-2">
        <div class="space-y-4">
          <div class="flex flex-wrap items-center gap-3">
            <PlatformBadge :platformSlug="rom.platform_slug" />
            <span v-if="rom.region" class="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase"
                  style="font-family: 'Share Tech Mono', monospace; letter-spacing: 0.06em; background: rgba(0,200,160,0.12); color: var(--neon-purple); border: 1px solid rgba(0,200,160,0.25);">
              {{ rom.region }}
            </span>
            <span v-if="rom.version" class="px-2.5 py-0.5 rounded text-[10px] font-bold"
                  style="font-family: 'Share Tech Mono', monospace; letter-spacing: 0.06em; background: rgba(255,184,0,0.08); color: var(--neon-amber); border: 1px solid rgba(255,184,0,0.2);">
              v{{ rom.version }}
            </span>
            <span v-for="lang in parsedLanguages" :key="lang"
                  class="px-2 py-0.5 rounded text-[10px]"
                  style="font-family: 'Share Tech Mono', monospace; background: rgba(40,208,96,0.08); color: var(--neon-green); border: 1px solid rgba(40,208,96,0.2);">
              {{ lang }}
            </span>
          </div>

          <h1 style="font-size: clamp(1.8rem, 5vw, 3.5rem); font-weight: 900; color: var(--text-main); line-height: 1.15; letter-spacing: -0.02em;">
            {{ rom.title }}
          </h1>

          <div class="flex flex-wrap items-center gap-5">
            <div class="flex items-center gap-2" style="color: var(--text-muted); font-family: 'Share Tech Mono', monospace; font-size: 0.8rem;">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--neon-cyan)">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {{ rom.release_date || rom.year || 'Unknown Year' }}
            </div>
            <div class="flex items-center gap-2" style="color: var(--text-muted); font-family: 'Share Tech Mono', monospace; font-size: 0.8rem;">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--neon-purple)">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              {{ rom.players || 'Single Player' }}
            </div>
            <!-- Rating -->
            <div v-if="rom.rating !== null && rom.rating !== undefined" class="flex items-center gap-2">
              <div class="flex items-center gap-1.5 px-2.5 py-1 rounded"
                   style="background: rgba(255,184,0,0.08); border: 1px solid rgba(255,184,0,0.2);">
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24" style="color: var(--neon-amber)">
                  <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
                <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--neon-amber); font-weight: 700;">
                  {{ rom.rating.toFixed(0) }}<span style="font-size: 0.65rem; opacity: 0.6;">/100</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="(item, i) in [
            { label: 'Genre',     value: rom.genre },
            { label: 'Developer', value: rom.developer },
            { label: 'Publisher', value: rom.publisher },
            { label: 'Size',      value: formatFileSize(rom.size) },
          ].filter(item => item.value)" :key="i" class="rounded-md p-4" style="background: rgba(12,10,28,0.8); border: 1px solid rgba(255,184,0,0.07);">
            <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">{{ item.label }}</p>
            <p class="font-bold truncate" :title="item.value!" style="color: var(--text-main); font-size: 0.85rem;">{{ item.value }}</p>
          </div>
        </div>

        <!-- Description -->
        <div v-if="rom.description" class="space-y-3">
          <h2 class="flex items-center gap-3" style="font-family: 'Orbitron', sans-serif; font-size: 0.9rem; font-weight: 800; letter-spacing: 0.06em; color: var(--text-main); text-transform: uppercase;">
            Synopsis
            <div class="h-px flex-1" style="background: linear-gradient(90deg, rgba(255,184,0,0.3), transparent)"></div>
          </h2>
          <p style="color: var(--text-muted); font-size: 0.95rem; line-height: 1.75; font-weight: 400;">
            {{ rom.description }}
          </p>
        </div>

        <!-- Screenshots -->
        <div v-if="parsedScreenshots.length > 0" class="space-y-3">
          <h2 class="flex items-center gap-3" style="font-family: 'Orbitron', sans-serif; font-size: 0.9rem; font-weight: 800; letter-spacing: 0.06em; color: var(--text-main); text-transform: uppercase;">
            Screenshots
            <div class="h-px flex-1" style="background: linear-gradient(90deg, rgba(255,184,0,0.3), transparent)"></div>
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div v-for="(ss, i) in parsedScreenshots" :key="i"
                 class="rounded overflow-hidden aspect-video"
                 style="border: 1px solid rgba(255,184,0,0.1);">
              <img :src="ss" class="w-full h-full object-cover" @error="($event.target as HTMLImageElement).parentElement!.style.display='none'" />
            </div>
          </div>
        </div>

        <!-- File Info -->
        <div class="space-y-3">
          <h2 style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.16em; color: var(--text-muted); text-transform: uppercase;">File Information</h2>
          <div class="rounded-md p-5 space-y-4" style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,184,0,0.06);">
            <div>
              <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Path</p>
              <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--neon-cyan); opacity: 0.7; word-break: break-all;">{{ rom.path }}</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4" style="border-top: 1px solid rgba(255,184,0,0.05);">
              <div>
                <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Added</p>
                <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted);">{{ formatDate(rom.created_at) }}</p>
              </div>
              <div v-if="rom.hash_sha1">
                <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">SHA1</p>
                <p class="truncate" style="font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: rgba(0,200,160,0.5);">{{ rom.hash_sha1 }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="glass-card p-16 text-center">
    <h2 style="font-family: 'Press Start 2P', monospace; font-size: 1rem; color: var(--text-main); margin-bottom: 1.5rem;">ROM NOT FOUND</h2>
    <RouterLink to="/" class="btn-nebula-primary inline-flex">Return to Library</RouterLink>
  </div>

  <!-- Edit Modal -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="editOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4"
           style="background: rgba(0,0,0,0.75); backdrop-filter: blur(8px);"
           @click.self="editOpen = false">
        <div class="w-full max-w-2xl rounded-xl overflow-hidden shadow-2xl"
             style="background: #100d06; border: 1px solid rgba(255,184,0,0.2); max-height: 90vh; display: flex; flex-direction: column;">

          <!-- Modal Header -->
          <div class="p-5 flex items-center justify-between flex-shrink-0"
               style="background: rgba(255,184,0,0.04); border-bottom: 1px solid rgba(255,184,0,0.1);">
            <div>
              <p style="font-family: 'Orbitron', sans-serif; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.16em; color: var(--neon-amber); text-transform: uppercase;">Edit Metadata</p>
              <h3 class="mt-1 truncate" style="font-family: 'Orbitron', sans-serif; font-size: 0.85rem; font-weight: 800; color: var(--text-main);">{{ rom?.title }}</h3>
            </div>
            <button @click="editOpen = false" style="color: var(--text-muted);"
                    onmouseenter="this.style.color='var(--text-main)'" onmouseleave="this.style.color='var(--text-muted)'">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Modal Body -->
          <div class="p-6 overflow-y-auto custom-scrollbar space-y-5 flex-1">

            <!-- Title + Year row -->
            <div class="grid grid-cols-2 gap-4">
              <div class="col-span-2 space-y-1.5">
                <label class="edit-label">Title</label>
                <input v-model="editForm.title" class="input-nebula w-full" placeholder="Game title" />
              </div>
            </div>

            <!-- Release + Genre row -->
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="edit-label">Release Date</label>
                <input v-model="editForm.release_date" class="input-nebula w-full" placeholder="YYYY-MM-DD" />
              </div>
              <div class="space-y-1.5">
                <label class="edit-label">Genre</label>
                <input v-model="editForm.genre" class="input-nebula w-full" placeholder="Action / RPG..." />
              </div>
            </div>

            <!-- Developer + Publisher -->
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="edit-label">Developer</label>
                <input v-model="editForm.developer" class="input-nebula w-full" />
              </div>
              <div class="space-y-1.5">
                <label class="edit-label">Publisher</label>
                <input v-model="editForm.publisher" class="input-nebula w-full" />
              </div>
            </div>

            <!-- Region + Players + Rating -->
            <div class="grid grid-cols-3 gap-4">
              <div class="space-y-1.5">
                <label class="edit-label">Region</label>
                <input v-model="editForm.region" class="input-nebula w-full" placeholder="USA" />
              </div>
              <div class="space-y-1.5">
                <label class="edit-label">Players</label>
                <input v-model="editForm.players" class="input-nebula w-full" placeholder="1-2" />
              </div>
              <div class="space-y-1.5">
                <label class="edit-label">Rating (0–100)</label>
                <input v-model.number="editForm.rating" type="number" min="0" max="100" class="input-nebula w-full" placeholder="75" />
              </div>
            </div>

            <!-- Cover URL -->
            <div class="space-y-1.5">
              <label class="edit-label">Cover URL</label>
              <input v-model="editForm.cover_url" class="input-nebula w-full" placeholder="https://..." />
            </div>

            <!-- Description -->
            <div class="space-y-1.5">
              <label class="edit-label">Description</label>
              <textarea v-model="editForm.description" class="input-nebula w-full" rows="5" placeholder="Game synopsis..." style="resize: vertical;"></textarea>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="p-5 flex justify-end gap-3 flex-shrink-0"
               style="background: rgba(0,0,0,0.3); border-top: 1px solid rgba(255,184,0,0.08);">
            <button @click="editOpen = false" class="btn-nebula-secondary !px-6 !py-2 !text-[0.68rem]">Cancel</button>
            <button @click="saveEdit" :disabled="saving" class="btn-nebula-primary !px-6 !py-2 !text-[0.68rem]">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.edit-label {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.5rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--text-muted);
  text-transform: uppercase;
  display: block;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
