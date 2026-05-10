<script setup lang="ts">
import type { Rom } from '@/api/roms'
import RomCard from './RomCard.vue'

withDefaults(defineProps<{
  roms: Rom[]
  loading?: boolean
  error?: string | null
  skeletonCount?: number
}>(), {
  loading: false,
  error: null,
  skeletonCount: 24
})

defineEmits<{ delete: [id: number]; retry: [] }>()
</script>

<template>
  <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">

    <!-- Skeleton loading -->
    <template v-if="loading">
      <div v-for="n in skeletonCount" :key="'sk-' + n" class="cartridge-card" aria-hidden="true">
        <div class="cartridge-shell skeleton-pulse">
          <div class="cartridge-label" style="background:rgba(255,184,0,0.04);"></div>
          <div class="cartridge-meta" style="gap:6px;">
            <div style="height:10px;width:60%;background:rgba(255,184,0,0.08);border-radius:4px;"></div>
            <div style="height:12px;width:90%;background:rgba(255,184,0,0.06);border-radius:4px;"></div>
            <div style="height:10px;width:40%;background:rgba(255,184,0,0.05);border-radius:4px;"></div>
          </div>
          <div class="cartridge-pins" aria-hidden="true">
            <span v-for="pin in 7" :key="pin" :style="{ '--pin-index': pin }"></span>
          </div>
        </div>
      </div>
    </template>

    <!-- Error state -->
    <template v-else-if="error">
      <div class="col-span-full flex flex-col items-center justify-center py-16 gap-4">
        <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color:var(--neon-pink);opacity:0.6">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
        <p style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;color:var(--neon-pink);">{{ error }}</p>
        <button @click="$emit('retry')" class="px-5 py-2 rounded font-bold transition-all"
          style="font-family:'Orbitron',sans-serif;font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;background:rgba(255,53,32,0.08);border:1px solid var(--neon-pink);color:var(--neon-pink);cursor:pointer;">
          RETRY
        </button>
      </div>
    </template>

    <!-- Normal grid -->
    <template v-else>
      <RomCard v-for="(rom, index) in roms" :key="rom.id" :rom="rom" :index="index" @delete="$emit('delete', $event)" />
    </template>
  </div>
</template>

<style scoped>
.skeleton-pulse {
  animation: skeleton-glow 1.5s ease-in-out infinite;
}
@keyframes skeleton-glow {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
