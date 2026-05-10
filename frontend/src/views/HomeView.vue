<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useRoute, useRouter } from 'vue-router'
import { useRomsStore } from '@/stores/roms'
import RomGrid from '@/components/RomGrid.vue'
import SearchBar from '@/components/SearchBar.vue'
import FilterBar from '@/components/FilterBar.vue'
import StatsWidget from '@/components/StatsWidget.vue'

const romsStore = useRomsStore()
const route = useRoute()
const router = useRouter()
const search = ref('')
const selectedPlatform = ref('')

const handleSortChange = (e: Event) => {
  const [by, dir] = (e.target as HTMLSelectElement).value.split(':')
  romsStore.setSort(by, dir as 'asc' | 'desc')
  romsStore.setPage(1)
  syncQuery()
  fetchRoms()
}

const fetchRoms = () => {
  romsStore.fetchRoms({
    page: romsStore.pagination.page,
    search: search.value,
    platform: selectedPlatform.value
  })
}

const debouncedFetch = useDebounceFn(() => {
  romsStore.setPage(1)
  syncQuery()
  fetchRoms()
}, 250)

const getRoutePlatform = () => {
  const platform = route.query.platform
  return typeof platform === 'string' ? platform : ''
}

onMounted(() => {
  selectedPlatform.value = getRoutePlatform()
  if (typeof route.query.search === 'string') {
    search.value = route.query.search
  }
  fetchRoms()
})

const syncQuery = () => {
  const query = { ...route.query }
  if (search.value) { query.search = search.value } else { delete query.search }
  if (selectedPlatform.value) { query.platform = selectedPlatform.value } else { delete query.platform }
  router.replace({ query })
}

watch(search, () => { debouncedFetch() })
watch(selectedPlatform, () => { romsStore.setPage(1); syncQuery(); fetchRoms() })
watch(() => route.query.platform, () => {
  const next = getRoutePlatform()
  if (selectedPlatform.value !== next) selectedPlatform.value = next
})
watch(() => route.query.search, () => {
  const next = typeof route.query.search === 'string' ? route.query.search : ''
  if (search.value !== next) search.value = next
})

const handlePageChange = (page: number) => {
  romsStore.setPage(page)
  fetchRoms()
}

