<script setup lang="ts">
import type { KPI } from '~/composables/useDashboardData'
defineProps<{ kpis: KPI[] }>()

const trendConfig = {
  up:     { icon: '▲', color: '#10b981' },
  down:   { icon: '▼', color: '#ef4444' },
  stable: { icon: '■', color: '#6b7a90' },
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
  background: #0d1017;
  border: 1px solid #1e2430;
  border-radius: 6px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  transition: border-color 0.15s;
}
.kpi-card:hover { border-color: rgba(245,158,11,0.3); }

.kpi-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #4a5568;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.kpi-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: -0.02em;
}
.kpi-unit {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #4a5568;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
}
.trend-icon { font-size: 8px; }
</style>
