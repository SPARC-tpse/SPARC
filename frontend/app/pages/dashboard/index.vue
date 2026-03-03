<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme.js'

import { useDashboardData }   from '~/composables/useDashboardData'
import { useDashboardLayout } from '~/composables/useDashboardLayout'
import type { WidgetLayout }  from '~/composables/useDashboardLayout'

import DashboardGrid    from '~/components/DashboardGrid.vue'
import DashboardWidget  from '~/components/widgets/DashboardWidget.vue'
import DashboardAddPanel from '~/components/DashboardAddPanel.vue'

import OrdersWidget      from '~/components/widgets/OrdersWidget.vue'
import ResourcesWidget   from '~/components/widgets/ResourcesWidget.vue'
import KPIWidget         from '~/components/widgets/KPIWidget.vue'
import DisruptionsWidget from '~/components/widgets/DisruptionsWidget.vue'
import GanttWidget       from '~/components/widgets/GanttWidget.vue'


definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Dashboard · Overview',
    showReset: false,
    showCreate: false,
  },
})

const { isDarkMode } = useTheme()

// ── Data ──────────────────────────────────────────────────────────────────────
const {
  orders, resources, kpis, disruptions,
  ganttOrders, ganttProcesses, ganttResources,
  wsConnected,
} = useDashboardData()

// ── Layout ────────────────────────────────────────────────────────────────────
const {
  visibleWidgets,
  editMode,
  addPanelOpen,
  addableWidgets,
  toggleEdit,
  removeWidget,
  addWidget,
  updateWidget,
  commitLayout,
  resetLayout,
} = useDashboardLayout()

// ── Widget content resolver ───────────────────────────────────────────────────
function getGanttItems(type: WidgetLayout['type']) {
  if (type === 'gantt-order')   return ganttOrders.value
  if (type === 'gantt-process') return ganttProcesses.value
  if (type === 'gantt-resource') return ganttResources.value
  return []
}

// Timestamp for last update indicator
const lastUpdate = ref(new Date())
onMounted(() => {
  setInterval(() => { lastUpdate.value = new Date() }, 30_000)
})
const lastUpdateStr = computed(() =>
  lastUpdate.value.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
)
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'" class="dashboard-root">

    <!-- ── Top toolbar ──────────────────────────────────────────────────── -->
    <div class="toolbar">
      <div class="toolbar__left">
        <!--<div class="toolbar__title">
          <span class="title-prefix">CTRL</span>
          <span class="title-sep">/</span>
          <span class="title-main">Dashboard</span>
        </div>-->
        <div class="ws-indicator" :class="wsConnected ? 'ws-indicator--on' : 'ws-indicator--off'">
          <span class="ws-dot" />
          <span>{{ wsConnected ? 'Live' : 'Offline' }}</span>
        </div>
        <span class="last-update">Updated {{ lastUpdateStr }}</span>
      </div>
      <div class="toolbar__right">
        <button
          class="toolbar-btn toolbar-btn--reset"
          :title="'Reset layout to default'"
          @click="resetLayout"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"/>
          </svg>
          Reset
        </button>
        <button
          v-if="editMode"
          class="toolbar-btn toolbar-btn--add"
          @click="addPanelOpen = !addPanelOpen"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"/>
          </svg>
          Add Widget
        </button>
        <button
          class="toolbar-btn"
          :class="editMode ? 'toolbar-btn--done' : 'toolbar-btn--edit'"
          @click="toggleEdit"
        >
          <svg v-if="!editMode" viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
          </svg>
          <svg v-else viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
          </svg>
          {{ editMode ? 'Done' : 'Edit Layout' }}
        </button>
      </div>
    </div>

    <!-- ── Edit mode banner ──────────────────────────────────────────────── -->
    <Transition name="banner">
      <div v-if="editMode" class="edit-banner">
        <svg viewBox="0 0 20 20" fill="currentColor" class="banner-icon">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"/>
        </svg>
        <span>Edit mode — drag widgets to reorder · drag corner to resize · click × to remove</span>
      </div>
    </Transition>

    <!-- ── Main grid ─────────────────────────────────────────────────────── -->
    <main class="dashboard-main">
      <DashboardGrid
        :widgets="visibleWidgets"
        :edit-mode="editMode"
        @update="(id, patch) => { updateWidget(id, patch); commitLayout() }"
        @remove="removeWidget"
      >
        <template #default="{ widget, editMode: em }">
          <DashboardWidget
            :widget="widget"
            :edit-mode="em"
            @remove="removeWidget"
          >
            <!-- Orders -->
            <OrdersWidget
              v-if="widget.type === 'orders'"
              :orders="orders"
            />
            <!-- Resources -->
            <ResourcesWidget
              v-else-if="widget.type === 'resources'"
              :resources="resources"
            />
            <!-- KPI -->
            <KPIWidget
              v-else-if="widget.type === 'kpi'"
              :kpis="kpis"
            />
            <!-- Disruptions chart -->
            <DisruptionsWidget
              v-else-if="widget.type === 'disruptions-chart'"
              :disruptions="disruptions"
            />
            <!-- Gantt widgets -->
            <GanttWidget
              v-else-if="widget.type.startsWith('gantt-')"
              :items="getGanttItems(widget.type)"
              :label="widget.title"
            />
          </DashboardWidget>
        </template>
      </DashboardGrid>

      <!-- Empty state -->
      <div v-if="visibleWidgets.length === 0" class="empty-state">
        <div class="empty-icon">⬛</div>
        <p>No widgets on your dashboard.</p>
        <button class="toolbar-btn toolbar-btn--add" @click="editMode = true; addPanelOpen = true">
          + Add widgets
        </button>
      </div>
    </main>

    <!-- ── Add widget panel ──────────────────────────────────────────────── -->
    <DashboardAddPanel
      :open="addPanelOpen"
      :widgets="addableWidgets"
      @close="addPanelOpen = false"
      @add="addWidget"
    />
  </div>
