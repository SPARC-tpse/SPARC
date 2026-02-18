<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Dashboard · Overview',
    showReset: false,
    showCreate: false,
  },
})

const { isDarkMode } = useTheme()

const editMode = ref(false)
const panelToAdd = ref('')
const dragIndex = ref(null)
const dragOverIndex = ref(null)
const disruptionChart = {
  width: 100,
  height: 100,
  leftPad: 16,
  rightPad: 6,
  topPad: 8,
  bottomPad: 18,
  gap: 4
}

const orders = ref([
  { id: 'ORD-1042', name: 'Test Order', status: 'Running', start: '2025-11-27' },
  { id: 'ORD-1043', name: 'Calibration Batch', status: 'Planned', start: '2025-11-29' },
  { id: 'ORD-1044', name: 'Valve Assembly', status: 'Paused', start: '2025-11-30' }
])

const resources = ref([
  { id: 'RES-01', name: 'Machine A', status: 'Online' },
  { id: 'RES-02', name: 'Conveyor 3', status: 'Idle' },
  { id: 'RES-03', name: 'Robot Arm', status: 'Maintenance' }
])

const disruptions = ref([
  { id: 'DIS-1234', name: 'Machine Malfunction', start: '2025-12-27T10:00', type: 'Error' },
  { id: 'DIS-1235', name: 'Planned Calibration', start: '2025-12-27T14:00', type: 'Maintenance' },
  { id: 'DIS-1236', name: 'Sensor Drift', start: '2025-12-28T09:20', type: 'Quality' },
  { id: 'DIS-1237', name: 'Material Shortage', start: '2025-12-28T13:30', type: 'Material' },
  { id: 'DIS-1238', name: 'Line Stop', start: '2025-12-28T16:10', type: 'Error' }
])

const kpis = ref([
  { id: 'kpi-01', name: 'KPI 1', value: 96, unit: '%', delta: '+2.4%' },
  { id: 'kpi-02', name: 'KPI 2', value: 1200, unit: 'pcs', delta: '-1.1%' },
  { id: 'kpi-03', name: 'KPI 3', value: 14.5, unit: 'min', delta: '+0.6%' },
  { id: 'kpi-04', name: 'KPI 4', value: 3.2, unit: '%', delta: '-0.3%' }
])

const disruptionSeries = computed(() => {
  const counts = disruptions.value.reduce((acc, item) => {
    acc[item.type] = (acc[item.type] || 0) + 1
    return acc
  }, {})

  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([label, count]) => ({ label, count }))
})

const disruptionBars = computed(() => {
  const series = disruptionSeries.value
  const count = series.length || 1
  const { width, height, leftPad, rightPad, topPad, bottomPad, gap } = disruptionChart
  const usableWidth = width - leftPad - rightPad
  const barWidth = Math.max((usableWidth - gap * (count - 1)) / count, 6)
  const max = Math.max(...series.map(item => item.count), 1)

  return series.map((item, index) => {
    const barHeight = ((item.count / max) * (height - topPad - bottomPad))
    return {
      ...item,
      x: leftPad + index * (barWidth + gap),
      y: height - bottomPad - barHeight,
      width: barWidth,
      height: barHeight
    }
  })
})

const panelLibrary = [
  { id: 'orders', title: 'Orders', type: 'orders', colSpan: 6, rowSpan: 2, link: '/order/overview' },
  { id: 'kpis', title: 'KPI list', type: 'kpis', colSpan: 6, rowSpan: 2 },
  { id: 'disruption-trend', title: 'Disruption trend', type: 'disruption-trend', colSpan: 6, rowSpan: 2 },
  { id: 'disruptions', title: 'Disruptions', type: 'disruptions', colSpan: 6, rowSpan: 2, link: '/disruption/overview' },
  { id: 'resources', title: 'Resources', type: 'resources', colSpan: 6, rowSpan: 2, link: '/ressource' }
]

