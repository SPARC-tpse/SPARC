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
  'orders':            '📋',
  'resources':         '⚙️',
  'kpi':               '📊',
  'disruptions-chart': '📉',
  'gantt-order':       '🗓',
  'gantt-process':     '🔄',
  'gantt-resource':    '🛠',
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
              <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
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
            <span class="widget-chip__icon">{{ iconMap[def.type] ?? '🧩' }}</span>
            <div class="widget-chip__info">
              <span class="widget-chip__name">{{ def.title }}</span>
              <span class="widget-chip__meta">{{ def.defaultW }} × {{ def.defaultH }} grid units</span>
            </div>
            <svg viewBox="0 0 20 20" fill="currentColor" class="widget-chip__add">
              <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"/>
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
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 72px 24px 24px;
}

.add-panel {
  background: #13161e;
  border: 1px solid #2a2d3a;
  border-radius: 12px;
  width: 320px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px rgba(0,0,0,0.7);
  overflow: hidden;
}

.add-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #1e2430;
}
.add-panel__title {
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f59e0b;
}
.add-panel__close {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7a90;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}
.add-panel__close:hover { color: #fff; }

.add-panel__empty {
  padding: 24px 20px;
  color: #6b7a90;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  text-align: center;
}

.add-panel__list {
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.widget-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #0d1017;
  border: 1px solid #1e2430;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: left;
  width: 100%;
}
.widget-chip:hover {
  border-color: rgba(245,158,11,0.4);
  background: rgba(245,158,11,0.05);
}
.widget-chip__icon {
  font-size: 20px;
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}
.widget-chip__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.widget-chip__name {
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: #c8d3e0;
}
.widget-chip__meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #4a5568;
}
.widget-chip__add {
  width: 16px;
  height: 16px;
  color: #f59e0b;
  flex-shrink: 0;
  opacity: 0.7;
  transition: opacity 0.15s;
}
.widget-chip:hover .widget-chip__add { opacity: 1; }

/* Transitions */
.panel-enter-active, .panel-leave-active { transition: opacity 0.2s, transform 0.2s; }
.panel-enter-from, .panel-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
