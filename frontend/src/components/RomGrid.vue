<script setup lang="ts">
import type { Rom } from '@/api/roms'
import RomCard from './RomCard.vue'

defineProps<{
  roms: Rom[]
}>()

defineEmits<{
  delete: [id: number]
}>()
</script>

<template>
  <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
    <RomCard 
      v-for="rom in roms" 
      :key="rom.id" 
      :rom="rom"
      @delete="$emit('delete', $event)"
    />
  </div>
</template>
