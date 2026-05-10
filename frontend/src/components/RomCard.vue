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
  toggleFavorite: [id: number]
  togglePlayed: [id: number]
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
          <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--cart-accent); opacity: 0.5">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span style="font-family: 'Share Tech Mono', monospace; font-size: 9px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--cart-accent); opacity: 0.7">{{ rom.platform_slug }}</span>
        </div>
      </div>

      <div class="cartridge-meta">
        <PlatformBadge :platformSlug="rom.platform_slug" />
        <h3 class="cartridge-title line-clamp-2">{{ rom.title }}</h3>
        <div class="cartridge-id-strip">
          <span style="color: var(--text-muted)">{{ rom.year || 'N/A' }}</span>
          <span style="color: var(--cart-accent)">{{ rom.region || 'ROM' }}</span>
        </div>
      </div>

      <div class="cartridge-ridges" aria-hidden="true"></div>
      <div class="cartridge-pins" aria-hidden="true">
        <span v-for="pin in 7" :key="pin" :style="{ '--pin-index': pin }"></span>
      </div>

      <!-- Favorite + Played buttons (top-left) -->
      <div class="absolute top-3 left-3 flex flex-col gap-1">
        <button
          @click.stop="emit('toggleFavorite', rom.id)"
          class="p-1.5 rounded transition-all duration-200"
          :class="rom.is_favorite ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100'"
          :style="rom.is_favorite
            ? 'background: rgba(255,27,141,0.2); color: var(--neon-pink); border: 1px solid rgba(255,27,141,0.5); box-shadow: 0 0 8px rgba(255,27,141,0.3);'
            : 'background: rgba(0,0,0,0.7); color: var(--text-muted); border: 1px solid rgba(255,255,255,0.08);'"
          aria-label="Toggle Favorite"
        >
          <svg class="w-3.5 h-3.5" :fill="rom.is_favorite ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>
        <button
          @click.stop="emit('togglePlayed', rom.id)"
          class="p-1.5 rounded transition-all duration-200"
          :class="rom.is_played ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100'"
          :style="rom.is_played
            ? 'background: rgba(0,200,100,0.2); color: var(--neon-green); border: 1px solid rgba(0,200,100,0.5); box-shadow: 0 0 8px rgba(0,200,100,0.3);'
            : 'background: rgba(0,0,0,0.7); color: var(--text-muted); border: 1px solid rgba(255,255,255,0.08);'"
          aria-label="Toggle Played"
        >
          <svg class="w-3.5 h-3.5" :fill="rom.is_played ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>

      <!-- Delete button -->
      <button
        @click.stop="emit('delete', rom.id)"
        class="absolute top-3 right-3 p-1.5 rounded opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100 transition-all duration-200"
        style="background: rgba(0,0,0,0.7); color: var(--text-muted); border: 1px solid rgba(255,255,255,0.08);"
        onmouseenter="this.style.color='var(--neon-pink)';this.style.background='rgba(255,27,141,0.15)';this.style.borderColor='rgba(255,27,141,0.3)';"
        onmouseleave="this.style.color='var(--text-muted)';this.style.background='rgba(0,0,0,0.7)';this.style.borderColor='rgba(255,255,255,0.08)';"
        aria-label="Delete ROM"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  </div>
</template>
