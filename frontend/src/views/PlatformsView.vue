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

const platformAccents = [
  { color: 'var(--neon-amber)',  glow: 'rgba(255,184,0,0.25)',  border: 'rgba(255,184,0,0.3)' },
  { color: 'var(--neon-orange)', glow: 'rgba(255,96,0,0.25)',   border: 'rgba(255,96,0,0.3)' },
  { color: 'var(--neon-teal)',   glow: 'rgba(0,200,160,0.25)',  border: 'rgba(0,200,160,0.3)' },
  { color: 'var(--neon-green)',  glow: 'rgba(40,208,96,0.25)',  border: 'rgba(40,208,96,0.3)' },
  { color: 'var(--neon-red)',    glow: 'rgba(255,53,32,0.25)',  border: 'rgba(255,53,32,0.3)' },
  { color: 'var(--neon-yellow)', glow: 'rgba(255,229,0,0.25)',  border: 'rgba(255,229,0,0.3)' },
]

const getAccent = (i: number) => platformAccents[i % platformAccents.length]
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <header>
      <p style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.18em; color: var(--neon-cyan); text-transform: uppercase; text-shadow: 0 0 8px rgba(255,184,0,0.5); margin-bottom: 8px;">
        &#9658; Systems Online
      </p>
      <h1 style="font-family: 'Press Start 2P', monospace; font-size: 1.4rem; color: var(--text-main); line-height: 1.4;">PLATFORMS</h1>
      <p class="mt-2" style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted);">
        Only systems with indexed games are shown.
      </p>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24 gap-5">
      <div class="chip-loader"></div>
      <p style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.2em; color: var(--text-muted); text-transform: uppercase;">Loading Platforms</p>
    </div>

    <!-- Grid -->
    <div v-else-if="platforms.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="(platform, i) in platforms"
        :key="platform.id"
        class="platform-card group"
        :style="{
          '--p-color': getAccent(i).color,
          '--p-glow':  getAccent(i).glow,
          '--p-border': getAccent(i).border,
        }"
        @click="$router.push(`/?platform=${platform.slug}`)"
      >
        <div class="platform-card-inner p-5 flex items-center justify-between gap-4">
          <div class="space-y-3 min-w-0">
            <PlatformBadge :platformSlug="platform.slug" />

            <div>
              <h3 class="platform-name">{{ platform.name }}</h3>
              <p style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 600; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase; margin-top: 3px;">
                {{ platform.family || 'Unknown Family' }}
              </p>
            </div>

            <div class="flex items-end gap-2">
              <span class="platform-count">{{ platform.rom_count }}</span>
              <span style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase; padding-bottom: 3px;">GAMES</span>
            </div>
          </div>

          <div class="platform-icon-box">
            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--p-color); opacity: 0.6; transition: all 0.2s;">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
        </div>

        <!-- Accent bar at bottom -->
        <div class="h-0.5 transition-all duration-300"
             :style="{ background: `linear-gradient(90deg, var(--p-color), transparent)`, opacity: 0.6 }"></div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="rounded-lg p-12 text-center" style="background: rgba(11,9,22,0.7); border: 1px dashed rgba(255,184,0,0.1);">
      <h2 style="font-family: 'Press Start 2P', monospace; font-size: 0.9rem; color: var(--text-main); margin-bottom: 10px;">NO PLATFORMS</h2>
      <p style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--text-muted);">Run a scan to index your library.</p>
    </div>
  </div>
</template>

<style scoped>
.platform-card {
  position: relative;
  border-radius: 0.5rem;
  overflow: hidden;
  cursor: pointer;
  background: rgba(12, 10, 26, 0.92);
  border: 1px solid rgba(255,255,255,0.06);
  transition: all 0.25s ease;
}
.platform-card:hover {
  border-color: var(--p-border);
  box-shadow: 0 0 24px var(--p-glow), 0 12px 40px rgba(0,0,0,0.4);
  transform: translateY(-2px);
}
.platform-card:hover .platform-name {
  color: var(--p-color);
  text-shadow: 0 0 10px var(--p-glow);
}
.platform-card:hover svg {
  opacity: 1 !important;
  filter: drop-shadow(0 0 6px var(--p-glow));
}
.platform-card-inner {
  position: relative;
}
.platform-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--text-main);
  transition: all 0.2s;
  letter-spacing: 0.02em;
}
.platform-count {
  font-family: 'Press Start 2P', monospace;
  font-size: 1.4rem;
  color: var(--p-color);
  text-shadow: 0 0 12px var(--p-glow);
}
.platform-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
  transition: all 0.25s;
}
.platform-card:hover .platform-icon-box {
  border-color: var(--p-border);
  background: color-mix(in srgb, var(--p-color) 6%, transparent);
}
</style>
