<script setup lang="ts">
import { computed } from 'vue'
import { useAppTheme } from '~/composables/useAppTheme'
import type { Disruption } from '~/composables/useDashboardData'

const props = defineProps<{ disruptions: Disruption[] }>()
const { isDarkMode } = useAppTheme()

const CHART_W = 360
const CHART_H = 200
const PADDING = { top: 16, right: 16, bottom: 40, left: 44 }

const innerW = CHART_W - PADDING.left - PADDING.right
const innerH = CHART_H - PADDING.top - PADDING.bottom

const chartColors = computed(() => ({
  grid: isDarkMode.value ? '#1e2430' : '#d6dfe9',
  axis: isDarkMode.value ? '#2a2d3a' : '#94a3b8',
  text: isDarkMode.value ? '#4a5568' : '#64748b',
  value: '#f59e0b',
}))

const maxFreq = computed(() => Math.max(...props.disruptions.map(disruption => disruption.frequency), 1))

const bars = computed(() => {
  const count = props.disruptions.length
  const barWidth = count ? innerW / count - 8 : 0

  return props.disruptions.map((disruption, index) => {
    const barHeight = (disruption.frequency / maxFreq.value) * innerH

    return {
      ...disruption,
      x: PADDING.left + index * (innerW / count) + 4,
      y: PADDING.top + (innerH - barHeight),
      w: barWidth,
      h: barHeight,
    }
  })
})

const yTicks = computed(() => {
  const max = maxFreq.value
  const step = Math.ceil(max / 4)

  return Array.from({ length: 5 }, (_, index) => ({
    val: index * step,
    y: PADDING.top + innerH - (index * step / max) * innerH,
  })).filter(tick => tick.val <= max + step)
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
      <line
        v-for="tick in yTicks"
        :key="tick.val"
        :x1="PADDING.left"
        :y1="tick.y"
        :x2="CHART_W - PADDING.right"
        :y2="tick.y"
        :stroke="chartColors.grid"
        stroke-width="1"
      />

      <text
        v-for="tick in yTicks"
        :key="`yt-${tick.val}`"
        :x="PADDING.left - 6"
        :y="tick.y + 4"
        :fill="chartColors.text"
        text-anchor="end"
        class="tick-label"
      >
        {{ tick.val }}
      </text>

      <g v-for="bar in bars" :key="bar.duration">
        <rect
          :x="bar.x"
          :y="bar.y"
          :width="bar.w"
          :height="bar.h"
          rx="3"
          fill="url(#barGrad)"
          class="bar"
        />

        <text
          :x="bar.x + bar.w / 2"
          :y="bar.y - 4"
          :fill="chartColors.value"
          text-anchor="middle"
          class="bar-value"
        >
          {{ bar.frequency }}
        </text>

        <text
          :x="bar.x + bar.w / 2"
          :y="PADDING.top + innerH + 18"
          :fill="chartColors.text"
          text-anchor="middle"
          class="tick-label"
        >
          {{ bar.duration }}
        </text>
      </g>

      <line
        :x1="PADDING.left"
        :y1="PADDING.top"
        :x2="PADDING.left"
        :y2="PADDING.top + innerH"
        :stroke="chartColors.axis"
        stroke-width="1"
      />
      <line
        :x1="PADDING.left"
        :y1="PADDING.top + innerH"
        :x2="CHART_W - PADDING.right"
        :y2="PADDING.top + innerH"
        :stroke="chartColors.axis"
        stroke-width="1"
      />

      <defs>
        <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.9" />
          <stop offset="100%" stop-color="#d97706" stop-opacity="0.45" />
        </linearGradient>
      </defs>
    </svg>

    <div class="x-axis-label">Duration</div>
  </div>
</template>

<style scoped>
.disruptions-widget {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-svg {
  width: 100%;
  height: 100%;
  min-height: 0;
  flex: 1;
}

.axis-labels {
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%) rotate(-90deg) translateX(-40%);
  transform-origin: left center;
}

.axis-y-label,
.x-axis-label {
  color: var(--dashboard-text-soft);
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.x-axis-label {
  margin-top: -4px;
  text-align: center;
}

.tick-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
}

.bar-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 600;
}

.bar {
  transition: opacity 0.15s ease;
}

.bar:hover {
  opacity: 0.8;
}
</style>
