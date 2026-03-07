<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { Resource, Process, Order } from '~/composables/useDashboardData'

const props = defineProps<{ resources: Resource[], processes: Process[], orders: Order[]}>()

// ── Approximated times — fetched separately, keyed by order id ────────────────
const approxTimes  = ref<Map<number, number[]>>(new Map())   // id -> seconds[]
const loadingTimes = ref(false)

const config = useRuntimeConfig()
const base   = config.public.apiBaseUrl
/*
async function fetchApproxTimes() {
  if (!props.resources.length) return
  loadingTimes.value = true

  const results = await Promise.allSettled(
    props.resources.map((resource: { id: number; }) =>
      $fetch<{ approximated_time: number[] }>(
        `${base}/api/resource/approximated_time/${resource.id}/`
      )
    )
  )

  const map = new Map<number, number[]>()
  results.forEach((result: { status: string; value: { approximated_time: number[]; }; }, i: number) => {
    if (result.status === 'fulfilled') {
      map.set(props.resources[i].id, result.value.approximated_time)
    }
  })
  approxTimes.value  = map
  loadingTimes.value = false
}
*/
// Re-fetch whenever orders list changes
//watch(() => props.resources, fetchApproxTimes, { immediate: true })

// Time range options
type RangeKey = '30min' | '1hour' | '1day' | '1week'

const RANGES: Record<RangeKey, { label: string; ms: number }> = {
  '30min': { label: '30 min', ms: 30 * 60 * 1000 },
  '1hour': { label: '1 hour', ms: 60 * 60 * 1000 },
  '1day':  { label: '1 day',  ms: 24 * 60 * 60 * 1000 },
  '1week': { label: '1 week', ms: 7 * 24 * 60 * 60 * 1000 },
}

const selectedRange = ref<RangeKey>('1day')
const halfRangeMs = computed(() => RANGES[selectedRange.value as RangeKey].ms / 2)
const totalRangeMs = computed(() => RANGES[selectedRange.value as RangeKey].ms)

// Live clock — updates every 30 seconds
const now = ref(Date.now())
let ticker: ReturnType<typeof setInterval>
onMounted(()   => { ticker = setInterval(() => { now.value = Date.now() }, 30_000) })
onUnmounted(() => clearInterval(ticker))

// Status colors
const STATUS_COLORS: Record<string, string> = {
  '0': '#8b5cf6',
  '1': '#3b82f6',
  '2': '#f59e0b',
  '3': '#10b981',
}
function statusColor(status: string | number) {
  return STATUS_COLORS[String(status)] ?? '#6b7a90'
}

// Bar geometry
function barGeometry(resource: Resource): { left: number; width: number; label: string; orderId: number }[] {
  const windowStart = now.value - halfRangeMs.value
  const windowEnd   = now.value + halfRangeMs.value

  return props.processes
    .filter((p: Process) => p.resource === resource.id)
    .flatMap((process: Process) => {
      const order = props.orders.find((o: Order) => o.id === process.order)
      if (!order?.start_date) return []

      const startMs = new Date(order.start_date).getTime()
      const endMs   = startMs + process.approximated_time * 1_000

      // skip if fully outside the window
      if (endMs < windowStart || startMs > windowEnd) return []

      const clampedStart = Math.max(startMs, windowStart)
      const clampedEnd   = Math.min(endMs,   windowEnd)

      return [{
        left:    ((clampedStart - windowStart) / totalRangeMs.value) * 100,
        width:   Math.max(((clampedEnd - clampedStart) / totalRangeMs.value) * 100, 0.15),
        label:   `${process.name} · #${order.order_number}`,
        orderId: order.id,
      }]
    })
}

// X-axis ticks
const ticks = computed(() => {
  const intervals: Record<RangeKey, number> = {
    '30min': 6,
    '1hour': 6,
    '1day':  8,
    '1week': 7,
  }
  const n           = intervals[selectedRange.value as RangeKey]
  const stepMs      = totalRangeMs.value / n
  const windowStart = now.value - halfRangeMs.value

  return Array.from({ length: n + 1 }, (_, i) => ({
    label: formatTick(windowStart + i * stepMs),
    pct:   (i / n) * 100,
  }))
})

