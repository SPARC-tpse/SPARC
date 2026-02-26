<script setup lang="js">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { buildTimelineWindow, normalizeTimelineRange, TIMELINE_RANGE_OPTIONS } from '~/composables/useTimelineRange'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const MS_PER_HOUR = 60 * 60 * 1000
const MS_PER_DAY = 24 * MS_PER_HOUR

const orderStatusMap = { 1: 'Planned', 2: 'Running', 3: 'Paused', 4: 'Done' }
const resourceStatusMap = { 1: 'Offline', 2: 'In Use', 3: 'Available', 4: 'Maintenance' }

const orders = ref([])
const resources = ref([])
const loadError = ref('')
const isLoading = ref(false)
const nowMs = ref(Date.now())
const timelineRangeOptions = TIMELINE_RANGE_OPTIONS
let nowTicker = null
let refreshTicker = null

const activeFocus = computed(() => {
  const raw = String(route.query.focus || 'orders')
  return ['orders', 'process', 'resources'].includes(raw) ? raw : 'orders'
})

const activeTimelineRange = computed(() => normalizeTimelineRange(route.query.range))
const timelineWindow = computed(() => buildTimelineWindow(activeTimelineRange.value, nowMs.value))
const tickStepLabel = computed(() => {
  const hours = timelineWindow.value.tickStepHours
  if (hours === 48) return '2 Tage'
  if (hours === 24) return '1 Tag'
  if (hours === 12) return '12 Stunden'
  if (hours === 2) return '2 Stunden'
  return `${hours} Stunden`
})

function setTimelineRange(value) {
  const normalized = normalizeTimelineRange(value)
  if (normalized === activeTimelineRange.value) return

  navigateTo({
    path: '/dashboard/gantt',
    query: {
      ...route.query,
      focus: activeFocus.value,
      range: normalized
    }
  }, { replace: true })
}

function focusLink(focus) {
  return `/dashboard/gantt?focus=${focus}&range=${activeTimelineRange.value}`
}

const backToDashboardLink = computed(() => `/dashboard?range=${activeTimelineRange.value}`)

function parseDateBoundary(value, endOfDay = false) {
  if (!value) return null

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-').map(Number)
    return endOfDay
      ? new Date(year, month - 1, day, 23, 59, 59, 999).getTime()
      : new Date(year, month - 1, day, 0, 0, 0, 0).getTime()
  }

  const parsed = new Date(value).getTime()
  if (!Number.isFinite(parsed)) return null

  if (!endOfDay) return parsed

  const date = new Date(parsed)
  date.setHours(23, 59, 59, 999)
  return date.getTime()
}

function normalizeOrderStatus(status) {
  if (typeof status === 'number') return orderStatusMap[status] || 'Planned'
  if (typeof status === 'string' && status.trim().length) return status
  return 'Planned'
}

function normalizeResourceStatus(status) {
  if (typeof status === 'number') return resourceStatusMap[status] || 'Offline'
  if (typeof status === 'string' && status.trim().length) return status
  return 'Offline'
}

function normalizeOrder(item) {
  const startDate = parseDateBoundary(item.start_date ?? item.start, false)
  const rawEndDate = parseDateBoundary(item.end_date ?? item.end, true)
  const endDate = startDate !== null
    ? Math.max(rawEndDate ?? startDate + MS_PER_DAY, startDate + MS_PER_HOUR)
    : null

  return {
    ...item,
    name: item.name || `Order ${item.id}`,
    statusLabel: normalizeOrderStatus(item.status),
    startDate,
    endDate,
    processes: Array.isArray(item.processes)
      ? item.processes
      : Array.isArray(item.process)
        ? item.process
        : []
  }
}

function normalizeResource(item) {
  return {
    ...item,
    statusLabel: normalizeResourceStatus(item.status)
  }
}

