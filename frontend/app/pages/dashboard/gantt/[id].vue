<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const route = useRoute();
const gantt_type = String(route.params.id);

// ─── Config ────────────────────────────────────────────────────────────────
const ROW_HEIGHT = 52
const TIMELINE_PADDING = 80 // px on each side beyond the window

const timeIntervals = [
  { label: '30m', value: '30min', ms: 30 * 60 * 1000 },
  { label: '1h',  value: '1h',   ms: 60 * 60 * 1000 },
  { label: '1d',  value: '1d',   ms: 24 * 60 * 60 * 1000 },
  { label: '1w',  value: '1week',ms: 7 * 24 * 60 * 60 * 1000 },
]

const viewModes = [
  { label: 'Order',    value: 'order',    icon: '📦' },
  { label: 'Resource', value: 'resource', icon: '🔧' },
  { label: 'Process',  value: 'process',  icon: '⚙️' },
]

// ─── State ─────────────────────────────────────────────────────────────────
const selectedInterval = ref('1d')
const selectedView     = ref('order')
const now              = ref(Date.now())
const rawOrders        = ref([])
const chartContainer   = ref(null)
const timelineWrap     = ref(null)
const containerWidth   = ref(900)
const tooltip          = ref({ visible: false, x: 0, y: 0, bar: null })