function formatTick(ms: number): string {
  const d     = new Date(ms)
  const range = selectedRange.value as RangeKey
  if (range === '1week') {
    return d.toLocaleDateString('en-CA', { weekday: 'short', month: 'numeric', day: 'numeric' })
  }
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

// Visible resources (sorted by start_date)
const visibleResources = computed(() => {
  const windowStart = now.value - halfRangeMs.value
  const windowEnd   = now.value + halfRangeMs.value

  return [...props.resources]
    .filter(resource => {
      // get all processes that use this resource
      const resourceProcesses = props.processes.filter((p: Process) => p.resource === resource.id)

      // resource is visible if ANY of its process bars overlap the window
      return resourceProcesses.some((process: Process) => {
        const order = props.orders.find((o: Order) => o.id === process.order)
        if (!order?.start_date) return false

        const startMs = new Date(order.start_date).getTime()
        const endMs   = startMs + process.approximated_time * 1_000

        return endMs >= windowStart && startMs <= windowEnd
      })
    })
    .sort((a, b) => a.id - b.id)
})
</script>

<template>
  <div class="gantt">
    <!-- Range selector -->
    <div class="range-bar">
      <span class="range-label">Range:</span>
      <button
        v-for="(opt, key) in RANGES"
        :key="key"
        class="range-btn"
        :class="{ 'range-btn--active': selectedRange === key }"
        @click="selectedRange = (key as RangeKey)"
      >{{ opt.label }}</button>
    </div>

    <!-- Chart -->
    <div class="chart-area">
      <!-- Label column -->
      <div class="label-col">
        <div v-for="resource in visibleResources" :key="resource.id" class="row-label">
          <span class="row-name">{{ resource.name }}</span>
          <span class="row-type">{{ resource.type.name }}</span>
        </div>
        <div class="row-label row-label--axis" />
      </div>

      <!-- Track column -->
      <div class="track-col">
        <!-- Resource rows -->
        <div
          v-for="resource in visibleResources"
          :key="resource.id"
          class="track-row"
        >
          <!-- Status indicator on the left edge of the track -->
          <div
            class="status-edge"
            :style="{ background: statusColor(resource.status) }"
          />

          <!-- One bar per process -->
          <template v-for="bar in barGeometry(resource)" :key="bar.processId">
            <div
              class="bar"
              :style="{
                left:       `${bar.left}%`,
                width:      `${bar.width}%`,
                background: statusColor(resource.status),
              }"
              :title="bar.label"
            >
              <div class="bar-shimmer" />
              <span v-if="bar.width > 6" class="bar-label">{{ bar.label }}</span>
            </div>
          </template>
        </div>

        <!-- NOW line — always at exactly 50% -->
        <div class="now-line">
          <span class="now-badge">NOW</span>
        </div>

        <!-- Tick axis -->
        <div class="tick-row">
          <div
            v-for="(tick, i) in ticks"
            :key="i"
            class="tick"
            :style="{ left: `${tick.pct}%` }"
          >
            <span class="tick-label">{{ tick.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="visibleResources.length === 0" class="empty">
      No resources active in this range.
    </div>
  </div>
</template>

<style scoped>
.gantt {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  overflow: hidden;
}

/* ── Range selector ──────────────────────────────────────────────────────── */
.range-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.range-label {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.range-btn {
  font-family: 'Rajdhani', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 3px 10px;
  border-radius: 3px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
.range-btn:hover { border-color: rgba(245,158,11,0.4); color: var(--text-secondary); }
.range-btn--active {
  border-color: rgba(245,158,11,0.6);
  background: rgba(245,158,11,0.1);
  color: #f59e0b;
}
.loading-indicator {
  font-size: 10px;
  color: var(--text-muted);
  font-style: italic;
  margin-left: 4px;
}

/* ── Layout ──────────────────────────────────────────────────────────────── */
.chart-area {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
.label-col {
  width: 90px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}
.row-label {
  flex: 1;
  min-height: 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-right: 8px;
  border-bottom: 1px solid var(--border);
}
.row-label--axis { min-height: 24px; flex: none; border-bottom: none; }
.row-name {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.row-num { font-size: 9px; color: var(--text-muted); }

/* ── Tracks ──────────────────────────────────────────────────────────────── */
.track-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  min-width: 0;
}
.track-row {
  flex: 1;
  min-height: 30px;
  position: relative;
  border-bottom: 1px solid var(--border);
  background: var(--bg-input);
}
.track-row:nth-child(even) { background: var(--bg-surface-alt); }

/* ── Bars ────────────────────────────────────────────────────────────────── */
.bar {
  position: absolute;
  top: 4px;
  bottom: 4px;
  border-radius: 3px;
  overflow: hidden;
  opacity: 0.85;
  transition: opacity 0.15s;
  display: flex;
  align-items: center;
  min-width: 3px;
}
.bar:hover { opacity: 1; }
.bar-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.18) 50%, transparent 100%);
  animation: shimmer 2.5s ease-in-out infinite;
}
@keyframes shimmer {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
.bar-label {
  position: relative;
  z-index: 1;
  padding: 0 5px;
  font-size: 9px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
}
.bar-placeholder {
  position: absolute;
  top: 4px;
  bottom: 4px;
  left: 10%;
  right: 10%;
  border-radius: 3px;
  background: var(--border);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 0.8; } }

/* ── Now line ────────────────────────────────────────────────────────────── */
.now-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 24px;
  width: 0;
  border-left: 1.5px dashed #f59e0b;
  pointer-events: none;
  z-index: 10;
}
.now-badge {
  position: absolute;
  top: 2px;
  left: 4px;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #f59e0b;
  background: rgba(245,158,11,0.12);
  padding: 1px 4px;
  border-radius: 2px;
}

/* ── Tick axis ───────────────────────────────────────────────────────────── */
.tick-row {
  height: 24px;
  flex-shrink: 0;
  position: relative;
  border-top: 1px solid var(--border);
}
.tick {
  position: absolute;
  transform: translateX(-50%);
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.tick::before {
  content: '';
  display: block;
  width: 1px;
  height: 4px;
  background: var(--border);
}
.tick-label { font-size: 9px; color: var(--text-muted); white-space: nowrap; margin-top: 1px; }

.empty { color: var(--text-muted); font-size: 11px; text-align: center; padding: 16px; }
</style>