function setFallbackData() {
  orders.value = [
    {
      id: '1042',
      name: 'Test Order',
      status: 'Running',
      start_date: '2026-02-24',
      end_date: '2026-02-28',
      processes: [
        {
          id: '1042-1',
          name: 'Preparation',
          setup_time_seconds: 1800,
          waiting_time_seconds: 600,
          process_time_seconds: 3600,
          resource: { name: 'Machine A' }
        },
        {
          id: '1042-2',
          name: 'Assembly',
          setup_time_seconds: 1200,
          waiting_time_seconds: 900,
          process_time_seconds: 4200,
          resource: { name: 'Conveyor 3' }
        }
      ]
    },
    {
      id: '1043',
      name: 'Calibration Batch',
      status: 'Planned',
      start_date: '2026-02-27',
      end_date: '2026-03-02',
      processes: [
        {
          id: '1043-1',
          name: 'Calibration',
          setup_time_seconds: 0,
          waiting_time_seconds: 0,
          process_time_seconds: 0,
          resource: { name: 'Machine A' }
        },
        {
          id: '1043-2',
          name: 'Verification',
          setup_time_seconds: 0,
          waiting_time_seconds: 0,
          process_time_seconds: 0,
          resource: { name: 'Robot Arm' }
        }
      ]
    }
  ].map(normalizeOrder)

  resources.value = [
    { id: 'RES-01', name: 'Machine A', status: 'In Use' },
    { id: 'RES-02', name: 'Conveyor 3', status: 'Available' },
    { id: 'RES-03', name: 'Robot Arm', status: 'Maintenance' }
  ].map(normalizeResource)
}

async function fetchData() {
  if (isLoading.value) return
  isLoading.value = true
  loadError.value = ''

  try {
    const [orderData, resourceData] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/order/get`),
      $fetch(`${API_BASE_URL}/api/resource/list`)
    ])

    orders.value = (orderData || [])
      .map(normalizeOrder)
      .sort((a, b) => (a.startDate || 0) - (b.startDate || 0))

    resources.value = (resourceData || []).map(normalizeResource)
  } catch (error) {
    console.error('Detailed timeline data load failed:', error)
    loadError.value = 'Live data could not be loaded. Showing fallback data.'
  } finally {
    isLoading.value = false
  }
}

function orderDateRange(order) {
  if (order.startDate === null || order.endDate === null) return null
  const start = Number(order.startDate)
  const end = Math.max(Number(order.endDate), start + MS_PER_HOUR)
  if (!Number.isFinite(start) || !Number.isFinite(end)) return null
  return { start, end }
}

function processMeasuredSeconds(step) {
  const setup = Number(step.setup_time_seconds || 0)
  const waiting = Number(step.waiting_time_seconds || 0)
  const process = Number(step.process_time_seconds || 0)
  return Math.max(0, setup) + Math.max(0, waiting) + Math.max(0, process)
}

const processAssignments = computed(() => {
  const assignments = []

  orders.value.forEach(order => {
    const range = orderDateRange(order)
    if (!range) return

    const steps = Array.isArray(order.processes) ? order.processes : []
    if (!steps.length) return

    const weights = steps.map(step => {
      const measuredSeconds = processMeasuredSeconds(step)
      return measuredSeconds > 0 ? measuredSeconds : 1
    })

    const totalWeight = weights.reduce((sum, value) => sum + value, 0) || steps.length
    const orderSpan = range.end - range.start
    let cursor = range.start

    steps.forEach((step, index) => {
      const isLast = index === steps.length - 1
      const stepSpan = isLast ? range.end - cursor : (orderSpan * weights[index]) / totalWeight

      const plannedStart = cursor
      const plannedEnd = isLast ? range.end : cursor + stepSpan
      cursor = plannedEnd

      const measuredMs = processMeasuredSeconds(step) * 1000
      let actualStart = null
      let actualEnd = null

      if (measuredMs > 0) {
        actualStart = plannedStart
        actualEnd = plannedStart + measuredMs
      } else if (order.statusLabel === 'Done') {
        actualStart = plannedStart
        actualEnd = plannedEnd
      }

      const resourceName = typeof step.resource === 'string'
        ? step.resource
        : step.resource?.name || 'Unassigned'

      assignments.push({
        id: `process-${order.id}-${step.id || index}`,
        orderId: order.id,
        stepId: step.id || index + 1,
        orderName: order.name,
        stepName: step.name || `Step ${index + 1}`,
        resourceName,
        plannedStart,
        plannedEnd,
        actualStart,
        actualEnd
      })
    })
  })

  return assignments
})

const resourceIdByName = computed(() => {
  const byName = new Map()
  resources.value.forEach(resource => {
    if (!resource?.name) return
    byName.set(resource.name, resource.id)
  })
  return byName
})

const orderTimelineRows = computed(() =>
  orders.value
    .map(order => {
      const range = orderDateRange(order)
      if (!range) return null

      let actualStart = null
      let actualEnd = null

      if (['Running', 'Paused', 'Done'].includes(order.statusLabel)) {
        actualStart = range.start
      }

      if (['Running', 'Paused'].includes(order.statusLabel)) {
        actualEnd = nowMs.value
      } else if (order.statusLabel === 'Done') {
        actualEnd = range.end
      }

      return {
        id: `order-${order.id}`,
        label: `#${order.id} ${order.name}`,
        meta: order.statusLabel,
        segments: [
          {
            id: `order-segment-${order.id}`,
            plannedStart: range.start,
            plannedEnd: range.end,
            actualStart,
            actualEnd,
            label: `${order.name} (${order.statusLabel})`,
            to: `/order/edit/${order.id}`
          }
        ]
      }
    })
    .filter(Boolean)
)

