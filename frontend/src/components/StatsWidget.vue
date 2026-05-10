<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getStats, type Stats } from '@/api/stats'

const STORAGE_KEY = 'jarl_stats_collapsed'

const stats = ref<Stats | null>(null)
const loading = ref(true)
const error = ref(false)
const collapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')

const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
  localStorage.setItem(STORAGE_KEY, String(collapsed.value))
}

onMounted(async () => {
  try {
    stats.value = await getStats()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})

const formatBytes = (bytes: number): string => {
  if (bytes >= 1_099_511_627_776) return (bytes / 1_099_511_627_776).toFixed(1) + ' TB'
  if (bytes >= 1_073_741_824)     return (bytes / 1_073_741_824).toFixed(1) + ' GB'
  if (bytes >= 1_048_576)         return (bytes / 1_048_576).toFixed(1) + ' MB'
  if (bytes >= 1_024)             return (bytes / 1_024).toFixed(1) + ' KB'
  return bytes + ' B'
}

const coveragePct = computed(() =>
  stats.value ? Math.round(stats.value.scrape_coverage * 100) : 0
)

const maxPlatformCount = computed(() =>
  stats.value && stats.value.top_platforms.length > 0
    ? stats.value.top_platforms[0].count
    : 1
)
</script>

<template>
  <div
    v-if="!error"
    class="rounded-lg overflow-hidden"
    style="background: rgba(11,9,22,0.85); border: 1px solid rgba(255,184,0,0.12); box-shadow: 0 8px 32px rgba(0,0,0,0.4);"
  >
    <!-- Header row -->
    <div
      class="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
      style="border-bottom: 1px solid rgba(255,184,0,0.08);"
      @click="toggleCollapsed"
    >
      <span
        style="font-family: 'Orbitron', sans-serif; font-size: 0.62rem; font-weight: 700; letter-spacing: 0.18em; color: var(--neon-cyan); text-transform: uppercase; text-shadow: 0 0 8px rgba(255,184,0,0.4);"
      >
        &#9658; Library Stats
      </span>
      <span
        style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text-muted); text-transform: uppercase;"
      >
        {{ collapsed ? '[expand]' : '[collapse]' }}
      </span>
    </div>

    <!-- Body -->
    <div v-if="!collapsed">
      <!-- Loading -->
      <div
        v-if="loading"
        class="px-4 py-5 text-center"
        style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--text-muted);"
      >
        Loading stats...
      </div>

      <div v-else-if="stats" class="p-4 space-y-4">
        <!-- Top stat cards row -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <!-- Games card -->
          <div
            class="rounded px-4 py-3"
            style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,184,0,0.1);"
          >
            <div
              style="font-family: 'Share Tech Mono', monospace; font-size: 1.5rem; color: var(--neon-cyan); line-height: 1;"
            >
              {{ stats.total_roms.toLocaleString() }}
            </div>
            <div
              class="mt-1"
              style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;"
            >
              Games
            </div>
            <div
              class="mt-1"
              style="font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: var(--text-muted);"
            >
              {{ formatBytes(stats.total_size_bytes) }}
            </div>
          </div>

          <!-- Platforms card -->
          <div
            class="rounded px-4 py-3"
            style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,184,0,0.1);"
          >
            <div
              style="font-family: 'Share Tech Mono', monospace; font-size: 1.5rem; color: var(--neon-cyan); line-height: 1;"
            >
              {{ stats.total_platforms }}
            </div>
            <div
              class="mt-1"
              style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;"
            >
              Platforms
            </div>
          </div>

          <!-- Scrape coverage card -->
          <div
            class="rounded px-4 py-3"
            style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,184,0,0.1);"
          >
            <div
              style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;"
            >
              Scrape Coverage
            </div>
            <div
              class="relative h-3 rounded-full overflow-hidden"
              style="background: rgba(255,255,255,0.06);"
            >
              <div
                class="absolute inset-y-0 left-0 rounded-full transition-all duration-700"
                :style="{
                  width: coveragePct + '%',
                  background: 'var(--neon-cyan)',
                  boxShadow: '0 0 8px rgba(255,184,0,0.5)'
                }"
              />
            </div>
            <div
              class="mt-1"
              style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: var(--neon-cyan);"
            >
              {{ coveragePct }}%
            </div>
          </div>
        </div>

        <!-- Top platforms -->
        <div v-if="stats.top_platforms.length > 0">
          <div
            class="mb-2"
            style="font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em; color: var(--text-muted); text-transform: uppercase;"
          >
            Top Platforms
          </div>
          <div class="space-y-2">
            <div
              v-for="(platform, index) in stats.top_platforms"
              :key="platform.slug"
              class="flex items-center gap-3"
            >
              <div
                class="w-20 shrink-0 text-right truncate"
                style="font-family: 'Share Tech Mono', monospace; font-size: 0.7rem;"
                :style="{ color: index === 0 ? 'var(--neon-pink)' : 'var(--text-muted)' }"
                :title="platform.name"
              >
                {{ platform.name }}
              </div>
              <div class="flex-1 h-2 rounded-full overflow-hidden" style="background: rgba(255,255,255,0.05);">
                <div
                  class="h-full rounded-full"
                  :style="{
                    width: Math.round((platform.count / maxPlatformCount) * 100) + '%',
                    background: index === 0 ? 'var(--neon-pink)' : 'var(--neon-cyan)',
                    boxShadow: index === 0 ? '0 0 6px rgba(255,53,32,0.5)' : '0 0 6px rgba(255,184,0,0.35)'
                  }"
                />
              </div>
              <div
                class="w-10 text-right shrink-0"
                style="font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: var(--text-muted);"
              >
                {{ platform.count }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
