<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getPlatforms, type Platform } from '@/api/platforms'
import PlatformBadge from '@/components/PlatformBadge.vue'

const platforms = ref<Platform[]>([])
const loading = ref(true)

const fetchPlatforms = async () => {
  loading.value = true
  try {
    platforms.value = await getPlatforms()
  } catch (e) {
    console.error('Failed to fetch platforms:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchPlatforms)
</script>

<template>
  <div class="space-y-6">
    <header>
      <p class="text-xs uppercase tracking-widest text-amber-300 font-bold mb-2">Systems with games</p>
      <h1 class="text-3xl font-black text-stone-50">Platforms</h1>
      <p class="text-stone-500 text-sm mt-2">Only systems that currently have indexed games are shown.</p>
    </header>

    <div v-if="loading" class="flex flex-col items-center justify-center py-24 gap-4">
      <div class="w-10 h-10 border-4 border-stone-700 border-t-amber-400 rounded-full animate-spin"></div>
      <p class="text-stone-500 font-bold uppercase tracking-widest text-xs">Loading platforms</p>
    </div>

    <div v-else-if="platforms.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div 
        v-for="platform in platforms" 
        :key="platform.id"
        class="glass-card group hover:border-amber-400/70 transition-colors duration-150 cursor-pointer"
        @click="$router.push(`/?platform=${platform.slug}`)"
      >
        <div class="p-6 flex items-center justify-between gap-5">
          <div class="space-y-4 min-w-0">
            <PlatformBadge :platformSlug="platform.slug" size="md" />
            <div>
              <h3 class="text-xl font-black text-stone-50 tracking-normal group-hover:text-amber-300 transition-colors">{{ platform.name }}</h3>
              <p class="text-xs text-stone-500 font-bold uppercase tracking-widest">{{ platform.family || 'Unknown' }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-3xl font-black text-stone-50">{{ platform.rom_count }}</span>
              <span class="text-[10px] text-stone-500 uppercase font-black tracking-widest mt-2">games</span>
            </div>
          </div>
          
          <div class="w-20 h-20 rounded-md bg-stone-900 flex items-center justify-center border border-stone-700 group-hover:border-amber-400/40 transition-colors">
            <svg class="w-10 h-10 text-stone-700 group-hover:text-amber-300/60 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
        </div>
        <div class="h-1 bg-amber-400/80"></div>
      </div>
    </div>

    <div v-else class="glass-card p-10 text-center">
      <h2 class="text-xl font-bold text-stone-50">No platforms with games yet</h2>
      <p class="text-stone-500 mt-2">Run a scan to index your library.</p>
    </div>
  </div>
</template>