// ─── Current time string ───────────────────────────────────────────────────
const currentTimeStr = computed(() => {
  return new Date(now.value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
})

// ─── Derived interval MS ──────────────────────────────────────────────────
const intervalMs = computed(() => {
  return timeIntervals.find(i => i.value === selectedInterval.value)?.ms ?? 24 * 60 * 60 * 1000
})

// ─── Timeline bounds ──────────────────────────────────────────────────────
const rangeStart = computed(() => now.value - intervalMs.value)
const rangeEnd   = computed(() => now.value + intervalMs.value)
const totalMs    = computed(() => rangeEnd.value - rangeStart.value)

// ─── Timeline pixel width ─────────────────────────────────────────────────
const timelineWidth = computed(() => containerWidth.value - 180) // subtract row label panel

// ─── Convert timestamp to X ───────────────────────────────────────────────
function tsToX(ts) {
  return ((ts - rangeStart.value) / totalMs.value) * timelineWidth.value
}

const nowX = computed(() => tsToX(now.value))

// ─── Gantt body height ───────────────────────────────────────────────────
const ganttBodyHeight = computed(() => Math.max(visibleRows.value.length * ROW_HEIGHT, 200))

// ─── Time ticks ──────────────────────────────────────────────────────────
const timeTicks = computed(() => {
  const ticks = []
  const ms = intervalMs.value
  // choose a sensible tick step
  let step
  if (ms <= 30 * 60 * 1000)       step = 5  * 60 * 1000   // 5min
  else if (ms <= 60 * 60 * 1000)  step = 10 * 60 * 1000   // 10min
  else if (ms <= 24 * 60 * 60 * 1000) step = 2 * 60 * 60 * 1000 // 2h
  else step = 24 * 60 * 60 * 1000  // 1day

  const start = Math.ceil(rangeStart.value / step) * step
  for (let t = start; t <= rangeEnd.value; t += step) {
    const d = new Date(t)
    let label
    if (ms <= 60 * 60 * 1000) {
      label = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (ms <= 24 * 60 * 60 * 1000) {
      label = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else {
      label = d.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
    ticks.push({ ts: t, x: tsToX(t), label })
  }
  return ticks
})

// ─── Build rows ───────────────────────────────────────────────────────────
const visibleRows = computed(() => {
  const orders = rawOrders.value.filter(o => {
    const s = new Date(o.start_datetime).getTime()
    const e = new Date(o.end_datetime).getTime()
    return e >= rangeStart.value && s <= rangeEnd.value
  })

  if (selectedView.value === 'order') {
    return orders.map(o => {
      const s = new Date(o.start_datetime).getTime()
      const e = new Date(o.end_datetime).getTime()
      const x = tsToX(s)
      const width = tsToX(e) - x
      const status = s > now.value ? 'future' : e < now.value ? 'done' : 'active'
      const durMin = Math.round((e - s) / 60000)
      return {
        id: o.id,
        label: `Order #${o.id}`,
        sub: o.resource ?? '',
        bars: [{
          id: o.id,
          x,
          width,
          label: `#${o.id}`,
          status,
          startStr: new Date(s).toLocaleString(),
          endStr: new Date(e).toLocaleString(),
          duration: durMin < 60 ? `${durMin}m` : `${Math.round(durMin/60*10)/10}h`,
        }]
      }
    })
  }

  if (selectedView.value === 'resource') {
    const groups = {}
    orders.forEach(o => {
      const key = o.resource ?? 'Unassigned'
      if (!groups[key]) groups[key] = { id: key, label: key, sub: '', bars: [] }
      const s = new Date(o.start_datetime).getTime()
      const e = new Date(o.end_datetime).getTime()
      const x = tsToX(s)
      const width = tsToX(e) - x
      const status = s > now.value ? 'future' : e < now.value ? 'done' : 'active'
      groups[key].bars.push({
        id: o.id, x, width, label: `#${o.id}`, status,
        startStr: new Date(s).toLocaleString(),
        endStr: new Date(e).toLocaleString(),
        duration: `${Math.round((e-s)/60000)}m`,
      })
    })
    return Object.values(groups)
  }

  if (selectedView.value === 'process') {
    const groups = {}
    orders.forEach(o => {
      const key = o.process ?? 'General'
      if (!groups[key]) groups[key] = { id: key, label: key, sub: '', bars: [] }
      const s = new Date(o.start_datetime).getTime()
      const e = new Date(o.end_datetime).getTime()
      const x = tsToX(s)
      const width = tsToX(e) - x
      const status = s > now.value ? 'future' : e < now.value ? 'done' : 'active'
      groups[key].bars.push({
        id: o.id, x, width, label: `#${o.id}`, status,
        startStr: new Date(s).toLocaleString(),
        endStr: new Date(e).toLocaleString(),
        duration: `${Math.round((e-s)/60000)}m`,
      })
    })
    return Object.values(groups)
  }

  return []
})

// ─── Tooltip ─────────────────────────────────────────────────────────────
function showTooltip(event, bar) {
  const rect = event.target.getBoundingClientRect()
  const wrapRect = chartContainer.value.getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: rect.left - wrapRect.left + rect.width / 2,
    y: rect.top - wrapRect.top - 8,
    bar,
  }
}
function hideTooltip() {
  tooltip.value.visible = false
}

// ─── Fetch from Django API ────────────────────────────────────────────────
async function fetchData() {
  try {
    const params = new URLSearchParams({
      start: new Date(rangeStart.value).toISOString(),
      end:   new Date(rangeEnd.value).toISOString(),
      view:  selectedView.value,
    })
    const res = await fetch(`/api/orders/?${params}`)
    if (!res.ok) throw new Error('API error')
    rawOrders.value = await res.json()
  } catch {
    // fallback demo data when API unavailable
    rawOrders.value = generateDemoData()
  }
}

function generateDemoData() {
  const resources = ['Machine A', 'Machine B', 'Line 1', 'Line 2', 'Robot Arm']
  const processes = ['Assembly', 'Welding', 'Painting', 'QA', 'Packaging']
  const orders = []
  for (let i = 1; i <= 18; i++) {
    const offset = (Math.random() - 0.5) * 2 * intervalMs.value * 1.2
    const start = now.value + offset
    const dur = intervalMs.value * 0.05 + Math.random() * intervalMs.value * 0.15
    orders.push({
      id: 1000 + i,
      start_datetime: new Date(start).toISOString(),
      end_datetime:   new Date(start + dur).toISOString(),
      resource: resources[i % resources.length],
      process:  processes[i % processes.length],
    })
  }
  return orders
}

// ─── Clock + scroll-to-center ─────────────────────────────────────────────
let clockTimer
onMounted(() => {
  // measure container
  const ro = new ResizeObserver(entries => {
    containerWidth.value = entries[0].contentRect.width
  })
  ro.observe(chartContainer.value)

  fetchData()

  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 1000)

  // scroll timeline so NOW is centered
  setTimeout(() => {
    if (timelineWrap.value) {
      timelineWrap.value.scrollLeft = nowX.value - timelineWrap.value.clientWidth / 2
    }
  }, 100)
})

onUnmounted(() => clearInterval(clockTimer))

watch(selectedInterval, () => {
  setTimeout(() => {
    if (timelineWrap.value) {
      timelineWrap.value.scrollLeft = nowX.value - timelineWrap.value.clientWidth / 2
    }
  }, 50)
})
</script>

<template>
  <div class="gantt-wrapper">
    <!-- Controls -->
    <div class="gantt-controls">
      <div class="control-group">
        <label class="control-label">TIME INTERVAL</label>
        <div class="btn-group">
          <button
            v-for="interval in timeIntervals"
            :key="interval.value"
            :class="['btn-interval', { active: selectedInterval === interval.value }]"
            @click="selectedInterval = interval.value; fetchData()"
          >
            {{ interval.label }}
          </button>
        </div>
      </div>

      <div class="control-group">
        <label class="control-label">VIEW BY</label>
        <div class="btn-group">
          <button
            v-for="view in viewModes"
            :key="view.value"
            :class="['btn-view', { active: selectedView === view.value }]"
            @click="selectedView = view.value; fetchData()"
          >
            <span class="view-icon">{{ view.icon }}</span>
            {{ view.label }}
          </button>
        </div>
      </div>

      <div class="control-group ml-auto">
        <label class="control-label">CURRENT TIME</label>
        <div class="current-time-display">{{ currentTimeStr }}</div>
      </div>
    </div>

    <!-- Chart Area -->
    <div class="gantt-chart" ref="chartContainer">
      <!-- Y-axis labels -->
      <div class="gantt-rows-panel">
        <div class="rows-header">
          <span>{{ selectedView.toUpperCase() }}</span>
        </div>
        <div class="rows-body">
          <div
            v-for="row in visibleRows"
            :key="row.id"
            class="row-label"
            :style="{ height: ROW_HEIGHT + 'px' }"
          >
            <span class="row-label-text" :title="row.label">{{ row.label }}</span>
            <span class="row-sub" v-if="row.sub">{{ row.sub }}</span>
          </div>
        </div>
      </div>

      <!-- Timeline -->
      <div class="gantt-timeline-wrap" ref="timelineWrap">
        <!-- Time ruler -->
        <div class="time-ruler">
          <div
            v-for="tick in timeTicks"
            :key="tick.ts"
            class="time-tick"
            :style="{ left: tick.x + 'px' }"
          >
            <span class="tick-label">{{ tick.label }}</span>
            <span class="tick-line"></span>
          </div>
        </div>

        <!-- Grid + bars -->
        <div class="gantt-body" :style="{ width: timelineWidth + 'px' }">
          <!-- Grid lines -->
          <div
            v-for="tick in timeTicks"
            :key="'grid-' + tick.ts"
            class="grid-line"
            :style="{ left: tick.x + 'px', height: ganttBodyHeight + 'px' }"
          ></div>

          <!-- NOW line -->
          <div
            class="now-line"
            :style="{ left: nowX + 'px', height: ganttBodyHeight + 'px' }"
          >
            <span class="now-label">NOW</span>
          </div>

          <!-- Rows -->
          <div
            v-for="row in visibleRows"
            :key="'row-' + row.id"
            class="gantt-row"
            :style="{ height: ROW_HEIGHT + 'px' }"
          >
            <!-- Bars for this row -->
            <div
              v-for="bar in row.bars"
              :key="bar.id"
              class="gantt-bar"
              :class="bar.status"
              :style="{
                left: bar.x + 'px',
                width: Math.max(bar.width, 4) + 'px',
                top: '8px',
                height: ROW_HEIGHT - 16 + 'px',
              }"
              @mouseenter="showTooltip($event, bar)"
              @mouseleave="hideTooltip"
            >
              <span class="bar-label" v-if="bar.width > 60">{{ bar.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <div
      v-if="tooltip.visible"
      class="gantt-tooltip"
      :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
    >
      <div class="tooltip-title">{{ tooltip.bar?.label }}</div>
      <div class="tooltip-row"><span>Start</span><span>{{ tooltip.bar?.startStr }}</span></div>
      <div class="tooltip-row"><span>End</span><span>{{ tooltip.bar?.endStr }}</span></div>
      <div class="tooltip-row"><span>Duration</span><span>{{ tooltip.bar?.duration }}</span></div>
      <div class="tooltip-status" :class="tooltip.bar?.status">{{ tooltip.bar?.status }}</div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

.gantt-wrapper {
  font-family: 'IBM Plex Sans', sans-serif;
  background: #0d1117;
  border: 1px solid #21262d;
  border-radius: 12px;
  overflow: hidden;
  color: #c9d1d9;
  position: relative;
}

/* ── Controls ─────────────────────────────────────────────────────────── */
.gantt-controls {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 14px 20px;
  background: #161b22;
  border-bottom: 1px solid #21262d;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-group.ml-auto { margin-left: auto; }

.control-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.12em;
  color: #484f58;
  font-weight: 600;
  text-transform: uppercase;
}

.btn-group {
  display: flex;
  gap: 4px;
}

.btn-interval,
.btn-view {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  padding: 5px 12px;
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #8b949e;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-interval:hover,
.btn-view:hover {
  border-color: #388bfd;
  color: #c9d1d9;
}

.btn-interval.active,
.btn-view.active {
  background: #1f3a5f;
  border-color: #388bfd;
  color: #58a6ff;
  font-weight: 600;
}

.view-icon { font-size: 14px; }

.current-time-display {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 16px;
  font-weight: 600;
  color: #f0f6fc;
  letter-spacing: 0.05em;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 4px 12px;
}

/* ── Chart ──────────────────────────────────────────────────────────────── */
.gantt-chart {
  display: flex;
  overflow: hidden;
  min-height: 200px;
}

/* Row labels panel */
.gantt-rows-panel {
  width: 180px;
  flex-shrink: 0;
  border-right: 1px solid #21262d;
  background: #161b22;
  z-index: 2;
}

.rows-header {
  height: 36px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.1em;
  color: #484f58;
  font-weight: 600;
  border-bottom: 1px solid #21262d;
}

.row-label {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 16px;
  border-bottom: 1px solid #161b22;
  background: #0d1117;
}

.row-label-text {
  font-size: 13px;
  font-weight: 500;
  color: #c9d1d9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-sub {
  font-size: 11px;
  color: #484f58;
  font-family: 'IBM Plex Mono', monospace;
}

/* Timeline */
.gantt-timeline-wrap {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
}

.gantt-timeline-wrap::-webkit-scrollbar {
  height: 6px;
}
.gantt-timeline-wrap::-webkit-scrollbar-track { background: #0d1117; }
.gantt-timeline-wrap::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

/* Ruler */
.time-ruler {
  height: 36px;
  position: relative;
  border-bottom: 1px solid #21262d;
  background: #161b22;
}

.time-tick {
  position: absolute;
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translateX(-50%);
}

.tick-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: #484f58;
  padding-top: 6px;
  white-space: nowrap;
}

.tick-line {
  display: block;
  width: 1px;
  height: 8px;
  background: #30363d;
  margin-top: 2px;
}

/* Body */
.gantt-body {
  position: relative;
  min-height: 200px;
}

.grid-line {
  position: absolute;
  top: 0;
  width: 1px;
  background: #161b22;
  border-right: 1px dashed #21262d;
}

/* NOW line */
.now-line {
  position: absolute;
  top: 0;
  width: 2px;
  background: #f78166;
  z-index: 5;
  box-shadow: 0 0 8px #f7816680;
}

.now-label {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  color: #f78166;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

/* Rows */
.gantt-row {
  position: relative;
  border-bottom: 1px solid #161b22;
}

/* Bars */
.gantt-bar {
  position: absolute;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  cursor: pointer;
  transition: filter 0.15s, transform 0.1s;
  overflow: hidden;
}

.gantt-bar:hover {
  filter: brightness(1.25);
  transform: scaleY(1.05);
  z-index: 4;
}

.gantt-bar.active {
  background: linear-gradient(90deg, #1f6feb 0%, #388bfd 100%);
  border: 1px solid #58a6ff;
}

.gantt-bar.future {
  background: linear-gradient(90deg, #1a3a2a 0%, #238636 100%);
  border: 1px solid #2ea043;
}

.gantt-bar.done {
  background: linear-gradient(90deg, #1c1c2e 0%, #2d2d4e 100%);
  border: 1px solid #484f58;
  opacity: 0.7;
}

.bar-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #f0f6fc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Tooltip */
.gantt-tooltip {
  position: absolute;
  background: #1c2128;
  border: 1px solid #388bfd;
  border-radius: 8px;
  padding: 12px 14px;
  z-index: 100;
  transform: translate(-50%, -100%) translateY(-12px);
  pointer-events: none;
  min-width: 180px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}

.tooltip-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 8px;
  color: #f0f6fc;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: #8b949e;
  margin-bottom: 3px;
}

.tooltip-row span:last-child { color: #c9d1d9; }

.tooltip-status {
  margin-top: 8px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-align: center;
  padding: 3px 8px;
  border-radius: 4px;
}

.tooltip-status.active { background: #1f3a5f; color: #58a6ff; }
.tooltip-status.future { background: #1a3a2a; color: #3fb950; }
.tooltip-status.done   { background: #21262d; color: #484f58; }
</style>