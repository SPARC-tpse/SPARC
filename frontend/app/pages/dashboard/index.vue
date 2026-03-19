<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAppTheme } from '~/composables/useAppTheme'
import { useDashboardData } from '~/composables/useDashboardData'
import { useDashboardLayout } from '~/composables/useDashboardLayout'
import { useZoom } from '~/composables/useZoom'

import DashboardAddPanel from '~/components/DashboardAddPanel.vue'
import DashboardGrid from '~/components/DashboardGrid.vue'
import DashboardWidget from '~/components/widgets/DashboardWidget.vue'

import DisruptionsWidget from '~/components/widgets/DisruptionsWidget.vue'
import KPIWidget from '~/components/widgets/KPIWidget.vue'
import OrdersWidget from '~/components/widgets/OrdersWidget.vue'
import OrderGanttWidget from '~/components/widgets/OrderGanttWidget.vue'
import ProcessGanttWidget from '~/components/widgets/ProcessGanttWidget.vue'
import ResourceGanttWidget from '~/components/widgets/ResourceGanttWidget.vue'
import ResourcesWidget from '~/components/widgets/ResourcesWidget.vue'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Dashboard - Overview',
    showReset: false,
    showCreate: false,
  },
})

const { theme, isDarkMode } = useAppTheme()
const { zoom } = useZoom()

const {
  orders,
  resources,
  kpis,
  disruptions,
  processes,
  wsConnected,
} = useDashboardData()

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

const lastUpdate = ref(new Date())
let lastUpdateTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  lastUpdateTimer = setInterval(() => {
    lastUpdate.value = new Date()
  }, 30_000)
})

onBeforeUnmount(() => {
  if (lastUpdateTimer) clearInterval(lastUpdateTimer)
})

const lastUpdateStr = computed(() =>
  lastUpdate.value.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
)
</script>

<template>
  <div
    :class="[
      theme.pageWrapper,
      'dashboard-root',
      isDarkMode ? 'dashboard-root--dark' : 'dashboard-root--light',
      { 'dashboard-root--zoomed': zoom !== 1 },
    ]"
  >
    <div class="toolbar">
      <div class="toolbar__left">
        <div class="ws-indicator" :class="wsConnected ? 'ws-indicator--on' : 'ws-indicator--off'">
          <span class="ws-dot" />
          <span>{{ wsConnected ? 'Live' : 'Offline' }}</span>
        </div>
        <span class="last-update">Updated {{ lastUpdateStr }}</span>
      </div>

      <div class="toolbar__right">
        <button
          class="toolbar-btn toolbar-btn--reset"
          title="Reset layout to default"
          @click="resetLayout"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" />
          </svg>
          Reset
        </button>

        <button
          v-if="editMode"
          class="toolbar-btn toolbar-btn--add"
          @click="addPanelOpen = !addPanelOpen"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" />
          </svg>
          Add Widget
        </button>

        <button
          class="toolbar-btn"
          :class="editMode ? 'toolbar-btn--done' : 'toolbar-btn--edit'"
          @click="toggleEdit"
        >
          <svg v-if="!editMode" viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg>
          <svg v-else viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
          </svg>
          {{ editMode ? 'Done' : 'Edit Layout' }}
        </button>
      </div>
    </div>

    <Transition name="banner">
      <div v-if="editMode" class="edit-banner">
        <svg viewBox="0 0 20 20" fill="currentColor" class="banner-icon">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" />
        </svg>
        <span>Edit mode: drag widgets to swap on wide screens, drag the corner to resize, click x to remove.</span>
      </div>
    </Transition>

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
            <OrdersWidget
              v-if="widget.type === 'orders'"
              :orders="orders"
            />

            <ResourcesWidget
              v-else-if="widget.type === 'resources'"
              :resources="resources"
            />

            <KPIWidget
              v-else-if="widget.type === 'kpi'"
              :kpis="kpis"
            />

            <DisruptionsWidget
              v-else-if="widget.type === 'disruptions-chart'"
              :disruptions="disruptions"
            />

            <OrderGanttWidget
              v-else-if="widget.type === 'gantt-order'"
              :orders="orders"
            />

            <ResourceGanttWidget
              v-else-if="widget.type === 'gantt-resource'"
              :resources="resources"
              :processes="processes"
              :orders="orders"
            />

            <ProcessGanttWidget
              v-else-if="widget.type === 'gantt-process'"
              :processes="processes"
              :orders="orders"
            />
          </DashboardWidget>
        </template>
      </DashboardGrid>

      <div v-if="visibleWidgets.length === 0" class="empty-state">
        <div class="empty-icon">[]</div>
        <p>No widgets on your dashboard.</p>
        <button class="toolbar-btn toolbar-btn--add" @click="editMode = true; addPanelOpen = true">
          + Add widgets
        </button>
      </div>
    </main>

    <DashboardAddPanel
      :open="addPanelOpen"
      :widgets="addableWidgets"
      @close="addPanelOpen = false"
      @add="addWidget"
    />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');
