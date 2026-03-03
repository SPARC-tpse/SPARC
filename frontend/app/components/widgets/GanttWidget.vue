<script setup lang="ts">
import type { GanttItem } from '~/composables/useDashboardData'

defineProps<{
  items: GanttItem[]
  label?: string
}>()

// Simple time markers
const timeMarkers = ['0%', '25%', '50%', '75%', '100%']
</script>

<template>
  <div class="gantt-widget">
    <!-- Time axis header -->
    <div class="gantt-header">
      <div class="gantt-name-col" />
      <div class="gantt-timeline-col">
        <div class="time-markers">
          <span v-for="m in timeMarkers" :key="m" class="time-mark">{{ m }}</span>
        </div>
      </div>
    </div>

    <!-- Rows -->
    <div class="gantt-rows">
      <div v-for="item in items" :key="item.id" class="gantt-row">
        <div class="gantt-row-name" :title="item.name">
          {{ item.name }}
        </div>
        <div class="gantt-row-track">
          <!-- Background grid -->
          <div
            v-for="n in 4"
            :key="n"
            class="track-grid-line"
            :style="{ left: `${(n - 1) * 25}%` }"
          />
          <!-- Bar -->
          <div
            class="gantt-bar"
            :style="{
              left:       `${item.start}%`,
              width:      `${item.duration}%`,
              background: item.color,
            }"
            :title="`${item.name} · ${item.status}`"
          >
            <div class="bar-shimmer" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="items.length === 0" class="empty">No data</div>

    <!-- Legend hint -->
    <div v-if="label" class="gantt-footer">
      <span>{{ label }}</span>
    </div>
  </div>
</template>

<style scoped>
.gantt-widget {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
  font-family: 'JetBrains Mono', monospace;
}

.gantt-header {
  display: flex;
  gap: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #1e2430;
  flex-shrink: 0;
}
.gantt-name-col { width: 80px; flex-shrink: 0; }
.gantt-timeline-col { flex: 1; }
.time-markers {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: #3a4558;
  letter-spacing: 0;
}

.gantt-rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  flex: 1;
}

.gantt-row {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 24px;
}

.gantt-row-name {
  width: 80px;
  flex-shrink: 0;
  font-size: 11px;
  color: #8a9bb0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gantt-row-track {
  flex: 1;
  height: 20px;
  background: #0a0c11;
  border-radius: 3px;
  position: relative;
  overflow: hidden;
  border: 1px solid #1a1e27;
}

.track-grid-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: #1a1e27;
}

.gantt-bar {
  position: absolute;
  top: 3px;
  bottom: 3px;
  border-radius: 2px;
  min-width: 4px;
  overflow: hidden;
  transition: opacity 0.15s;
  opacity: 0.85;
}
.gantt-bar:hover { opacity: 1; }

.bar-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%);
  animation: shimmer 2.5s ease-in-out infinite;
}
@keyframes shimmer {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}

.gantt-footer {
  padding-top: 4px;
  border-top: 1px solid #1e2430;
  font-size: 9px;
  color: #3a4558;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  flex-shrink: 0;
}

.empty {
  color: #4a5568;
  font-size: 12px;
  padding: 8px;
}
</style>
