<script setup lang="ts">
import type { WidgetLayout } from '~/composables/useDashboardLayout'

defineProps<{
  widget: WidgetLayout
  editMode: boolean
}>()

const emit = defineEmits<{
  (e: 'remove', id: string): void
}>()
</script>

<template>
  <div class="widget" :class="{ 'widget--edit': editMode }">
    <div class="widget__header">
      <span class="widget__title">{{ widget.title }}</span>

      <div class="widget__actions">
        <a
          v-if="widget.redirect"
          :href="widget.redirect"
          class="widget__action widget__action--open"
          title="Open full view"
        >
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" class="action-icon">
            <path d="M11 3h6v6M17 3l-8 8M4 8H3a1 1 0 00-1 1v8a1 1 0 001 1h8a1 1 0 001-1v-1" />
          </svg>
          <span>Open</span>
        </a>

        <button
          v-if="editMode"
          class="widget__action widget__action--close"
          title="Remove widget"
          @click="emit('remove', widget.id)"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" class="action-icon">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </button>
      </div>
    </div>

    <div class="widget__body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.widget {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  border: 1px solid var(--dashboard-panel-border);
  border-radius: 8px;
  background: var(--dashboard-panel-bg);
  color: var(--dashboard-text);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  box-shadow: var(--dashboard-shadow-soft);
}

.widget--edit {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.12), var(--dashboard-shadow-soft);
}

.widget__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  background: var(--dashboard-panel-header-bg);
  border-bottom: 1px solid var(--dashboard-panel-border);
}

.widget__title {
  color: var(--dashboard-text-secondary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.widget__actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.widget__action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-family: inherit;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.widget__action--open {
  color: var(--dashboard-primary);
  background: var(--dashboard-primary-soft);
}

.widget__action--open:hover {
  filter: brightness(1.05);
}

.widget__action--close {
  color: var(--dashboard-text-muted);
  background: transparent;
}

.widget__action--close:hover {
  color: var(--dashboard-danger);
  background: var(--dashboard-danger-soft);
}

.action-icon {
  width: 13px;
  height: 13px;
}

.widget__body {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 12px 14px;
}

@media (max-width: 1200px) {
  .widget__header {
    min-height: 40px;
    padding: 0 12px;
  }

  .widget__body {
    padding: 10px 12px;
  }
}
</style>
