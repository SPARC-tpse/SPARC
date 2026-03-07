<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Process, Order } from '~/composables/useDashboardData'

const props = defineProps<{ processes: Process[], orders: Order[] }>()

// ── Time range options ────────────────────────────────────────────────────────
type RangeKey = '30min' | '1hour' | '1day' | '1week'

const RANGES: Record<RangeKey, { label: string; ms: number }> = {
  '30min': { label: '30 min', ms: 30 * 60 * 1000 },
  '1hour': { label: '1 hour', ms: 60 * 60 * 1000 },
  '1day':  { label: '1 day',  ms: 24 * 60 * 60 * 1000 },
  '1week': { label: '1 week', ms: 7 * 24 * 60 * 60 * 1000 },
}

const selectedRange = ref<RangeKey>('1day')
const halfRangeMs   = computed(() => RANGES[selectedRange.value as RangeKey].ms / 2)
const totalRangeMs  = computed(() => RANGES[selectedRange.value as RangeKey].ms)

// ── Live clock — updates every 30 seconds ─────────────────────────────────────
const now = ref(Date.now())
let ticker: ReturnType<typeof setInterval>
onMounted(()   => { ticker = setInterval(() => { now.value = Date.now() }, 30_000) })
onUnmounted(() => clearInterval(ticker))

// ── Order status colors (bar color is driven by the parent order's status) ────
const STATUS_COLORS: { [key: number]: string } = {
  0: '#8b5cf6',
  1: '#3b82f6',
  2: '#f59e0b',
  3: '#10b981',
}
function statusColor(status: number): string {
  return STATUS_COLORS[status] ?? '#6b7a90'
}

// ── Visible processes filtered by time range, sorted by order id then process id
const visibleProcesses = computed(() => {
  const windowStart = now.value - halfRangeMs.value
  const windowEnd   = now.value + halfRangeMs.value

  return [...props.processes]
    .filter(process => {
      const order = props.orders.find(o => o.id === process.order)
      if (!order?.start_date) return false

      const startMs = new Date(order.start_date).getTime()
      const endMs   = startMs + process.approximated_time * 1_000

      return endMs >= windowStart && startMs <= windowEnd
    })
    .sort((a, b) => {
      // primary sort: order id, secondary: process id
      if (a.order !== b.order) return a.order - b.order
      return a.id - b.id
    })
})

// ── Bar geometry for a single process ────────────────────────────────────────
function processStartMs(process: Process): number | null {
  const order = props.orders.find(o => o.id === process.order)
  if (!order?.start_date) return null

  // get all processes for the same order, sorted by id (insertion order)
  const siblings = props.processes
    .filter(p => p.order === process.order)
    .sort((a, b) => a.id - b.id)

  const orderStartMs = new Date(order.start_date).getTime()

  // sum approximated_time of all processes that come before this one
  let offset = 0
  for (const sibling of siblings) {
    if (sibling.id === process.id) break
    offset += sibling.approximated_time * 1_000
  }

  return orderStartMs + offset
}

function barGeometry(process: Process): { left: number; width: number } | null {
  const startMs = processStartMs(process)
  if (startMs == null) return null

  const windowStart = now.value - halfRangeMs.value
  const windowEnd   = now.value + halfRangeMs.value
  const endMs       = startMs + process.approximated_time * 1_000

  if (endMs < windowStart || startMs > windowEnd) return null

  const clampedStart = Math.max(startMs, windowStart)
  const clampedEnd   = Math.min(endMs,   windowEnd)

  return {
    left:  ((clampedStart - windowStart) / totalRangeMs.value) * 100,
    width: Math.max(((clampedEnd - clampedStart) / totalRangeMs.value) * 100, 0.15),
  }
}

// ── Helper: get the order for a process ──────────────────────────────────────
function getOrder(process: Process): Order | undefined {
  return props.orders.find(o => o.id === process.order)
}

// ── X-axis ticks ──────────────────────────────────────────────────────────────
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
</script>

<template>
  <div class="gantt">
    <!-- ── Range selector ──────────────────────────────────────────────────── -->
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

    <!-- ── Chart ───────────────────────────────────────────────────────────── -->
    <div class="chart-area">
      <!-- Label column -->
      <div class="label-col">
        <div v-for="process in visibleProcesses" :key="process.id" class="row-label">
          <span class="row-name">{{ process.name }}</span>
          <span class="row-order">#{{ getOrder(process)?.order_number ?? process.order }}</span>
        </div>
        <div class="row-label row-label--axis" />
      </div>

      <!-- Track column -->
      <div class="track-col">
        <!-- Process rows -->
        <div
          v-for="process in visibleProcesses"
          :key="process.id"
          class="track-row"
        >
          <template v-if="barGeometry(process)">
            <div
              class="bar"
              :style="{
                left:       `${barGeometry(process)!.left}%`,
                width:      `${barGeometry(process)!.width}%`,
                background: statusColor(getOrder(process)?.status ?? 0),
              }"
              :title="`${process.name} · #${getOrder(process)?.order_number}`"
            >
              <div class="bar-shimmer" />
              <span v-if="barGeometry(process)!.width > 6" class="bar-label">
                {{ process.name }}
              </span>
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

    <div v-if="visibleProcesses.length === 0" class="empty">
      No processes active in this range.
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

/* ── Layout ──────────────────────────────────────────────────────────────── */
.chart-area {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
.label-col {
  width: 100px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}
.row-label {
  flex: 1;
  min-height: 34px;
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
.row-order { font-size: 9px; color: var(--text-muted); }

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
  min-height: 34px;
  position: relative;
  border-bottom: 1px solid var(--border);
  background: var(--bg-input);
}
.track-row:nth-child(even) { background: var(--bg-surface-alt); }

/* ── Bars ────────────────────────────────────────────────────────────────── */
.bar {
  position: absolute;
  top: 5px;
  bottom: 5px;
  border-radius: 3px;
  overflow: hidden;
  opacity: 0.82;
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