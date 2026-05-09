<script setup lang="ts">
defineProps<{
  platformSlug: string
  showIcon?: boolean
  size?: 'sm' | 'md'
}>()

const platformColors: Record<string, { bg: string; glow: string }> = {
  'nintendo-switch': { bg: 'rgba(255,27,141,0.15)', glow: 'rgba(255,27,141,0.5)' },
  'playstation-5':   { bg: 'rgba(0,112,255,0.15)',  glow: 'rgba(0,112,255,0.5)' },
  'playstation-4':   { bg: 'rgba(0,80,220,0.15)',   glow: 'rgba(0,80,220,0.5)' },
  'playstation-3':   { bg: 'rgba(0,60,180,0.15)',   glow: 'rgba(0,60,180,0.5)' },
  'playstation-2':   { bg: 'rgba(0,40,140,0.15)',   glow: 'rgba(0,40,140,0.5)' },
  'playstation':     { bg: 'rgba(0,40,140,0.15)',   glow: 'rgba(0,40,140,0.5)' },
  'xbox-series-x':   { bg: 'rgba(0,180,70,0.15)',   glow: 'rgba(0,180,70,0.5)' },
  'xbox-one':        { bg: 'rgba(0,160,60,0.15)',   glow: 'rgba(0,160,60,0.5)' },
  'xbox-360':        { bg: 'rgba(0,140,50,0.15)',   glow: 'rgba(0,140,50,0.5)' },
  'nintendo-wii-u':  { bg: 'rgba(0,200,220,0.15)',  glow: 'rgba(0,200,220,0.5)' },
  'nintendo-wii':    { bg: 'rgba(160,200,220,0.15)', glow: 'rgba(160,200,220,0.5)' },
  'nintendo-gamecube': { bg: 'rgba(100,60,180,0.15)', glow: 'rgba(100,60,180,0.5)' },
  'nintendo-64':     { bg: 'rgba(180,60,100,0.15)', glow: 'rgba(180,60,100,0.5)' },
  'nintendo-3ds':    { bg: 'rgba(220,60,60,0.15)',  glow: 'rgba(220,60,60,0.5)' },
  'nintendo-ds':     { bg: 'rgba(200,80,80,0.15)',  glow: 'rgba(200,80,80,0.5)' },
  'game-boy-advance':{ bg: 'rgba(120,80,180,0.15)', glow: 'rgba(120,80,180,0.5)' },
  'game-boy-color':  { bg: 'rgba(160,100,200,0.15)', glow: 'rgba(160,100,200,0.5)' },
  'game-boy':        { bg: 'rgba(100,120,100,0.15)', glow: 'rgba(100,120,100,0.5)' },
  'nes':             { bg: 'rgba(180,60,60,0.15)',  glow: 'rgba(180,60,60,0.5)' },
  'snes':            { bg: 'rgba(100,60,180,0.15)', glow: 'rgba(100,60,180,0.5)' },
  'sega-saturn':     { bg: 'rgba(100,100,200,0.15)', glow: 'rgba(100,100,200,0.5)' },
  'sega-dreamcast':  { bg: 'rgba(220,100,60,0.15)', glow: 'rgba(220,100,60,0.5)' },
  'sega-genesis':    { bg: 'rgba(60,60,60,0.25)',   glow: 'rgba(160,160,160,0.5)' },
  'pc':              { bg: 'rgba(60,100,200,0.15)',  glow: 'rgba(60,100,200,0.5)' },
}

const getStyle = (slug: string) => {
  const found = platformColors[slug.toLowerCase()] ?? { bg: 'rgba(0,245,255,0.1)', glow: 'rgba(0,245,255,0.4)' }
  return {
    background: found.bg,
    border: `1px solid ${found.glow.replace('0.5', '0.3')}`,
    color: found.glow.replace('0.5)', '1)').replace('rgba', 'rgb').replace(/, [^,]+\)$/, ')'),
    boxShadow: `inset 0 0 8px ${found.bg}`,
  }
}
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold"
    :style="[getStyle(platformSlug), { fontFamily: '\'Share Tech Mono\', monospace', letterSpacing: '0.05em', textTransform: 'uppercase' }]"
  >
    {{ platformSlug.replace(/-/g, ' ') }}
  </span>
</template>