const widgets = ref([
  { ...panelLibrary[0] },
  { ...panelLibrary[1] },
  { ...panelLibrary[2] },
  { ...panelLibrary[3] }
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
    Online: 'bg-emerald-600 text-emerald-100',
    Idle: 'bg-amber-600 text-amber-100',
    Maintenance: 'bg-pink-600 text-pink-100',
    Offline: 'bg-slate-600 text-slate-100',
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
    default: 'bg-slate-600 text-slate-100'
  }
  return tones[type] || tones.default
}

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <!--
    <Topbar
      title="Overview"
      :show-reset="false"
      :show-create="false"
    />
    -->

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
              <div class="grid grid-cols-[1.3fr,0.7fr,0.7fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span>Order</span><span>Status</span><span>Start</span>
              </div>
              <div
                v-for="order in orders.slice(0, 4)"
                :key="order.id"
                class="grid grid-cols-[1.3fr,0.7fr,0.7fr] gap-2 items-center rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <span class="font-medium">{{ order.name }}</span>
                <span class="px-2 py-1 rounded-full text-xs font-semibold w-fit" :class="orderBadge(order.status)">
                  {{ order.status }}
                </span>
                <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                  {{ order.start }}
                </span>
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

            <div v-else-if="widget.type === 'disruption-trend'" class="space-y-2">
              <div class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                Frequency by type
              </div>
              <div class="rounded-lg border px-3 py-3" :class="isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-slate-200 bg-slate-50'">
                <svg
                  v-if="disruptionBars.length"
                  :viewBox="`0 0 ${disruptionChart.width} ${disruptionChart.height}`"
                  class="w-full h-36"
                >
                  <line
                    :x1="disruptionChart.leftPad"
                    :y1="disruptionChart.height - disruptionChart.bottomPad"
                    :x2="disruptionChart.width - disruptionChart.rightPad"
                    :y2="disruptionChart.height - disruptionChart.bottomPad"
                    :stroke="isDarkMode ? '#475569' : '#cbd5f5'"
                    stroke-width="1"
                  />
                  <text
                    :x="disruptionChart.leftPad - 10"
                    :y="disruptionChart.height / 2"
                    :fill="isDarkMode ? '#94a3b8' : '#64748b'"
                    font-size="6"
                    text-anchor="middle"
                    :transform="`rotate(-90 ${disruptionChart.leftPad - 10} ${disruptionChart.height / 2})`"
                  >
                    Duration
                  </text>
                  <text
                    :x="disruptionChart.width / 2"
                    :y="disruptionChart.height - 4"
                    :fill="isDarkMode ? '#94a3b8' : '#64748b'"
                    font-size="6"
                    text-anchor="middle"
                  >
                    Frequency
                  </text>
                  <rect
                    v-for="bar in disruptionBars"
                    :key="bar.label"
                    :x="bar.x"
                    :y="bar.y"
                    :width="bar.width"
                    :height="bar.height"
                    :fill="isDarkMode ? '#f472b6' : '#6366f1'"
                    rx="2"
                  />
                </svg>
                <div v-else class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                  No disruption data yet.
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2 text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                <div v-for="item in disruptionSeries" :key="item.label" class="flex items-center justify-between">
                  <span>{{ item.label }}</span>
                  <span class="font-semibold">{{ item.count }}</span>
                </div>
              </div>
            </div>

            <div v-else-if="widget.type === 'disruptions'" class="space-y-2">
              <div class="grid grid-cols-[1.2fr,0.7fr,0.9fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span>Disruption</span><span>Type</span><span>Start</span>
              </div>
              <div
                v-for="disruption in disruptions"
                :key="disruption.id"
                class="grid grid-cols-[1.2fr,0.7fr,0.9fr] gap-2 items-center rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <span class="font-medium">{{ disruption.name }}</span>
                <span class="px-2 py-1 rounded-full text-xs font-semibold w-fit" :class="disruptionBadge(disruption.type)">
                  {{ disruption.type }}
                </span>
                <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                  {{ formatDate(disruption.start) }}
                </span>
              </div>
            </div>

            <div v-else-if="widget.type === 'resources'" class="space-y-2">
              <div class="grid grid-cols-[1.2fr,0.7fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                <span>Resource</span><span>Status</span>
              </div>
              <div
                v-for="resource in resources"
                :key="resource.id"
                class="grid grid-cols-[1.2fr,0.7fr] gap-2 items-center rounded-lg border px-3 py-2 text-sm"
                :class="isDarkMode
                  ? 'border-gray-700 bg-gray-700'
                  : 'border-slate-200 bg-slate-50'"
              >
                <span class="font-medium">{{ resource.name }}</span>
                <span class="px-2 py-1 rounded-full text-xs font-semibold w-fit" :class="resourceBadge(resource.status)">
                  {{ resource.status }}
                </span>
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
