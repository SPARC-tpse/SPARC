<script setup lang="ts">
import { computed } from 'vue'
import type { Disruption } from '~/composables/useDashboardData'

const props = defineProps<{ disruptions: Disruption[] }>()

const CHART_W = 360
const CHART_H = 200
const PADDING = { top: 16, right: 16, bottom: 40, left: 44 }

const innerW = CHART_W - PADDING.left - PADDING.right
const innerH = CHART_H - PADDING.top - PADDING.bottom

const maxFreq = computed(() => Math.max(...props.disruptions.map(d => d.frequency), 1))

const bars = computed(() => {
  const n = props.disruptions.length
  const barW = innerW / n - 8
  return props.disruptions.map((d, i) => {
    const barH = (d.frequency / maxFreq.value) * innerH
    return {
      ...d,
      x: PADDING.left + i * (innerW / n) + 4,
      y: PADDING.top + (innerH - barH),
      w: barW,
      h: barH,
    }
  })
})

// Y-axis ticks
const yTicks = computed(() => {
  const max = maxFreq.value
  const step = Math.ceil(max / 4)
  return Array.from({ length: 5 }, (_, i) => ({
    val: i * step,
    y:   PADDING.top + innerH - (i * step / max) * innerH,
  })).filter(t => t.val <= max + step)
})
</script>

<template>
  <div class="disruptions-widget">
    <div class="axis-labels">
      <span class="axis-y-label">Frequency</span>
    </div>
    <svg
      :viewBox="`0 0 ${CHART_W} ${CHART_H}`"
      class="chart-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- Grid lines -->
      <line
        v-for="t in yTicks"
        :key="t.val"
        :x1="PADDING.left" :y1="t.y"
        :x2="CHART_W - PADDING.right" :y2="t.y"
        stroke="#1e2430" stroke-width="1"
      />

      <!-- Y axis ticks -->
      <text
        v-for="t in yTicks"
        :key="`yt-${t.val}`"
        :x="PADDING.left - 6" :y="t.y + 4"
        text-anchor="end"
        class="tick-label"
      >{{ t.val }}</text>

      <!-- Bars -->
      <g v-for="bar in bars" :key="bar.duration">
        <rect
          :x="bar.x" :y="bar.y"
          :width="bar.w" :height="bar.h"
          rx="3"
          fill="url(#barGrad)"
          class="bar"
        />
        <!-- Value label on bar -->
        <text
          :x="bar.x + bar.w / 2"
          :y="bar.y - 4"
          text-anchor="middle"
          class="bar-value"
        >{{ bar.frequency }}</text>

        <!-- X axis label -->
        <text
          :x="bar.x + bar.w / 2"
          :y="PADDING.top + innerH + 18"
          text-anchor="middle"
          class="tick-label"
        >{{ bar.duration }}</text>
      </g>

      <!-- Axes -->
      <line
        :x1="PADDING.left" :y1="PADDING.top"
        :x2="PADDING.left" :y2="PADDING.top + innerH"
        stroke="#2a2d3a" stroke-width="1"
      />
      <line
        :x1="PADDING.left" :y1="PADDING.top + innerH"
        :x2="CHART_W - PADDING.right" :y2="PADDING.top + innerH"
        stroke="#2a2d3a" stroke-width="1"
      />

      <!-- Gradient def -->
      <defs>
        <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#f59e0b" stop-opacity="0.9"/>
          <stop offset="100%" stop-color="#d97706" stop-opacity="0.4"/>
        </linearGradient>
      </defs>
    </svg>
    <div class="x-axis-label">Duration</div>
  </div>
</template>

<style scoped>
.disruptions-widget {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}
.chart-svg {
  width: 100%;
  height: 100%;
  flex: 1;
  min-height: 0;
}
.axis-labels {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) rotate(-90deg) translateX(-40%);
  transform-origin: left center;
}
.axis-y-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #4a5568;
}
.x-axis-label {
  text-align: center;
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #4a5568;
  margin-top: -4px;
}
.tick-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  fill: #4a5568;
}
.bar-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  fill: #f59e0b;
  font-weight: 600;
}
.bar {
  transition: opacity 0.15s;
}
.bar:hover { opacity: 0.8; }
</style>
