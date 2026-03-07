<script setup lang="ts">
import type { WidgetLayout } from '~/composables/useDashboardLayout'

const props = defineProps<{
  widget: WidgetLayout
  editMode: boolean
}>()

const emit = defineEmits<{
  (e: 'remove', id: string): void
}>()
</script>

<template>
  <div class="widget" :class="{ 'widget--edit': editMode }">
    <!-- Header -->
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
            <path d="M11 3h6v6M17 3l-8 8M4 8H3a1 1 0 00-1 1v8a1 1 0 001 1h8a1 1 0 001-1v-1"/>
          </svg>
          <span>Open</span>
        </a>
        <button
          v-if="editMode"
          class="widget__action widget__action--close"
          @click="emit('remove', widget.id)"
          title="Remove widget"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" class="action-icon">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Content -->
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
  background: #111318;
  border: 1px solid #1e2430;
  border-radius: 8px;
  overflow: hidden;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.widget--edit {
  border-color: rgba(245, 158, 11, 0.25);
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.1);
}

.widget__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  height: 42px;
  min-height: 42px;
  background: #0d1017;
  border-bottom: 1px solid #1e2430;
  gap: 8px;
}

.widget__title {
  font-family: 'Rajdhani', 'Barlow Condensed', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8a9bb0;
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
  border-radius: 4px;
  border: none;
  font-size: 11px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}

.widget__action--open {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}
.widget__action--open:hover {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.widget__action--close {
  color: #6b7a90;
  background: transparent;
}
.widget__action--close:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.12);
}

.action-icon {
  width: 13px;
  height: 13px;
}

.widget__body {
  flex: 1;
  overflow: auto;
  padding: 12px 14px;
  min-height: 0;
}
</style>
