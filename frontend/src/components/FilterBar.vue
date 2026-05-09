<script setup lang="ts">
import { onMounted } from 'vue'
import { useRomsStore } from '@/stores/roms'

const model = defineModel<string>({ default: '' })
const romsStore = useRomsStore()

onMounted(() => {
  if (romsStore.platforms.length === 0) {
    romsStore.fetchPlatforms()
  }
})
</script>

<template>
  <div class="relative">
    <select
      v-model="model"
      class="input-nebula w-full h-11 appearance-none pr-9"
      aria-label="Filter by platform"
    >
      <option value="">All Platforms</option>
      <option v-for="platform in romsStore.platforms" :key="platform.slug" :value="platform.slug">
        {{ platform.name }} ({{ platform.rom_count }})
      </option>
    </select>
    <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--text-muted)">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4 4 4-4" />
      </svg>
    </div>
  </div>
</template>
