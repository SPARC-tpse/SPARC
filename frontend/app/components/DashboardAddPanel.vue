<script setup lang="ts">
import type { WidgetDef } from '~/composables/useDashboardLayout'

defineProps<{
  open: boolean
  widgets: WidgetDef[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'add', def: WidgetDef): void
}>()

const iconMap: Record<string, string> = {
  orders: 'ORD',
  resources: 'RES',
  kpi: 'KPI',
  'disruptions-chart': 'DIS',
  'gantt-order': 'GO',
  'gantt-process': 'GP',
  'gantt-resource': 'GR',
}
</script>

<template>
  <Transition name="panel">
    <div v-if="open" class="add-panel-overlay" @click.self="emit('close')">
      <div class="add-panel">
        <div class="add-panel__header">
          <span class="add-panel__title">Add Widget</span>

          <button class="add-panel__close" @click="emit('close')">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
            </svg>
          </button>
        </div>

        <div v-if="widgets.length === 0" class="add-panel__empty">
          All widgets are already on your dashboard.
        </div>

        <div class="add-panel__list">
          <button
            v-for="def in widgets"
            :key="def.type"
            class="widget-chip"
            @click="() => { emit('add', def); emit('close') }"
          >
            <span class="widget-chip__icon">{{ iconMap[def.type] ?? 'ADD' }}</span>

            <div class="widget-chip__info">
              <span class="widget-chip__name">{{ def.title }}</span>
              <span class="widget-chip__meta">{{ def.defaultW }} x {{ def.defaultH }} grid units</span>
            </div>

            <svg viewBox="0 0 20 20" fill="currentColor" class="widget-chip__add">
              <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.add-panel-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 72px 24px 24px;
  background: var(--dashboard-overlay);
  backdrop-filter: blur(4px);
}

.add-panel {
  width: 320px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--dashboard-panel-border);
  border-radius: 12px;
  background: var(--dashboard-panel-bg);
  box-shadow: var(--dashboard-shadow-strong);
}

.add-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--dashboard-panel-border);
  background: var(--dashboard-panel-header-bg);
}

.add-panel__title {
  color: var(--dashboard-accent);
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.add-panel__close {
  padding: 4px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--dashboard-text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-panel__close:hover {
  color: var(--dashboard-text-strong);
  background: var(--dashboard-surface);
}

.add-panel__empty {
  padding: 24px 20px;
  color: var(--dashboard-text-muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  text-align: center;
}

.add-panel__list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  padding: 12px;
}

.widget-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--dashboard-panel-border);
  border-radius: 8px;
  background: var(--dashboard-surface);
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
}

.widget-chip:hover {
  border-color: var(--dashboard-accent-border);
  background: color-mix(in srgb, var(--dashboard-accent) 6%, var(--dashboard-surface));
}

.widget-chip__icon {
  width: 32px;
  flex-shrink: 0;
  color: var(--dashboard-text-secondary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-align: center;
}

.widget-chip__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.widget-chip__name {
  color: var(--dashboard-text-strong);
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 600;
}

.widget-chip__meta {
  color: var(--dashboard-text-muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
}

.widget-chip__add {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: var(--dashboard-accent);
  opacity: 0.72;
  transition: opacity 0.15s ease;
}

.widget-chip:hover .widget-chip__add {
  opacity: 1;
}

.panel-enter-active,
.panel-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 900px) {
  .add-panel-overlay {
    padding: 64px 16px 16px;
  }

  .add-panel {
    width: min(360px, calc(100vw - 32px));
  }
}
</style>