</style>

<style scoped>
.dashboard-root {
  min-height: 100vh;
  background: var(--dashboard-bg);
  color: var(--dashboard-text);
  font-family: 'JetBrains Mono', monospace;
  --dashboard-accent: #f59e0b;
  --dashboard-accent-soft: rgba(245, 158, 11, 0.12);
  --dashboard-accent-border: rgba(245, 158, 11, 0.4);
  --dashboard-primary: #3b82f6;
  --dashboard-primary-soft: rgba(59, 130, 246, 0.12);
  --dashboard-success: #10b981;
  --dashboard-success-soft: rgba(16, 185, 129, 0.12);
  --dashboard-danger: #ef4444;
  --dashboard-danger-soft: rgba(239, 68, 68, 0.12);
  --dashboard-overlay: rgba(0, 0, 0, 0.55);
  --dashboard-shadow-soft: 0 20px 60px rgba(0, 0, 0, 0.6);
  --dashboard-shadow-strong: 0 24px 64px rgba(0, 0, 0, 0.7);
  --dashboard-ghost-bg: rgba(245, 158, 11, 0.12);
  --dashboard-ghost-border: rgba(245, 158, 11, 0.5);
}

.dashboard-root--dark {
  --dashboard-bg: #08090d;
  --dashboard-text: #c8d3e0;
  --dashboard-text-strong: #e2e8f0;
  --dashboard-text-secondary: #8a9bb0;
  --dashboard-text-muted: #5a6a80;
  --dashboard-text-soft: #4a5568;
  --dashboard-toolbar-bg: rgba(8, 9, 13, 0.92);
  --dashboard-toolbar-border: #1a1d24;
  --dashboard-panel-bg: #111318;
  --dashboard-panel-border: #1e2430;
  --dashboard-panel-header-bg: #0d1017;
  --dashboard-surface: #0d1017;
  --dashboard-surface-alt: #151923;
  --dashboard-row-hover: rgba(255, 255, 255, 0.03);
  --dashboard-grid-line-bg: rgba(245, 158, 11, 0.04);
  --dashboard-grid-line-border: rgba(245, 158, 11, 0.12);
  --dashboard-handle-color: rgba(255, 255, 255, 0.3);
  --dashboard-handle-bg: rgba(255, 255, 255, 0.05);
  --dashboard-resize-color: rgba(255, 255, 255, 0.22);
  --text-muted: #5a6a80;
  --text-secondary: #8a9bb0;
  --border: #1e2430;
  --bg-input: #0d1017;
  --bg-surface-alt: #151923;
}

.dashboard-root--light {
  --dashboard-bg: #f4f6fa;
  --dashboard-text: #1a2030;
  --dashboard-text-strong: #0f172a;
  --dashboard-text-secondary: #334155;
  --dashboard-text-muted: #64748b;
  --dashboard-text-soft: #94a3b8;
  --dashboard-toolbar-bg: rgba(244, 246, 250, 0.95);
  --dashboard-toolbar-border: #dbe3ee;
  --dashboard-panel-bg: #ffffff;
  --dashboard-panel-border: #d6dfe9;
  --dashboard-panel-header-bg: #f7f9fc;
  --dashboard-surface: #f8fafc;
  --dashboard-surface-alt: #eef2f7;
  --dashboard-row-hover: rgba(15, 23, 42, 0.04);
  --dashboard-grid-line-bg: rgba(59, 130, 246, 0.04);
  --dashboard-grid-line-border: rgba(59, 130, 246, 0.12);
  --dashboard-handle-color: rgba(51, 65, 85, 0.45);
  --dashboard-handle-bg: rgba(148, 163, 184, 0.12);
  --dashboard-resize-color: rgba(51, 65, 85, 0.35);
  --dashboard-shadow-soft: 0 16px 40px rgba(15, 23, 42, 0.12);
  --dashboard-shadow-strong: 0 20px 48px rgba(15, 23, 42, 0.18);
  --text-muted: #64748b;
  --text-secondary: #334155;
  --border: #d6dfe9;
  --bg-input: #f8fafc;
  --bg-surface-alt: #eef2f7;
}

.toolbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  height: 56px;
  padding: 0 24px;
  background: var(--dashboard-toolbar-bg);
  border-bottom: 1px solid var(--dashboard-toolbar-border);
  backdrop-filter: blur(12px);
}

.toolbar__left,
.toolbar__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ws-indicator {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 3px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.ws-indicator--on {
  color: var(--dashboard-success);
  background: var(--dashboard-success-soft);
}

.ws-indicator--off {
  color: var(--dashboard-text-muted);
  background: color-mix(in srgb, var(--dashboard-text-muted) 12%, transparent);
}

.ws-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.ws-indicator--on .ws-dot {
  animation: pulse 1.5s ease-in-out infinite;
}

.last-update {
  color: var(--dashboard-text-muted);
  font-size: 10px;
}

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
  transition: all 0.15s ease;
}

.btn-icon {
  width: 14px;
  height: 14px;
}

.toolbar-btn--edit {
  color: var(--dashboard-accent);
  background: var(--dashboard-accent-soft);
  border-color: rgba(245, 158, 11, 0.24);
}

.toolbar-btn--edit:hover {
  background: rgba(245, 158, 11, 0.18);
  border-color: rgba(245, 158, 11, 0.45);
}

.toolbar-btn--done {
  color: var(--dashboard-success);
  background: var(--dashboard-success-soft);
  border-color: rgba(16, 185, 129, 0.24);
}

.toolbar-btn--done:hover {
  background: rgba(16, 185, 129, 0.18);
}

.toolbar-btn--add {
  color: var(--dashboard-primary);
  background: var(--dashboard-primary-soft);
  border-color: rgba(59, 130, 246, 0.24);
}

.toolbar-btn--add:hover {
  background: rgba(59, 130, 246, 0.18);
}

.toolbar-btn--reset {
  color: var(--dashboard-text-secondary);
  background: transparent;
  border-color: var(--dashboard-panel-border);
}

.toolbar-btn--reset:hover {
  color: var(--dashboard-text-strong);
  background: var(--dashboard-surface);
}

.edit-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 24px;
  background: color-mix(in srgb, var(--dashboard-accent) 8%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--dashboard-accent) 20%, transparent);
  color: color-mix(in srgb, var(--dashboard-accent) 80%, white 20%);
  font-size: 11px;
  letter-spacing: 0.03em;
}

.banner-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.banner-enter-active,
.banner-leave-active {
  transition: all 0.2s ease;
}

.banner-enter-from,
.banner-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.dashboard-main {
  min-height: calc(100vh - 56px);
  padding: 20px 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 24px;
  color: var(--dashboard-text-muted);
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  letter-spacing: 0.05em;
}

.empty-icon {
  opacity: 0.35;
  font-size: 32px;
  letter-spacing: -0.2em;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.35;
  }
}

@media (max-width: 1200px) {
  .toolbar {
    gap: 10px;
    padding: 0 18px;
  }

  .toolbar__left,
  .toolbar__right {
    gap: 10px;
  }

  .toolbar-btn {
    padding: 7px 12px;
  }

  .dashboard-main {
    padding: 16px 18px;
  }

  .edit-banner {
    padding: 8px 18px;
  }
}

@media (max-width: 900px) {
  .toolbar {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 16px;
  }

  .dashboard-main {
    padding: 16px;
  }
}

@supports not (zoom: 1) {
  .dashboard-root--zoomed .toolbar {
    position: relative;
    top: auto;
  }
}
</style>
