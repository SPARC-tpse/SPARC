<script setup lang="ts">
import { computed } from 'vue'
import type { Resource } from '~/composables/useDashboardData'

const props = defineProps<{ resources: Resource[] }>()

const statusConfig: Record<string, { label: string; color: string; dot: string }> = {
  '0': { label: 'Available', color: '#10b981', dot: '#10b981' },
  '1': { label: 'In Use', color: '#3b82f6', dot: '#3b82f6' },
  '2': { label: 'Maintenance', color: '#f59e0b', dot: '#f59e0b' },
  '3': { label: 'Offline', color: '#6b7a90', dot: '#64748b' },
}

const sortedResources = computed(() =>
  [...props.resources]
    .filter(resource => resource.id)
    .sort((a, b) => a.id - b.id)
)
</script>

<template>
  <div class="resources-widget">
    <table class="data-table">
      <thead>
        <tr>
          <th>Resource</th>
          <th>Type</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="resource in sortedResources" :key="resource.id" class="data-row">
          <td class="res-name">{{ resource.name }}</td>
          <td class="res-type">{{ resource.type.name }}</td>
          <td>
            <span class="status-row">
              <span class="status-dot" :style="{ background: statusConfig[resource.status].dot }" />
              <span :style="{ color: statusConfig[resource.status].color }">
                {{ statusConfig[resource.status].label }}
              </span>
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="sortedResources.length === 0" class="empty">No resources</div>
  </div>
</template>

<style scoped>
.resources-widget {
  height: 100%;
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}

thead tr {
  border-bottom: 1px solid var(--border);
}

th {
  padding: 0 8px 8px;
  color: var(--dashboard-text-soft);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-align: left;
  text-transform: uppercase;
}

.data-row {
  border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
  transition: background 0.1s ease;
}

.data-row:hover {
  background: var(--dashboard-row-hover);
}

td {
  padding: 8px;
  color: var(--text-secondary);
}

.res-name {
  color: var(--dashboard-text-strong);
  font-weight: 500;
}

.res-type {
  color: var(--text-muted);
  font-size: 11px;
}

.status-row {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.status-dot {
  width: 7px;
  height: 7px;
  flex-shrink: 0;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.empty {
  padding: 20px;
  color: var(--dashboard-text-muted);
  font-size: 12px;
  text-align: center;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}
</style>