const processTimelineRows = computed(() =>
  [...processAssignments.value]
    .sort((a, b) => a.plannedStart - b.plannedStart)
    .map(item => ({
      id: item.id,
      label: item.stepName,
      meta: `#${item.orderId} | ${item.resourceName}`,
      segments: [
        {
          id: `${item.id}-segment`,
          plannedStart: item.plannedStart,
          plannedEnd: item.plannedEnd,
          actualStart: item.actualStart,
          actualEnd: item.actualEnd,
          label: `${item.orderName} | ${item.stepName}`,
          to: `/order/process-steps/${item.orderId}-${item.stepId}`
        }
      ]
    }))
)

const resourceTimelineRows = computed(() => {
  const grouped = new Map()

  processAssignments.value.forEach(item => {
    const key = item.resourceName || 'Unassigned'
    if (!grouped.has(key)) grouped.set(key, [])
    grouped.get(key).push(item)
  })

  return Array.from(grouped.entries())
    .map(([resourceName, segments]) => {
      const resourceId = resourceIdByName.value.get(resourceName)
      const resourceLink = resourceId ? `/resource/edit/${resourceId}` : '/resource/overview'

      return {
        id: `resource-${resourceName}`,
        label: resourceName,
        meta: `${segments.length} assigned steps`,
        segments: segments
          .sort((a, b) => a.plannedStart - b.plannedStart)
          .map(segment => ({
            id: `${segment.id}-resource`,
            plannedStart: segment.plannedStart,
            plannedEnd: segment.plannedEnd,
            actualStart: segment.actualStart,
            actualEnd: segment.actualEnd,
            label: `#${segment.orderId} ${segment.stepName}`,
            to: resourceLink
          }))
      }
    })
    .sort((a, b) => a.label.localeCompare(b.label))
})

const focusConfig = computed(() => {
  const map = {
    orders: {
      title: 'Order Timeline',
      description: 'Planned windows with live actual overlay.',
      rows: orderTimelineRows.value
    },
    process: {
      title: 'Process Step Timeline',
      description: 'Step schedule and measured process times.',
      rows: processTimelineRows.value
    },
    resources: {
      title: 'Resource Timeline',
      description: 'Machine utilization and overlaps.',
      rows: resourceTimelineRows.value
    }
  }
  return map[activeFocus.value]
})

onMounted(() => {
  setFallbackData()
  fetchData()
  nowTicker = setInterval(() => {
    nowMs.value = Date.now()
  }, 60 * 1000)
  refreshTicker = setInterval(() => {
    fetchData()
  }, 90 * 1000)
})