</template>

<style>
/* Google Fonts import — add to nuxt.config or <head> if needed */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');
</style>

<style scoped>
.dashboard-root {
  min-height: 100vh;
  background: #08090d;
  color: #c8d3e0;
  font-family: 'JetBrains Mono', monospace;
}

/* ── Toolbar ────────────────────────────────────────────────────────────── */
.toolbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  background: rgba(8,9,13,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #1a1d24;
  gap: 12px;
}

.toolbar__left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar__title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.title-prefix {
  color: #f59e0b;
  text-transform: uppercase;
}
.title-sep {
  color: #2a2d3a;
  font-weight: 300;
}
.title-main {
  color: #c8d3e0;
  text-transform: uppercase;
}

.ws-indicator {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 3px;
}
.ws-indicator--on  { color: #10b981; background: rgba(16,185,129,0.1); }
.ws-indicator--off { color: #6b7a90; background: rgba(107,122,144,0.1); }
.ws-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.ws-indicator--on .ws-dot {
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity: 1; }
  50%     { opacity: 0.3; }
}

.last-update {
  font-size: 10px;
  color: #3a4558;
  font-family: 'JetBrains Mono', monospace;
}

.toolbar__right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Toolbar buttons ────────────────────────────────────────────────────── */
.toolbar-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 5px;
  border: 1px solid transparent;
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-icon { width: 14px; height: 14px; }

.toolbar-btn--edit {
  color: #f59e0b;
  background: rgba(245,158,11,0.1);
  border-color: rgba(245,158,11,0.25);
}
.toolbar-btn--edit:hover {
  background: rgba(245,158,11,0.2);
  border-color: rgba(245,158,11,0.5);
}

.toolbar-btn--done {
  color: #10b981;
  background: rgba(16,185,129,0.1);
  border-color: rgba(16,185,129,0.25);
}
.toolbar-btn--done:hover {
  background: rgba(16,185,129,0.2);
}

.toolbar-btn--add {
  color: #3b82f6;
  background: rgba(59,130,246,0.1);
  border-color: rgba(59,130,246,0.25);
}
.toolbar-btn--add:hover {
  background: rgba(59,130,246,0.2);
}

.toolbar-btn--reset {
  color: #6b7a90;
  background: transparent;
  border-color: #1e2430;
}
.toolbar-btn--reset:hover {
  color: #8a9bb0;
  border-color: #2a2d3a;
}

/* ── Edit banner ────────────────────────────────────────────────────────── */
.edit-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 24px;
  background: rgba(245,158,11,0.06);
  border-bottom: 1px solid rgba(245,158,11,0.15);
  font-size: 11px;
  color: rgba(245,158,11,0.8);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.03em;
}
.banner-icon { width: 14px; height: 14px; flex-shrink: 0; }

.banner-enter-active, .banner-leave-active { transition: all 0.2s; }
.banner-enter-from, .banner-leave-to {
  opacity: 0;
  transform: translateY(-8px);
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* ── Main grid area ─────────────────────────────────────────────────────── */
.dashboard-main {
  padding: 20px 24px;
  min-height: calc(100vh - 56px);
}

/* ── Empty state ────────────────────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px;
  color: #3a4558;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  letter-spacing: 0.05em;
}
.empty-icon { font-size: 40px; opacity: 0.3; }

/* ── Light mode overrides ───────────────────────────────────────────────── */
.light-mode.dashboard-root {
  background: #f4f6fa;
  color: #1a2030;
}
.light-mode .toolbar {
  background: rgba(244,246,250,0.95);
  border-bottom-color: #dde2ea;
}
.light-mode .last-update { color: #9aabb8; }
</style>