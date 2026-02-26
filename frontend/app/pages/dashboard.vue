<script setup lang="js">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const editMode = ref(false)
const panelToAdd = ref('')
const dragIndex = ref(null)
const dragOverIndex = ref(null)

const MS_PER_HOUR = 60 * 60 * 1000
const MS_PER_DAY = 24 * MS_PER_HOUR

const orderStatusMap = { 1: 'Planned', 2: 'Running', 3: 'Paused', 4: 'Done' }
const resourceStatusMap = { 1: 'Offline', 2: 'In Use', 3: 'Available', 4: 'Maintenance' }

const orders = ref([])
const resources = ref([])
const disruptions = ref([])
const loadError = ref('')
const isLoading = ref(false)
const nowMs = ref(Date.now())
let nowTicker = null
let refreshTicker = null

const kpis = ref([
  { id: 'kpi-01', name: 'On-time delivery', value: 96, unit: '%', delta: '+2.4%' },
  { id: 'kpi-02', name: 'Daily output', value: 1200, unit: 'pcs', delta: '-1.1%' },
  { id: 'kpi-03', name: 'Cycle time', value: 14.5, unit: 'min', delta: '+0.6%' },
  { id: 'kpi-04', name: 'Scrap rate', value: 3.2, unit: '%', delta: '-0.3%' }
])

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
    startText: item.start_date ?? item.start ?? '',
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

function normalizeDisruption(item) {
  return {
    ...item,
    type: item.type || 'General'
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
    },
    {
      id: '1044',
      name: 'Valve Assembly',
      status: 'Done',
      start_date: '2026-02-21',
      end_date: '2026-02-25',
      processes: [
        {
          id: '1044-1',
          name: 'Cutting',
          setup_time_seconds: 600,
          waiting_time_seconds: 300,
          process_time_seconds: 2400,
          resource: { name: 'Conveyor 3' }
        },
        {
          id: '1044-2',
          name: 'Final Check',
          setup_time_seconds: 450,
          waiting_time_seconds: 200,
          process_time_seconds: 1800,
          resource: { name: 'Machine A' }
        }
      ]
    }
  ].map(normalizeOrder)

  resources.value = [
    { id: 'RES-01', name: 'Machine A', status: 'In Use' },
    { id: 'RES-02', name: 'Conveyor 3', status: 'Available' },
    { id: 'RES-03', name: 'Robot Arm', status: 'Maintenance' }
  ].map(normalizeResource)

  disruptions.value = [
    { id: 'DIS-1234', name: 'Machine Malfunction', start: '2026-02-24T10:00:00', type: 'Error' },
    { id: 'DIS-1235', name: 'Planned Calibration', start: '2026-02-24T14:00:00', type: 'Maintenance' },
    { id: 'DIS-1236', name: 'Sensor Drift', start: '2026-02-25T09:20:00', type: 'Quality' }
  ].map(normalizeDisruption)
}

