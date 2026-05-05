<script setup lang="ts">
import { computed } from 'vue'
import { useScanStore } from '@/stores/scan'

const scanStore = useScanStore()

const progressPercentage = computed(() => {
  if (scanStore.progress.total_files === 0) return 0
  return Math.round((scanStore.progress.scanned_files / scanStore.progress.total_files) * 100)
})

const statusColor = computed(() => {
  switch (scanStore.scanStatus) {
    case 'running': return 'bg-primary-500'
    case 'completed': return 'bg-green-500'
    case 'failed': return 'bg-red-500'
    default: return 'bg-slate-600'
  }
})

const statusText = computed(() => {
  switch (scanStore.scanStatus) {
    case 'running': return 'Scanning...'
    case 'completed': return 'Scan Complete'
    case 'failed': return 'Scan Failed'
    default: return 'Idle'
  }
})
</script>

<template>
  <div v-if="scanStore.scanStatus !== 'idle'" class="card p-4">
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <span
            class="inline-block w-3 h-3 rounded-full"
            :class="{
              'bg-primary-500 animate-pulse': scanStore.scanStatus === 'running',
              'bg-green-500': scanStore.scanStatus === 'completed',
              'bg-red-500': scanStore.scanStatus === 'failed'
            }"
          ></span>
          <span class="font-medium text-white">{{ statusText }}</span>
        </div>
      </div>
      <span class="text-sm text-slate-400">
        {{ scanStore.progress.scanned_files }} / {{ scanStore.progress.total_files }}
      </span>
    </div>

    <div class="w-full bg-slate-700 rounded-full h-2 mb-3">
      <div
        class="h-2 rounded-full transition-all duration-300"
        :class="statusColor"
        :style="{ width: `${progressPercentage}%` }"
      ></div>
    </div>

    <div v-if="scanStore.progress.current_file" class="text-xs text-slate-400 truncate">
      {{ scanStore.progress.current_file }}
    </div>

    <div v-if="scanStore.progress.errors > 0" class="mt-3 space-y-1">
      <p class="text-xs text-red-400 font-medium">Errors ({{ scanStore.progress.errors }})</p>
    </div>
  </div>
</template>
