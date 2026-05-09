<script setup lang="ts">
const model = defineModel<string>({ default: '' })

withDefaults(defineProps<{
  placeholder?: string
}>(), {
  placeholder: 'Search games...'
})
</script>

<template>
  <div class="relative">
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--text-muted)">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.2-5.2m1.2-5.3a6.5 6.5 0 11-13 0 6.5 6.5 0 0113 0z" />
      </svg>
    </div>
    <input
      v-model="model"
      type="search"
      :placeholder="placeholder"
      class="input-nebula w-full pl-9 pr-9 h-11"
    />
    <button
      v-if="model"
      @click="model = ''"
      class="absolute inset-y-0 right-0 pr-3 flex items-center transition-colors"
      style="color: var(--text-muted)"
      onmouseenter="this.style.color='var(--neon-cyan)'"
      onmouseleave="this.style.color='var(--text-muted)'"
      aria-label="Clear search"
    >
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