async function fetchDashboardData() {
  if (isLoading.value) return
  isLoading.value = true
  loadError.value = ''

  try {
    const [orderData, resourceData, disruptionData] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/order/get`),
      $fetch(`${API_BASE_URL}/api/resource/list`),
      $fetch(`${API_BASE_URL}/api/disruption/list`)
    ])

    orders.value = (orderData || [])
      .map(normalizeOrder)
      .sort((a, b) => (a.startDate || 0) - (b.startDate || 0))

    resources.value = (resourceData || []).map(normalizeResource)
    disruptions.value = (disruptionData || []).map(normalizeDisruption)
  } catch (error) {
    console.error('Dashboard data load failed:', error)
    loadError.value = 'Live data could not be loaded. Showing fallback data.'
  } finally {
    isLoading.value = false
  }
}

const panelLibrary = [
  { id: 'order-gantt', title: 'Order plan timeline', type: 'order-gantt', colSpan: 6, rowSpan: 2, link: '/dashboard/gantt?focus=orders' },
  { id: 'process-gantt', title: 'Process plan timeline', type: 'process-gantt', colSpan: 6, rowSpan: 2, link: '/dashboard/gantt?focus=process' },
  { id: 'resource-gantt', title: 'Resource utilization timeline', type: 'resource-gantt', colSpan: 6, rowSpan: 2, link: '/dashboard/gantt?focus=resources' },
  { id: 'orders', title: 'Orders', type: 'orders', colSpan: 6, rowSpan: 2, link: '/order/overview' },
  { id: 'kpis', title: 'KPI list', type: 'kpis', colSpan: 6, rowSpan: 2 },
  { id: 'disruptions', title: 'Disruptions', type: 'disruptions', colSpan: 6, rowSpan: 2, link: '/disruption/overview' },
  { id: 'resources', title: 'Resources', type: 'resources', colSpan: 6, rowSpan: 2, link: '/resource/overview' }
]

const widgets = ref([
  { ...panelLibrary[0] },
  { ...panelLibrary[1] },
  { ...panelLibrary[2] },
  { ...panelLibrary[3] },
  { ...panelLibrary[5] }
])

const availablePanels = computed(() =>
  panelLibrary.filter(panel => !widgets.value.some(widget => widget.id === panel.id))
)

function addPanel() {
  if (!panelToAdd.value) return
  const panel = panelLibrary.find(item => item.id === panelToAdd.value)
  if (!panel) return
  widgets.value.push({ ...panel })
  panelToAdd.value = ''
}

function closePanel(panelId) {
  widgets.value = widgets.value.filter(widget => widget.id !== panelId)
}

function panelStyle(widget) {
  return {
    gridColumn: `span ${widget.colSpan}`,
    gridRow: `span ${widget.rowSpan}`
  }
}

function startDrag(index, event) {
  if (!editMode.value) return
  dragIndex.value = index
  dragOverIndex.value = index
  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(index))
  }
}

function onDragOver(index, event) {
  if (!editMode.value) return
  event.preventDefault()
  dragOverIndex.value = index
}

function onDrop(index) {
  if (!editMode.value || dragIndex.value === null || dragIndex.value === index) return
  const sourceIndex = dragIndex.value
  const updated = [...widgets.value]
  ;[updated[sourceIndex], updated[index]] = [updated[index], updated[sourceIndex]]
  widgets.value = updated
  dragIndex.value = null
  dragOverIndex.value = null
}

function onDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
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
    .slice(0, 24)
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
    .slice(0, 36)
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

function summarizeConcurrency(segments) {
  const normalized = (segments || [])
    .map(segment => ({
      start: Number(segment.plannedStart),
      end: Number(segment.plannedEnd)
    }))
    .filter(segment => Number.isFinite(segment.start) && Number.isFinite(segment.end) && segment.end > segment.start)

  if (!normalized.length) {
    return {
      maxConcurrent: 0,
      idleWindows: 0
    }
  }

  const events = []
  normalized.forEach(segment => {
    events.push({ time: segment.start, delta: 1 })
    events.push({ time: segment.end, delta: -1 })
  })

  events.sort((a, b) => (a.time === b.time ? a.delta - b.delta : a.time - b.time))

  let current = 0
  let maxConcurrent = 0

  events.forEach(event => {
    current += event.delta
    maxConcurrent = Math.max(maxConcurrent, current)
  })

  const sorted = [...normalized].sort((a, b) => a.start - b.start)
  let mergedEnd = sorted[0].end
  let idleWindows = 0

  for (let index = 1; index < sorted.length; index += 1) {
    const segment = sorted[index]
    if (segment.start <= mergedEnd) {
      mergedEnd = Math.max(mergedEnd, segment.end)
      continue
    }

    idleWindows += 1
    mergedEnd = segment.end
  }

  return {
    maxConcurrent,
    idleWindows
  }
}

const orderLoadSummary = computed(() =>
  summarizeConcurrency(orderTimelineRows.value.flatMap(row => row.segments))
)

const resourceLoadSummary = computed(() => {
  let peakConcurrency = 0
  let resourcesWithConflict = 0

  resourceTimelineRows.value.forEach(row => {
    const summary = summarizeConcurrency(row.segments)
    peakConcurrency = Math.max(peakConcurrency, summary.maxConcurrent)
    if (summary.maxConcurrent > 1) resourcesWithConflict += 1
  })

  return {
    peakConcurrency,
    resourcesWithConflict
  }
})

function orderBadge(status) {
  const tones = {
    Running: 'bg-emerald-600 text-emerald-100',
    Planned: 'bg-blue-600 text-blue-100',
    Paused: 'bg-amber-600 text-amber-100',
    Done: 'bg-slate-600 text-slate-100',
    default: 'bg-slate-600 text-slate-100'
  }
  return tones[status] || tones.default
}

function resourceBadge(status) {
  const tones = {
    'In Use': 'bg-emerald-600 text-emerald-100',
    Available: 'bg-blue-600 text-blue-100',
    Maintenance: 'bg-pink-600 text-pink-100',
    Offline: 'bg-slate-600 text-slate-100',
    Broken: 'bg-rose-600 text-rose-100',
    default: 'bg-slate-600 text-slate-100'
  }
  return tones[status] || tones.default
}

function disruptionBadge(type) {
  const tones = {
    Error: 'bg-amber-600 text-amber-100',
    Maintenance: 'bg-indigo-600 text-indigo-100',
    Quality: 'bg-cyan-600 text-cyan-100',
    Material: 'bg-orange-600 text-orange-100',
    General: 'bg-slate-600 text-slate-100',
    default: 'bg-slate-600 text-slate-100'
  }
  return tones[type] || tones.default
}

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDateOnly(value) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

onMounted(() => {
  setFallbackData()
  fetchDashboardData()
  nowTicker = setInterval(() => {
    nowMs.value = Date.now()
  }, 60 * 1000)
  refreshTicker = setInterval(() => {
    fetchDashboardData()
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
      title="Overview"
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
              Dashboard layout
            </h2>
            <p class="text-xs mt-1" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
              Edit mode enables drag, close, and add panels.
            </p>
            <p v-if="isLoading" class="text-xs mt-1" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
              Loading live timeline data...
            </p>
            <p v-else-if="loadError" class="text-xs mt-1 text-amber-500">
              {{ loadError }}
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button
              class="px-3 py-2 text-sm rounded-lg border transition-colors"
              :class="isDarkMode
                ? 'border-gray-600 hover:bg-gray-700 text-slate-200'
                : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
              @click="editMode = !editMode"
            >
              {{ editMode ? 'Finish edit' : 'Edit layout' }}
            </button>
            <div class="flex items-center gap-2">
              <select v-model="panelToAdd" class="input h-10">
                <option disabled value="">Add panel</option>
                <option v-for="panel in availablePanels" :key="panel.id" :value="panel.id">
                  {{ panel.title }}
                </option>
              </select>
              <button
                class="px-3 py-2 text-sm rounded-lg border transition-colors disabled:opacity-50"
                :class="isDarkMode
                  ? 'border-gray-600 hover:bg-gray-700 text-slate-200'
                  : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
                :disabled="!panelToAdd"
                @click="addPanel"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      </section>

      <TransitionGroup name="panel-swap" tag="section" class="dashboard-grid">
        <article
          v-for="(widget, index) in widgets"
          :key="widget.id"
          class="panel"
          :style="panelStyle(widget)"
          :class="[
            isDarkMode ? 'border-gray-700 bg-slate-900 shadow-black' : 'border-slate-200 bg-white shadow-slate-200',
            editMode ? 'cursor-move' : '',
            editMode && dragOverIndex === index
              ? (isDarkMode ? 'ring-2 ring-pink-500' : 'ring-2 ring-indigo-400')
              : ''
          ]"
          :draggable="editMode"
          @dragstart="startDrag(index, $event)"
          @dragover="onDragOver(index, $event)"
          @drop="onDrop(index)"
          @dragend="onDragEnd"
        >
          <div class="panel-header">
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold">{{ widget.title }}</span>
              <span v-if="editMode" class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">Drag</span>
            </div>
            <div class="flex items-center gap-2">
              <NuxtLink
                v-if="widget.link"
                :to="widget.link"
                class="text-xs font-medium"
                :class="isDarkMode ? 'text-pink-200 hover:text-pink-100' : 'text-pink-600 hover:text-pink-800'"
              >
                Open
              </NuxtLink>
              <button
                v-if="editMode"
                class="text-xs px-2 py-1 rounded border transition-colors"
                :class="isDarkMode
                  ? 'border-gray-600 hover:bg-gray-700 text-slate-200'
                  : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
                @click="closePanel(widget.id)"
              >
                Close
              </button>
            </div>
          </div>

          <div class="panel-body space-y-2">
            <div v-if="widget.type === 'orders'" class="space-y-2">
              <div class="grid grid-cols-[1.3fr,0.7fr,0.8fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span>Order</span><span>Status</span><span>Start</span>
              </div>
              <div
                v-for="order in orders.slice(0, 6)"
                :key="order.id"
                class="grid grid-cols-[1.3fr,0.7fr,0.8fr] gap-2 items-center rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <span class="font-medium truncate">{{ order.name }}</span>
                <span class="px-2 py-1 rounded-full text-xs font-semibold w-fit" :class="orderBadge(order.statusLabel)">
                  {{ order.statusLabel }}
                </span>
                <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                  {{ formatDateOnly(order.startText) }}
                </span>
              </div>
              <div v-if="!orders.length" class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                No orders available.
              </div>
            </div>

            <div v-else-if="widget.type === 'kpis'" class="space-y-2">
              <div
                v-for="kpi in kpis"
                :key="kpi.id"
                class="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <div>
                  <div class="font-medium">{{ kpi.name }}</div>
                  <div class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">{{ kpi.unit }}</div>
                </div>
                <div class="text-right">
                  <div class="font-semibold">{{ kpi.value }}</div>
                  <div class="text-xs" :class="kpi.delta.startsWith('+') ? 'text-emerald-500' : 'text-rose-400'">
                    {{ kpi.delta }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="widget.type === 'order-gantt'" class="space-y-2">
              <div class="flex flex-wrap items-center justify-between gap-2 text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                <span>Planned windows with live actual overlay.</span>
                <span>Peak parallel: {{ orderLoadSummary.maxConcurrent }} · Idle gaps: {{ orderLoadSummary.idleWindows }}</span>
              </div>
              <div class="flex flex-wrap items-center gap-4 text-[11px]" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span class="inline-flex items-center gap-1"><i class="legend-swatch planned" />Planned</span>
                <span class="inline-flex items-center gap-1"><i class="legend-swatch actual" :class="isDarkMode ? 'actual-dark' : 'actual-light'" />Actual</span>
                <span class="inline-flex items-center gap-1"><i class="legend-line" :class="isDarkMode ? 'bg-pink-400/80' : 'bg-indigo-500/80'" />Now</span>
              </div>
              <div class="timeline-preview" @click="navigateTo('/dashboard/gantt?focus=orders')">
                <GanttTimeline
                  :rows="orderTimelineRows"
                  :is-dark-mode="isDarkMode"
                  :now-ms="nowMs"
                  empty-text="No orders with a valid time range."
                />
              </div>
            </div>

            <div v-else-if="widget.type === 'process-gantt'" class="space-y-2">
              <div class="flex flex-wrap items-center justify-between gap-2 text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                <span>Step schedule derived from order windows and measured step times.</span>
                <span>{{ processTimelineRows.length }} process steps in current horizon</span>
              </div>
              <div class="timeline-preview" @click="navigateTo('/dashboard/gantt?focus=process')">
                <GanttTimeline
                  :rows="processTimelineRows"
                  :is-dark-mode="isDarkMode"
                  :now-ms="nowMs"
                  empty-text="No process steps linked to current orders."
                />
              </div>
            </div>

            <div v-else-if="widget.type === 'resource-gantt'" class="space-y-2">
              <div class="flex flex-wrap items-center justify-between gap-2 text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                <span>Machine allocation timeline based on assigned process steps.</span>
                <span>Peak overlap: {{ resourceLoadSummary.peakConcurrency }} · Conflict machines: {{ resourceLoadSummary.resourcesWithConflict }}</span>
              </div>
              <div class="timeline-preview" @click="navigateTo('/dashboard/gantt?focus=resources')">
                <GanttTimeline
                  :rows="resourceTimelineRows"
                  :is-dark-mode="isDarkMode"
                  :now-ms="nowMs"
                  empty-text="No resource assignments available for timeline rendering."
                />
              </div>
            </div>

            <div v-else-if="widget.type === 'disruptions'" class="space-y-2">
              <div class="grid grid-cols-[1.2fr,0.7fr,0.9fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span>Disruption</span><span>Type</span><span>Start</span>
              </div>
              <div
                v-for="disruption in disruptions.slice(0, 8)"
                :key="disruption.id"
                class="grid grid-cols-[1.2fr,0.7fr,0.9fr] gap-2 items-center rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <span class="font-medium truncate">{{ disruption.name }}</span>
                <span class="px-2 py-1 rounded-full text-xs font-semibold w-fit" :class="disruptionBadge(disruption.type)">
                  {{ disruption.type }}
                </span>
                <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                  {{ formatDate(disruption.start) }}
                </span>
              </div>
              <div v-if="!disruptions.length" class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                No disruptions available.
              </div>
            </div>

            <div v-else-if="widget.type === 'resources'" class="space-y-2">
              <div class="grid grid-cols-[1.2fr,0.7fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span>Resource</span><span>Status</span>
              </div>
              <div
                v-for="resource in resources.slice(0, 8)"
                :key="resource.id"
                class="grid grid-cols-[1.2fr,0.7fr] gap-2 items-center rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <span class="font-medium truncate">{{ resource.name }}</span>
                <span class="px-2 py-1 rounded-full text-xs font-semibold w-fit" :class="resourceBadge(resource.statusLabel)">
                  {{ resource.statusLabel }}
                </span>
              </div>
              <div v-if="!resources.length" class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                No resources available.
              </div>
            </div>
          </div>
        </article>
      </TransitionGroup>
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
.dashboard-grid {
  @apply grid gap-4;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-auto-rows: 120px;
  grid-auto-flow: dense;
}
.panel {
  @apply rounded-xl border shadow-lg flex flex-col min-h-[220px] transition-colors;
}
.panel-swap-move {
  transition: transform 320ms cubic-bezier(0.2, 0.9, 0.2, 1);
}
.panel-swap-enter-active,
.panel-swap-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}
.panel-swap-enter-from,
.panel-swap-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
.panel-header {
  @apply flex items-center justify-between border-b px-4 py-3;
}
.panel-body {
  @apply flex-1 px-4 pb-4 pt-3 overflow-auto;
}
.dark-mode .panel-header {
  @apply border-gray-700 text-slate-100;
}
.light-mode .panel-header {
  @apply border-slate-200 text-slate-900;
}
.input {
  @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors;
}
.dark-mode .input {
  @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500;
}
.light-mode .input {
  @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500;
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
.timeline-preview {
  @apply rounded-md transition duration-150 cursor-zoom-in;
}
.timeline-preview:hover {
  @apply ring-1;
}
.dark-mode .timeline-preview:hover {
  @apply ring-pink-500/40;
}
.light-mode .timeline-preview:hover {
  @apply ring-indigo-400/50;
}
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
@media (max-width: 768px) {
  .panel {
    grid-column: 1 / -1 !important;
    grid-row: auto !important;
  }
}
</style>

