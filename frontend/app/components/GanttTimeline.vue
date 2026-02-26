<script setup lang="js">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  rows: {
    type: Array,
    default: () => []
  },
  isDarkMode: {
    type: Boolean,
    default: true
  },
  nowMs: {
    type: Number,
    default: 0
  },
  emptyText: {
    type: String,
    default: 'No timeline data available.'
  },
  axisStartMs: {
    type: Number,
    default: null
  },
  axisEndMs: {
    type: Number,
    default: null
  },
  tickStepHours: {
    type: Number,
    default: null
  }
})

const BAR_HEIGHT = 10
const LANE_GAP = 5
const ROW_PADDING = 4
const ONE_HOUR_MS = 60 * 60 * 1000
const MIN_BAR_WIDTH_PERCENT = 0.8

const containerRef = ref(null)
const containerWidth = ref(0)
let resizeObserver = null

function toMs(value) {
  if (value === null || value === undefined || value === '') return null
  const date = value instanceof Date ? value : new Date(value)
  const ms = date.getTime()
  return Number.isFinite(ms) ? ms : null
}

function normalizeEnd(startMs, endMs) {
  if (startMs === null || endMs === null) return null
  return endMs <= startMs ? startMs + ONE_HOUR_MS : endMs
}

function assignLanes(segments) {
  const laneEndTimes = []
  return segments.map(segment => {
    let lane = 0
    while (lane < laneEndTimes.length && segment.plannedStart < laneEndTimes[lane]) {
      lane += 1
    }
    laneEndTimes[lane] = segment.plannedEnd
    return { ...segment, lane }
  })
}

const normalizedRows = computed(() =>
  (props.rows || [])
    .map((row, rowIndex) => {
      const sourceSegments = Array.isArray(row.segments) && row.segments.length ? row.segments : [row]
      const normalizedSegments = sourceSegments
        .map((segment, segmentIndex) => {
          const plannedStart = toMs(segment.plannedStart)
          const plannedEndRaw = toMs(segment.plannedEnd)
          const plannedEnd = normalizeEnd(plannedStart, plannedEndRaw)
          if (plannedStart === null || plannedEnd === null) return null

          const actualStart = toMs(segment.actualStart)
          const actualEndRaw = toMs(segment.actualEnd)
          const actualEnd = normalizeEnd(actualStart, actualEndRaw)

          return {
            id: segment.id ?? `${row.id ?? rowIndex}-${segmentIndex}`,
            plannedStart,
            plannedEnd,
            actualStart,
            actualEnd,
            label: segment.label || '',
            to: segment.to || ''
          }
        })
        .filter(Boolean)
        .sort((a, b) => a.plannedStart - b.plannedStart)

      if (!normalizedSegments.length) return null

      const segmentsWithLanes = assignLanes(normalizedSegments)
      const laneCount = Math.max(...segmentsWithLanes.map(item => item.lane + 1), 1)
      const trackHeight = ROW_PADDING * 2 + laneCount * BAR_HEIGHT + (laneCount - 1) * LANE_GAP

      return {
        id: row.id ?? `row-${rowIndex}`,
        label: row.label || '-',
        meta: row.meta || '',
        trackHeight,
        segments: segmentsWithLanes
      }
    })
    .filter(Boolean)
)

const axisRange = computed(() => {
  const customStart = Number(props.axisStartMs)
  const customEnd = Number(props.axisEndMs)

  if (Number.isFinite(customStart) && Number.isFinite(customEnd) && customEnd > customStart) {
    return {
      min: customStart,
      max: customEnd
    }
  }

  const points = [props.nowMs]
  normalizedRows.value.forEach(row => {
    row.segments.forEach(segment => {
      points.push(segment.plannedStart, segment.plannedEnd)
      if (segment.actualStart !== null) points.push(segment.actualStart)
      if (segment.actualEnd !== null) points.push(segment.actualEnd)
    })
  })

  const min = Math.min(...points)
  const max = Math.max(...points)
  const span = Math.max(max - min, ONE_HOUR_MS * 4)
  const pad = Math.max(ONE_HOUR_MS * 6, span * 0.08)

  return {
    min: min - pad,
    max: max + pad
  }
})

const visibleRows = computed(() => {
  const min = axisRange.value.min
  const max = axisRange.value.max

  return normalizedRows.value
    .map(row => {
      const visibleSegments = row.segments.filter(segment =>
        segment.plannedEnd >= min && segment.plannedStart <= max
      )

      if (!visibleSegments.length) return null
      return {
        ...row,
        segments: visibleSegments
      }
    })
    .filter(Boolean)
})

