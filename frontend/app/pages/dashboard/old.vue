<script setup lang="js">
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Dashboard · Overview',
    showReset: false,
    showCreate: false,
  },
})

const { theme, colors, isDarkMode, getBadgeColor } = useAppTheme()

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
  { id: 'ORD-1042', name: 'Test Order', status: 'Running', start_date: '2025-11-27' },
  { id: 'ORD-1043', name: 'Calibration Batch', status: 'Planned', start_date: '2025-11-29' },
  { id: 'ORD-1044', name: 'Valve Assembly', status: 'Paused', start_date: '2025-11-30' }
])

const resources = ref([
  { id: 'RES-01', name: 'Machine A', status: 'Online' },
  { id: 'RES-02', name: 'Conveyor 3', status: 'Idle' },
  { id: 'RES-03', name: 'Robot Arm', status: 'Maintenance' }
])

const disruptions = ref([
  { id: 'DIS-1234', name: 'Machine Malfunction', start_date: '2025-12-27T10:00', type: 'Error' },
  { id: 'DIS-1235', name: 'Planned Calibration', start_date: '2025-12-27T14:00', type: 'Maintenance' },
  { id: 'DIS-1236', name: 'Sensor Drift', start_date: '2025-12-28T09:20', type: 'Quality' },
  { id: 'DIS-1237', name: 'Material Shortage', start_date: '2025-12-28T13:30', type: 'Material' },
  { id: 'DIS-1238', name: 'Line Stop', start_date: '2025-12-28T16:10', type: 'Error' }
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
  return getBadgeColor('status', status)
}

function resourceBadge(status) {
  const tones = {
    Online: 'bg-emerald-600 text-emerald-100',
    Idle: 'bg-amber-600 text-amber-100',
    Maintenance: 'bg-pink-600 text-pink-100',
    Offline: 'bg-slate-600 text-slate-100'
  }
  return tones[status] || 'bg-slate-600 text-slate-100'
}

function disruptionBadge(type) {
  const tones = {
    Error: 'bg-amber-600 text-amber-100',
    Maintenance: 'bg-indigo-600 text-indigo-100',
    Quality: 'bg-cyan-600 text-cyan-100',
    Material: 'bg-orange-600 text-orange-100'
  }
  return tones[type] || 'bg-slate-600 text-slate-100'
}

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('en-GB', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}
</script>

<template>
  <main :class="theme.container" class="space-y-4">

    <!-- Layout-Editor Card -->
    <section :class="theme.dashboardCard">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 :class="theme.dashboardSubtitle">Dashboard layout</h2>
          <p :class="theme.dashboardHint">Edit mode enables drag, close, and add panels.</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button :class="theme.dashboardEditBtn" @click="editMode = !editMode">
            {{ editMode ? 'Finish edit' : 'Edit layout' }}
          </button>
          <div class="flex items-center gap-2">
            <select v-model="panelToAdd" :class="theme.input" class="h-10 mt-0">
              <option disabled value="">Add panel</option>
              <option v-for="panel in availablePanels" :key="panel.id" :value="panel.id">
                {{ panel.title }}
              </option>
            </select>
            <button
              :class="theme.dashboardEditBtn"
              class="disabled:opacity-50"
              :disabled="!panelToAdd"
              @click="addPanel"
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Widget Grid -->
    <TransitionGroup name="panel-swap" tag="section" class="dashboard-grid">
      <article
        v-for="(widget, index) in widgets"
        :key="widget.id"
        class="panel"
        :style="panelStyle(widget)"
        :class="[
          theme.dashboardPanel,
          editMode ? 'cursor-move' : '',
          editMode && dragOverIndex === index ? theme.dashboardEditRing : ''
        ]"
        :draggable="editMode"
        @dragstart="startDrag(index, $event)"
        @dragover="onDragOver(index, $event)"
        @drop="onDrop(index)"
        @dragend="onDragEnd"
      >
        <div class="panel-header" :class="colors.dashboardPanelHeaderBorder">
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold">{{ widget.title }}</span>
            <span v-if="editMode" :class="theme.dashboardDragHint">Drag</span>
          </div>
          <div class="flex items-center gap-2">
            <NuxtLink v-if="widget.link" :to="widget.link" :class="theme.dashboardOpenLink">Open</NuxtLink>
            <button v-if="editMode" :class="theme.dashboardEditBtn" @click="closePanel(widget.id)">Close</button>
          </div>
        </div>

        <div class="panel-body space-y-2">

          <!-- Orders -->
          <div v-if="widget.type === 'orders'" class="space-y-2">
            <div class="grid grid-cols-[1.3fr,0.7fr,0.7fr] gap-2" :class="theme.dashboardHeaderText">
              <span>Order</span><span>Status</span><span>Start</span>
            </div>
            <div
              v-for="order in orders.slice(0, 4)" :key="order.id"
              class="grid grid-cols-[1.3fr,0.7fr,0.7fr] gap-2 items-center"
              :class="theme.dashboardPanelRow"
            >
              <span class="font-medium">{{ order.name }}</span>
              <span :class="[theme.badge, orderBadge(order.status)]" class="w-fit">{{ order.status }}</span>
              <span :class="theme.dashboardMetaText">{{ order.start_date }}</span>
            </div>
          </div>

          <!-- KPIs -->
          <div v-else-if="widget.type === 'kpis'" class="space-y-2">
            <div
              v-for="kpi in kpis" :key="kpi.id"
              class="flex items-center justify-between"
              :class="theme.dashboardPanelRow"
            >
              <div>
                <div class="font-medium">{{ kpi.name }}</div>
                <div :class="theme.dashboardMetaText">{{ kpi.unit }}</div>
              </div>
              <div class="text-right">
                <div class="font-semibold">{{ kpi.value }}</div>
                <div class="text-xs" :class="kpi.delta.startsWith('+') ? 'text-emerald-500' : 'text-rose-400'">{{ kpi.delta }}</div>
              </div>
            </div>
          </div>

          <!-- Disruption Trend -->
          <div v-else-if="widget.type === 'disruption-trend'" class="space-y-2">
            <div :class="theme.dashboardMetaText">Frequency by type</div>
            <div :class="theme.dashboardChartBg">
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
                  :stroke="colors.dashboardAxisStroke"
                  stroke-width="1"
                />
                <text
                  :x="disruptionChart.leftPad - 10"
                  :y="disruptionChart.height / 2"
                  :fill="colors.dashboardAxisText"
                  font-size="6" text-anchor="middle"
                  :transform="`rotate(-90 ${disruptionChart.leftPad - 10} ${disruptionChart.height / 2})`"
                >Duration</text>
                <text
                  :x="disruptionChart.width / 2"
                  :y="disruptionChart.height - 4"
                  :fill="colors.dashboardAxisText"
                  font-size="6" text-anchor="middle"
                >Frequency</text>
                <rect
                  v-for="bar in disruptionBars" :key="bar.label"
                  :x="bar.x" :y="bar.y" :width="bar.width" :height="bar.height"
                  :fill="colors.dashboardBarFill"
                  rx="2"
                />
              </svg>
              <div v-else :class="theme.dashboardEmptyChart">No disruption data yet.</div>
            </div>
            <div class="grid grid-cols-2 gap-2" :class="theme.dashboardMetaText">
              <div v-for="item in disruptionSeries" :key="item.label" class="flex items-center justify-between">
                <span>{{ item.label }}</span>
                <span class="font-semibold">{{ item.count }}</span>
              </div>
            </div>
          </div>

          <!-- Disruptions -->
          <div v-else-if="widget.type === 'disruptions'" class="space-y-2">
            <div class="grid grid-cols-[1.2fr,0.7fr,0.9fr] gap-2" :class="theme.dashboardHeaderText">
              <span>Disruption</span><span>Type</span><span>Start</span>
            </div>
            <div
              v-for="disruption in disruptions" :key="disruption.id"
              class="grid grid-cols-[1.2fr,0.7fr,0.9fr] gap-2 items-center"
              :class="theme.dashboardPanelRow"
            >
              <span class="font-medium">{{ disruption.name }}</span>
              <span :class="[theme.badge, disruptionBadge(disruption.type)]" class="w-fit">{{ disruption.type }}</span>
              <span :class="theme.dashboardMetaText">{{ formatDate(disruption.start_date) }}</span>
            </div>
          </div>

          <!-- Resources -->
          <div v-else-if="widget.type === 'resources'" class="space-y-2">
            <div class="grid grid-cols-[1.2fr,0.7fr] gap-2" :class="theme.dashboardHeaderText">
              <span>Resource</span><span>Status</span>
            </div>
            <div
              v-for="resource in resources" :key="resource.id"
              class="grid grid-cols-[1.2fr,0.7fr] gap-2 items-center"
              :class="theme.dashboardPanelRow"
            >
              <span class="font-medium">{{ resource.name }}</span>
              <span :class="[theme.badge, resourceBadge(resource.status)]" class="w-fit">{{ resource.status }}</span>
            </div>
          </div>

        </div>
      </article>
    </TransitionGroup>
  </main>
</template>

<style scoped>
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
