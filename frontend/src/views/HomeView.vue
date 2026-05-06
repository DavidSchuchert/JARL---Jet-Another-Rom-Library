<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useRoute, useRouter } from 'vue-router'
import { useRomsStore } from '@/stores/roms'
import RomGrid from '@/components/RomGrid.vue'
import SearchBar from '@/components/SearchBar.vue'
import FilterBar from '@/components/FilterBar.vue'

const romsStore = useRomsStore()
const route = useRoute()
const router = useRouter()
const search = ref('')
const selectedPlatform = ref('')

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
  if (search.value) {
    query.search = search.value
  } else {
    delete query.search
  }
  if (selectedPlatform.value) {
    query.platform = selectedPlatform.value
  } else {
    delete query.platform
  }
  router.replace({ query })
}

watch(search, () => {
  debouncedFetch()
})

watch(selectedPlatform, () => {
  romsStore.setPage(1)
  syncQuery()
  fetchRoms()
})

watch(() => route.query.platform, () => {
  const nextPlatform = getRoutePlatform()
  if (selectedPlatform.value !== nextPlatform) {
    selectedPlatform.value = nextPlatform
  }
})

watch(() => route.query.search, () => {
  const nextSearch = typeof route.query.search === 'string' ? route.query.search : ''
  if (search.value !== nextSearch) {
    search.value = nextSearch
  }
})

const handlePageChange = (page: number) => {
  romsStore.setPage(page)
  fetchRoms()
}

const handleDelete = async (id: number) => {
  if (confirm('Are you sure you want to delete this ROM?')) {
    await romsStore.deleteRom(id)
  }
}
</script>

<template>
  <div class="space-y-6">
    <header class="relative overflow-hidden rounded-lg border border-stone-700/70 bg-[#1a1a17]/85 p-5 shadow-[0_18px_50px_rgba(0,0,0,0.22)]">
      <div class="absolute inset-y-0 right-0 hidden w-1/3 sm:block opacity-70 pointer-events-none">
        <div class="absolute right-10 top-5 h-20 w-28 rounded-lg border border-amber-300/20 bg-stone-950/40 shadow-[inset_0_-16px_30px_rgba(0,0,0,0.35)] rotate-6"></div>
        <div class="absolute right-16 bottom-5 grid w-28 grid-cols-7 gap-1">
          <span v-for="pin in 7" :key="pin" class="h-8 rounded-sm bg-amber-300/25"></span>
        </div>
      </div>

      <div class="relative flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs uppercase tracking-widest text-amber-300 font-bold mb-2">Game library</p>
          <h1 class="text-3xl font-black text-stone-50">Archive</h1>
          <p class="text-sm text-stone-500 mt-2">{{ romsStore.pagination.total }} indexed entries</p>
        </div>

        <div class="glass-card p-3 w-full lg:w-[620px]">
          <div class="flex flex-col sm:flex-row gap-3">
            <div class="flex-1">
              <SearchBar v-model="search" placeholder="Search title or filename" />
            </div>
            <div class="w-full sm:w-56">
              <FilterBar v-model="selectedPlatform" />
            </div>
          </div>
        </div>
      </div>
    </header>

    <div v-if="search || selectedPlatform" class="flex flex-wrap items-center gap-2 text-xs">
      <span class="text-stone-500 font-bold uppercase tracking-widest">Active filters</span>
      <span v-if="search" class="px-2 py-1 rounded-md bg-stone-800 border border-stone-700 text-stone-200 shadow-[inset_0_-6px_12px_rgba(0,0,0,0.18)]">
        Search: {{ search }}
      </span>
      <span v-if="selectedPlatform" class="px-2 py-1 rounded-md bg-stone-800 border border-stone-700 text-amber-300 shadow-[inset_0_-6px_12px_rgba(0,0,0,0.18)]">
        Platform: {{ selectedPlatform }}
      </span>
      <button
        class="px-2 py-1 rounded-md text-stone-400 hover:text-stone-100 hover:bg-stone-800"
        @click="search = ''; selectedPlatform = ''"
      >
        Clear
      </button>
    </div>

    <!-- Main Grid Section -->
    <section>
      <div v-if="romsStore.loading" class="flex flex-col items-center justify-center py-24 gap-4">
        <div class="chip-loader"></div>
        <p class="text-stone-500 font-bold uppercase tracking-widest text-xs">Loading archive</p>
      </div>

      <div v-else-if="romsStore.roms.length > 0" class="space-y-8">
        <div class="library-stage">
          <RomGrid :roms="romsStore.roms" @delete="handleDelete" />
        </div>

        <!-- Pagination -->
        <div class="flex justify-center items-center gap-6 py-8">
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
            <span class="text-xs text-stone-500 font-bold uppercase">Page</span>
            <span class="px-3 py-1 glass-card text-stone-100 font-bold">{{ romsStore.pagination.page }}</span>
            <span class="text-xs text-stone-500 font-bold uppercase">of {{ romsStore.pagination.totalPages }}</span>
          </div>

          <button 
            @click="handlePageChange(romsStore.pagination.page + 1)"
            :disabled="romsStore.pagination.page === romsStore.pagination.totalPages"
            class="btn-nebula-secondary !px-4"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <div v-else class="glass-card p-16 text-center border-dashed border-white/10">
        <div class="w-20 h-20 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-6 text-slate-600">
          <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H4a2 2 0 00-2 2v7m18 0v5a2 2 0 01-2 2H4a2 2 0 01-2-2v-5m18 0l-2 3m-16-3l2 3m5 5l1-1m0 0l1 1m-1-1l-1-1m1 1l1-1" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-stone-50 mb-2">No games found</h2>
        <p class="text-stone-500 mb-8">Adjust search or filters, or run a scan.</p>
        <RouterLink to="/scan" class="btn-nebula-primary inline-flex">Open Jobs</RouterLink>
      </div>
    </section>
  </div>
</template>
