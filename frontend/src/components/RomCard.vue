<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Rom } from '@/api/roms'
import PlatformBadge from './PlatformBadge.vue'

const props = withDefaults(defineProps<{
  rom: Rom
  index?: number
}>(), {
  index: 0
})

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
    class="group cartridge-card"
    :style="{ '--card-index': index }"
    tabindex="0"
    role="button"
    :aria-label="`Open ${rom.title}`"
    @click="navigateToDetail"
    @keydown.enter="navigateToDetail"
    @keydown.space.prevent="navigateToDetail"
  >
    <div class="cartridge-shell">
      <div class="cartridge-top-slot" aria-hidden="true"></div>
      <div class="cartridge-grip left" aria-hidden="true"></div>
      <div class="cartridge-grip right" aria-hidden="true"></div>

      <div class="cartridge-label">
        <img 
          v-if="rom.cover_url" 
          :src="rom.cover_url" 
          :alt="rom.title"
          class="cartridge-art"
          loading="lazy"
        />
        <div v-else class="cartridge-placeholder">
          <svg class="w-12 h-12 text-stone-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span class="text-[10px] text-stone-400 font-black uppercase tracking-widest">{{ rom.platform_slug }}</span>
        </div>
      </div>

      <div class="cartridge-meta">
        <PlatformBadge :platformSlug="rom.platform_slug" size="sm" />
        <h3 class="cartridge-title line-clamp-2">
          {{ rom.title }}
        </h3>
        <div class="cartridge-id-strip">
          <span class="text-stone-300">{{ rom.year || 'N/A' }}</span>
          <span class="text-[var(--cart-accent)]">{{ rom.region || 'ROM' }}</span>
        </div>
      </div>

      <div class="cartridge-ridges" aria-hidden="true"></div>
      <div class="cartridge-pins" aria-hidden="true">
        <span v-for="pin in 7" :key="pin" :style="{ '--pin-index': pin }"></span>
      </div>

      <button 
        @click.stop="emit('delete', rom.id)"
        class="absolute top-3 right-3 p-2 rounded-md bg-black/60 text-stone-400 hover:text-red-300 opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100 transition-all duration-200 hover:bg-red-500/20"
        aria-label="Delete ROM"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  </div>
</template>