function toPercent(ms) {
  const range = axisRange.value.max - axisRange.value.min || ONE_HOUR_MS
  const clamped = Math.min(Math.max(ms, axisRange.value.min), axisRange.value.max)
  return ((clamped - axisRange.value.min) / range) * 100
}

function buildBarStyle(startMs, endMs, lane) {
  const left = toPercent(startMs)
  const right = toPercent(endMs)
  const rawWidth = Math.max(right - left, MIN_BAR_WIDTH_PERCENT)
  const width = Math.max(0, Math.min(rawWidth, 100 - left))
  const top = ROW_PADDING + lane * (BAR_HEIGHT + LANE_GAP)

  return {
    left: `${left}%`,
    width: `${width}%`,
    top: `${top}px`,
    height: `${BAR_HEIGHT}px`
  }
}

const chartRows = computed(() =>
  visibleRows.value.map(row => ({
    ...row,
    segments: row.segments.map(segment => ({
      ...segment,
      plannedStyle: buildBarStyle(segment.plannedStart, segment.plannedEnd, segment.lane),
      actualStyle: segment.actualStart !== null && segment.actualEnd !== null
        ? buildBarStyle(segment.actualStart, segment.actualEnd, segment.lane)
        : null
    }))
  }))
)

const nowLineStyle = computed(() => ({
  left: `${toPercent(props.nowMs)}%`
}))

