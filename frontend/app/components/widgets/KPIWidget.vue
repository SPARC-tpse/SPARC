<script setup lang="ts">
import type { KPI } from '~/composables/useDashboardData'

defineProps<{ kpis: KPI[] }>()

const trendConfig = {
  up: { icon: '+', color: '#10b981' },
  down: { icon: '-', color: '#ef4444' },
  stable: { icon: '=', color: '#6b7a90' },
}
</script>

<template>
  <div class="kpi-grid">
    <div v-for="kpi in kpis" :key="kpi.id" class="kpi-card">
      <div class="kpi-label">{{ kpi.label }}</div>

      <div class="kpi-value-row">
        <span class="kpi-value">{{ kpi.value }}</span>
        <span v-if="kpi.unit" class="kpi-unit">{{ kpi.unit }}</span>
      </div>

      <div
        v-if="kpi.trend"
        class="kpi-trend"
        :style="{ color: trendConfig[kpi.trend].color }"
      >
        <span class="trend-icon">{{ trendConfig[kpi.trend].icon }}</span>
        <span>{{ kpi.delta }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  height: 100%;
  align-content: start;
}

.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid var(--dashboard-panel-border);
  border-radius: 6px;
  background: var(--dashboard-surface);
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.kpi-card:hover {
  border-color: var(--dashboard-accent-border);
  transform: translateY(-1px);
}

.kpi-label {
  color: var(--dashboard-text-soft);
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.kpi-value {
  color: var(--dashboard-text-strong);
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.kpi-unit {
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}

.trend-icon {
  font-size: 10px;
  font-weight: 700;
}
</style>
