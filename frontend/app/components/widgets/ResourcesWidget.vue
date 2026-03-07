<script setup lang="ts">
import type { Resource } from '~/composables/useDashboardData'

const props = defineProps<{ resources: Resource[] }>()

const statusConfig: Record<string, { label: string; color: string; dot: string }> = {
  '0': { label: 'Available',   color: '#10b981', dot: '#10b981' },
  '1': { label: 'In Use',      color: '#3b82f6', dot: '#3b82f6' },
  '2': { label: 'Maintenance', color: '#f59e0b', dot: '#f59e0b' },
  '3': { label: 'Offline',     color: '#6b7a90', dot: '#4a5568' },
}

// Sorts the list of resources
const sortedResources = computed(() =>
  [...props.resources]
    .filter(r => r.id)
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
        <tr v-for="r in sortedResources" :key="r.id" class="data-row">
          <td class="res-name">{{ r.name }}</td>
          <td class="res-type">{{ r.type.name }}</td>
          <td>
            <span class="status-row">
              <span class="status-dot" :style="{ background: statusConfig[r.status].dot }" />
              <span :style="{ color: statusConfig[r.status].color }">
                {{ statusConfig[r.status].label }}
              </span>
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.res-type { color: var(--text-muted); font-size: 11px; }
.resources-widget { height: 100%; overflow: auto; }
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
}
thead tr { border-bottom: 1px solid #1e2430; }
th {
  padding: 0 8px 8px;
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #4a5568;
}
.data-row {
  border-bottom: 1px solid rgba(30,36,48,0.5);
  transition: background 0.1s;
}
.data-row:hover { background: rgba(255,255,255,0.03); }
td { padding: 8px; color: #8a9bb0; }
.res-name { color: #c8d3e0; font-weight: 500; }

.status-row {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}
</style>
