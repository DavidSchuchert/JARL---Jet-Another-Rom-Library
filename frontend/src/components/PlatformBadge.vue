<script setup lang="ts">
defineProps<{
  platformSlug: string
  showIcon?: boolean
}>()

const platformIcons: Record<string, string> = {
  'nintendo-switch': '🖥️',
  'playstation-5': '🎮',
  'playstation-4': '🎮',
  'playstation-3': '🎮',
  'playstation-2': '🎮',
  'playstation': '🎮',
  'xbox-series-x': '🎮',
  'xbox-one': '🎮',
  'xbox-360': '🎮',
  'xbox': '🎮',
  'nintendo-wii-u': '🎮',
  'nintendo-wii': '🎮',
  'nintendo-gamecube': '🎮',
  'nintendo-64': '🎮',
  'nintendo-3ds': '🎮',
  'nintendo-ds': '🎮',
  'game-boy-advance': '🎮',
  'game-boy-color': '🎮',
  'game-boy': '🎮',
  'nes': '🎮',
  'snes': '🎮',
  'sega-saturn': '🎮',
  'sega-dreamcast': '🎮',
  'sega-genesis': '🎮',
  'pc': '💻',
  'default': '🎮'
}

const getIcon = (slug: string): string => {
  return platformIcons[slug.toLowerCase()] || platformIcons['default']
}

const getPlatformColor = (slug: string): string => {
  const colors: Record<string, string> = {
    'nintendo-switch': 'bg-red-500',
    'playstation-5': 'bg-blue-500',
    'playstation-4': 'bg-blue-600',
    'playstation-3': 'bg-blue-700',
    'playstation-2': 'bg-blue-800',
    'xbox-series-x': 'bg-green-500',
    'xbox-one': 'bg-green-600',
    'nintendo-3ds': 'bg-red-400',
    'game-boy': 'bg-slate-500',
    'game-boy-color': 'bg-slate-600',
    'game-boy-advance': 'bg-slate-700',
    'nes': 'bg-gray-400',
    'snes': 'bg-gray-500',
    'pc': 'bg-indigo-500'
  }
  return colors[slug.toLowerCase()] || 'bg-slate-600'
}
</script>

<template>
  <span
    class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
    :class="getPlatformColor(platformSlug)"
  >
    <span v-if="showIcon" class="text-sm">{{ getIcon(platformSlug) }}</span>
    <span class="capitalize">{{ platformSlug.replace(/-/g, ' ') }}</span>
  </span>
</template>