const handleDelete = async (id: number) => {
  if (confirm('Delete this ROM from the archive?')) {
    await romsStore.deleteRom(id)
  }
}
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <header class="relative overflow-hidden rounded-lg p-5" style="background: rgba(11,9,22,0.9); border: 1px solid rgba(255,184,0,0.12); box-shadow: 0 18px 50px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,184,0,0.06);">
      <!-- Decorative cartridge pins -->
      <div class="absolute inset-y-0 right-0 hidden w-1/3 sm:block opacity-50 pointer-events-none">
        <div class="absolute right-10 top-5 h-20 w-28 rounded-lg rotate-6"
             style="border: 1px solid rgba(255,184,0,0.2); background: rgba(255,184,0,0.03)"></div>
        <div class="absolute right-16 bottom-5 grid w-28 grid-cols-7 gap-1">
          <span v-for="pin in 7" :key="pin" class="h-8 rounded-sm"
                :style="{ background: `rgba(255,184,0,${0.15 + pin * 0.03})`, boxShadow: `0 0 4px rgba(255,184,0,0.2)` }"></span>
        </div>
      </div>

      <div class="relative flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.18em; color: var(--neon-cyan); text-transform: uppercase; text-shadow: 0 0 8px rgba(255,184,0,0.5); margin-bottom: 8px;">
            &#9658; Game Library
          </p>
          <h1 style="font-family: 'Press Start 2P', monospace; font-size: 1.4rem; color: var(--text-main); line-height: 1.4;">ARCHIVE</h1>
          <p class="mt-2" style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted);">
            {{ romsStore.pagination.total }} indexed entries
          </p>
        </div>

        <div class="w-full lg:w-[600px] rounded-md p-3" style="background: rgba(0,0,0,0.35); border: 1px solid rgba(255,184,0,0.08);">
          <div class="flex flex-col sm:flex-row gap-3">
            <div class="flex-1">
              <SearchBar v-model="search" placeholder="Search title or filename" />
            </div>
            <div class="w-full sm:w-52">
              <FilterBar v-model="selectedPlatform" />
            </div>
            <div class="w-full sm:w-44">
              <select
                :value="romsStore.sort.by + ':' + romsStore.sort.dir"
                @change="handleSortChange"
                class="w-full h-full rounded px-3 py-2 text-xs"
                style="background:rgba(0,0,0,0.5); border:1px solid rgba(255,184,0,0.15); color:var(--text-main); font-family:'Share Tech Mono',monospace; cursor:pointer;"
              >
                <option value="title:asc">Title A&#x2192;Z</option>
                <option value="title:desc">Title Z&#x2192;A</option>
                <option value="year:desc">Year &#x2193;</option>
                <option value="year:asc">Year &#x2191;</option>
                <option value="rating:desc">Rating &#x2193;</option>
                <option value="size:desc">Size &#x2193;</option>
                <option value="scrape_status:asc">Unscraped First</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Stats Widget -->
    <StatsWidget class="mb-2" />

    <!-- Active Filters -->
    <div v-if="search || selectedPlatform" class="flex flex-wrap items-center gap-2 text-xs">
      <span style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase;">Filters</span>
      <span v-if="search" class="px-2 py-1 rounded" style="background: rgba(255,184,0,0.08); border: 1px solid rgba(255,184,0,0.2); color: var(--neon-cyan); font-family: 'Share Tech Mono', monospace;">
        "{{ search }}"
      </span>
      <span v-if="selectedPlatform" class="px-2 py-1 rounded" style="background: rgba(0,200,160,0.08); border: 1px solid rgba(0,200,160,0.2); color: var(--neon-purple); font-family: 'Share Tech Mono', monospace;">
        {{ selectedPlatform }}
      </span>
      <button @click="search = ''; selectedPlatform = ''" class="px-2 py-1 rounded transition-all"
              style="color: var(--text-muted); font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;"
              onmouseenter="this.style.color='var(--neon-pink)'" onmouseleave="this.style.color='var(--text-muted)'">
        [CLEAR]
      </button>
    </div>

    <!-- Grid Section -->
    <section>
      <!-- Grid -->
      <div v-if="romsStore.roms.length > 0 || romsStore.loading || romsStore.error" class="space-y-8">
        <div class="library-stage">
          <RomGrid :roms="romsStore.roms" :loading="romsStore.loading" :error="romsStore.error" :skeleton-count="50" @delete="handleDelete" @retry="fetchRoms()" />
        </div>

        <!-- Pagination -->
        <div v-if="!romsStore.loading && !romsStore.error" class="flex justify-center items-center gap-6 py-6">
          <button
            @click="handlePageChange(romsStore.pagination.page - 1)"
            :disabled="romsStore.pagination.page === 1"
            class="btn-nebula-secondary !px-3"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div class="flex items-center gap-2">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase;">Page</span>
            <span class="px-3 py-1.5 rounded" style="font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: var(--neon-cyan); background: rgba(255,184,0,0.07); border: 1px solid rgba(255,184,0,0.2);">
              {{ romsStore.pagination.page }}
            </span>
            <span style="font-family: 'Orbitron', sans-serif; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase;">of {{ romsStore.pagination.totalPages }}</span>
          </div>

          <button
            @click="handlePageChange(romsStore.pagination.page + 1)"
            :disabled="romsStore.pagination.page === romsStore.pagination.totalPages"
            class="btn-nebula-secondary !px-3"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!romsStore.loading && !romsStore.error" class="rounded-lg p-16 text-center" style="background: rgba(11,9,22,0.7); border: 1px dashed rgba(255,184,0,0.1);">
        <div class="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
             style="background: rgba(255,184,0,0.05); border: 1px solid rgba(255,184,0,0.1);">
          <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: rgba(255,184,0,0.3)">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H4a2 2 0 00-2 2v7m18 0v5a2 2 0 01-2 2H4a2 2 0 01-2-2v-5m18 0l-2 3m-16-3l2 3m5 5l1-1m0 0l1 1m-1-1l-1-1m1 1l1-1" />
          </svg>
        </div>
        <h2 style="font-family: 'Press Start 2P', monospace; font-size: 0.9rem; color: var(--text-main); margin-bottom: 10px;">NO GAMES FOUND</h2>
        <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 2rem;">Adjust search or run a scan to index your library.</p>
        <RouterLink to="/scan" class="btn-nebula-primary inline-flex">Open Jobs</RouterLink>
      </div>
    </section>
  </div>
</template>
