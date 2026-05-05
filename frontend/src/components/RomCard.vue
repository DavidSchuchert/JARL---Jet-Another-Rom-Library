<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Rom } from '@/api/roms'
import PlatformBadge from './PlatformBadge.vue'

const props = defineProps<{
  rom: Rom
}>()

const emit = defineEmits<{
  delete: [id: number]
}>()

const router = useRouter()

const navigateToDetail = () => {
  router.push(`/roms/${props.rom.id}`)
}
</script>

<template>
  <div 
    class="group poster-card"
    @click="navigateToDetail"
  >
    <!-- Background Image -->
    <div class="absolute inset-0 bg-slate-800">
      <img 
        v-if="rom.cover_url" 
        :src="rom.cover_url" 
        :alt="rom.title"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 text-center">
        <svg class="w-12 h-12 text-slate-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span class="text-xs text-slate-500 font-bold uppercase tracking-widest">{{ rom.platform_slug }}</span>
      </div>
    </div>

    <!-- Overlays -->
    <div class="poster-glow"></div>
    <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent opacity-80 transition-opacity duration-150"></div>

    <!-- Content -->
    <div class="absolute inset-x-0 bottom-0 p-4">
      <div class="flex flex-col gap-1.5">
        <PlatformBadge :platformSlug="rom.platform_slug" size="sm" />
        <h3 class="text-sm font-bold text-white leading-tight line-clamp-2 drop-shadow-lg">
          {{ rom.title }}
        </h3>
        <div class="flex items-center justify-between mt-1">
          <span class="text-[10px] text-slate-400 font-bold">{{ rom.year || 'N/A' }}</span>
          <span class="text-[10px] text-amber-300 font-black uppercase">{{ rom.region || '' }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <button 
      @click.stop="emit('delete', rom.id)"
      class="absolute top-2 right-2 p-2 rounded-md bg-black/55 text-stone-400 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
      aria-label="Delete ROM"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    </button>
  </div>
</template>