function formatTickLabel(ms, fixedStepMs = null) {
  if (fixedStepMs !== null) {
    const diffMs = ms - props.nowMs
    if (Math.abs(diffMs) < Math.max(ONE_HOUR_MS, fixedStepMs / 2)) return 'Jetzt'

    if (fixedStepMs >= 24 * ONE_HOUR_MS) {
      const dayDiff = Math.round(diffMs / (24 * ONE_HOUR_MS))
      return String(dayDiff)
    }

    const hourDiff = Math.round(diffMs / ONE_HOUR_MS)
    return String(hourDiff)
  }

  return new Date(ms).toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const axisTicks = computed(() => {
  const range = axisRange.value.max - axisRange.value.min || ONE_HOUR_MS
  const fixedHours = Number(props.tickStepHours)
  const fixedStepMs = Number.isFinite(fixedHours) && fixedHours > 0 ? fixedHours * ONE_HOUR_MS : null

  if (fixedStepMs !== null) {
    const halfSpanMs = range / 2
    const maxSteps = Math.floor(halfSpanMs / fixedStepMs)
    const ticks = []

    for (let step = -maxSteps; step <= maxSteps; step += 1) {
      const tickMs = props.nowMs + step * fixedStepMs
      const ratio = (tickMs - axisRange.value.min) / range
      ticks.push({
        id: `tick-fixed-${step}`,
        left: `${Math.min(Math.max(ratio, 0), 1) * 100}%`,
        label: formatTickLabel(tickMs, fixedStepMs)
      })
    }

    return ticks
  }

  const tickCount = containerWidth.value < 520 ? 3 : (containerWidth.value < 860 ? 4 : 5)

  return Array.from({ length: tickCount }, (_, index) => {
    const ratio = tickCount === 1 ? 0 : index / (tickCount - 1)
    const ms = axisRange.value.min + range * ratio
    return {
      id: `tick-auto-${index}`,
      left: `${ratio * 100}%`,
      label: formatTickLabel(ms)
    }
  })
})

function updateContainerWidth() {
  if (!containerRef.value) return
  const width = containerRef.value.clientWidth
  if (Number.isFinite(width) && width > 0) {
    containerWidth.value = width
  }
}

onMounted(() => {
  updateContainerWidth()

  if (typeof window === 'undefined' || typeof ResizeObserver === 'undefined') return

  resizeObserver = new ResizeObserver(() => updateContainerWidth())
  if (containerRef.value) resizeObserver.observe(containerRef.value)
})

onBeforeUnmount(() => {
  if (resizeObserver) resizeObserver.disconnect()
})
</script>

<template>
  <div ref="containerRef" class="gantt-container">
    <div
      v-if="!chartRows.length"
      class="gantt-empty"
      :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'"
    >
      {{ emptyText }}
    </div>

    <div v-else class="gantt-scroll">
      <div
        v-for="row in chartRows"
        :key="row.id"
        class="gantt-row"
      >
        <div class="gantt-label" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">
          <div class="font-medium truncate">
            {{ row.label }}
          </div>
          <div v-if="row.meta" class="text-[11px] opacity-70 truncate">
            {{ row.meta }}
          </div>
        </div>

        <div
          class="gantt-track"
          :class="isDarkMode ? 'gantt-track-dark' : 'gantt-track-light'"
          :style="{ height: `${row.trackHeight}px` }"
        >
          <span
            v-for="tick in axisTicks"
            :key="`${row.id}-${tick.id}`"
            class="gantt-slot-line"
            :style="{ left: tick.left }"
          />

          <div
            class="gantt-now"
            :class="isDarkMode ? 'bg-pink-400/80' : 'bg-indigo-500/80'"
            :style="nowLineStyle"
          />

          <template v-for="segment in row.segments" :key="`${segment.id}-planned`">
            <NuxtLink
              v-if="segment.to"
              :to="segment.to"
              class="gantt-bar planned gantt-link"
              :style="segment.plannedStyle"
              :title="segment.label || row.label"
              @click.stop
            />
            <div
              v-else
              class="gantt-bar planned"
              :style="segment.plannedStyle"
              :title="segment.label || row.label"
            />
          </template>

          <template v-for="segment in row.segments" :key="`${segment.id}-actual`">
            <NuxtLink
              v-if="segment.actualStyle && segment.to"
              :to="segment.to"
              class="gantt-bar actual gantt-link"
              :class="isDarkMode ? 'gantt-actual-dark' : 'gantt-actual-light'"
              :style="segment.actualStyle"
              :title="segment.label || row.label"
              @click.stop
            />
            <div
              v-else-if="segment.actualStyle"
              class="gantt-bar actual"
              :class="isDarkMode ? 'gantt-actual-dark' : 'gantt-actual-light'"
              :style="segment.actualStyle"
              :title="segment.label || row.label"
            />
          </template>
        </div>
      </div>

      <div class="gantt-axis" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
        <div />
        <div class="gantt-axis-scale">
          <span
            v-for="tick in axisTicks"
            :key="tick.id"
            class="gantt-axis-tick"
            :style="{ left: tick.left }"
          >
            {{ tick.label }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gantt-container {
  @apply space-y-2;
}
.gantt-scroll {
  @apply space-y-2 overflow-auto;
}
.gantt-row {
  @apply grid items-start gap-3;
  grid-template-columns: minmax(160px, 220px) minmax(0, 1fr);
}
.gantt-label {
  @apply text-xs leading-tight pt-1;
}
.gantt-track {
  @apply relative rounded-lg border overflow-hidden;
}
.gantt-track-dark {
  @apply border-gray-700 bg-gray-800/80;
}
.gantt-track-light {
  @apply border-slate-200 bg-slate-50;
}
.gantt-bar {
  @apply absolute rounded-sm;
}
.gantt-link {
  @apply cursor-pointer transition duration-150 hover:brightness-110;
}
.gantt-bar.planned {
  border: 1px dashed rgba(100, 116, 139, 0.9);
  background: rgba(148, 163, 184, 0.2);
}
.gantt-bar.actual {
  @apply border;
}
.gantt-actual-dark {
  @apply border-pink-400/80 bg-pink-500/40;
}
.gantt-actual-light {
  @apply border-indigo-400/80 bg-indigo-500/40;
}
.gantt-now {
  @apply absolute top-0 bottom-0 w-[2px] z-10;
}
.gantt-slot-line {
  @apply absolute top-0 bottom-0 w-px bg-black/60 pointer-events-none;
}
.gantt-axis {
  @apply grid gap-3;
  grid-template-columns: minmax(160px, 220px) minmax(0, 1fr);
}
.gantt-axis-scale {
  @apply relative h-5;
}
.gantt-axis-tick {
  @apply absolute -translate-x-1/2 text-[10px] whitespace-nowrap;
  top: 0;
}
.gantt-empty {
  @apply text-xs py-6 text-center;
}
@media (max-width: 1024px) {
  .gantt-row {
    grid-template-columns: minmax(130px, 170px) minmax(0, 1fr);
  }
  .gantt-axis {
    grid-template-columns: minmax(130px, 170px) minmax(0, 1fr);
  }
}
@media (max-width: 768px) {
  .gantt-row {
    grid-template-columns: 1fr;
  }
  .gantt-axis {
    grid-template-columns: 1fr;
  }
  .gantt-axis > div:first-child {
    display: none;
  }
}
</style>