onUnmounted(() => {
  if (nowTicker) clearInterval(nowTicker)
  if (refreshTicker) clearInterval(refreshTicker)
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Gantt Details"
      :show-reset="false"
      :show-create="false"
    />

    <main class="max-w-6xl mx-auto p-6 space-y-4">
      <section
        class="rounded-xl border p-4 shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-semibold uppercase tracking-[0.2em]" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
              Timeline focus
            </h2>
            <p class="text-xs mt-1" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
              Click any bar to open the related order, process step, or resource.
            </p>
            <p v-if="isLoading" class="text-xs mt-1" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
              Loading live data...
            </p>
            <p v-else-if="loadError" class="text-xs mt-1 text-amber-500">
              {{ loadError }}
            </p>
          </div>
          <NuxtLink
            :to="backToDashboardLink"
            class="px-3 py-2 text-sm rounded-lg border transition-colors"
            :class="isDarkMode
              ? 'border-gray-600 hover:bg-gray-700 text-slate-200'
              : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
          >
            Back to dashboard
          </NuxtLink>
        </div>

        <div class="mt-3 flex flex-wrap items-center gap-2">
          <label class="text-xs font-semibold uppercase tracking-wider" :class="isDarkMode ? 'text-slate-300' : 'text-slate-600'">
            Zeitachse
          </label>
          <select
            :value="activeTimelineRange"
            class="tab-btn min-w-[170px]"
            @change="setTimelineRange($event.target?.value)"
          >
            <option v-for="option in timelineRangeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
          <span class="text-[11px]" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            Tick: {{ tickStepLabel }}
          </span>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <NuxtLink
            :to="focusLink('orders')"
            class="tab-btn"
            :class="activeFocus === 'orders'
              ? (isDarkMode ? 'tab-active-dark' : 'tab-active-light')
              : (isDarkMode ? 'tab-idle-dark' : 'tab-idle-light')"
          >
            Orders
          </NuxtLink>
          <NuxtLink
            :to="focusLink('process')"
            class="tab-btn"
            :class="activeFocus === 'process'
              ? (isDarkMode ? 'tab-active-dark' : 'tab-active-light')
              : (isDarkMode ? 'tab-idle-dark' : 'tab-idle-light')"
          >
            Process Steps
          </NuxtLink>
          <NuxtLink
            :to="focusLink('resources')"
            class="tab-btn"
            :class="activeFocus === 'resources'
              ? (isDarkMode ? 'tab-active-dark' : 'tab-active-light')
              : (isDarkMode ? 'tab-idle-dark' : 'tab-idle-light')"
          >
            Resources
          </NuxtLink>
        </div>
      </section>

      <section
        class="rounded-xl border p-4 shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h3 class="text-base font-semibold">
            {{ focusConfig.title }}
          </h3>
          <span class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            {{ focusConfig.description }}
          </span>
        </div>

        <div class="mt-2 flex flex-wrap items-center gap-4 text-[11px]" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
          <span class="inline-flex items-center gap-1"><i class="legend-swatch planned" />Planned</span>
          <span class="inline-flex items-center gap-1"><i class="legend-swatch actual" :class="isDarkMode ? 'actual-dark' : 'actual-light'" />Actual</span>
          <span class="inline-flex items-center gap-1"><i class="legend-line" :class="isDarkMode ? 'bg-pink-400/80' : 'bg-indigo-500/80'" />Now</span>
        </div>

        <div class="mt-3">
          <GanttTimeline
            :rows="focusConfig.rows"
            :is-dark-mode="isDarkMode"
            :now-ms="nowMs"
            :axis-start-ms="timelineWindow.startMs"
            :axis-end-ms="timelineWindow.endMs"
            :tick-step-hours="timelineWindow.tickStepHours"
            empty-text="No timeline data available for this view."
          />
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dark-mode {
  @apply bg-slate-950 text-slate-100;
}
.light-mode {
  @apply bg-slate-50 text-slate-900;
}
.tab-btn {
  @apply px-3 py-2 text-sm rounded-lg border transition-colors;
}
.tab-active-dark {
  @apply border-pink-500 bg-pink-500/20 text-pink-100;
}
.tab-active-light {
  @apply border-indigo-500 bg-indigo-500/15 text-indigo-700;
}
.tab-idle-dark {
  @apply border-gray-600 hover:bg-gray-700 text-slate-200;
}
.tab-idle-light {
  @apply border-slate-300 hover:bg-slate-200 text-slate-700;
}
.legend-swatch {
  width: 14px;
  height: 8px;
  border-radius: 4px;
  display: inline-block;
}
.legend-swatch.planned {
  border: 1px dashed rgba(100, 116, 139, 0.9);
  background: rgba(148, 163, 184, 0.2);
}
.legend-swatch.actual {
  border: 1px solid;
}
.legend-swatch.actual.actual-dark {
  border-color: rgba(244, 114, 182, 0.9);
  background: rgba(236, 72, 153, 0.35);
}
.legend-swatch.actual.actual-light {
  border-color: rgba(99, 102, 241, 0.9);
  background: rgba(99, 102, 241, 0.35);
}
.legend-line {
  width: 2px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}
</style>
