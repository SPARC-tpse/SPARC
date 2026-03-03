<script setup lang="ts">
import type { Order } from '~/composables/useDashboardData'

defineProps<{ orders: Order[] }>()

// status values from the backend may differ — adjust to match your model choices
const statusConfig: Record<string, { label: string; color: string; bg: string }> = {
  '0': { label: 'Planned', color: '#8b5cf6', bg: 'rgba(139,92,246,0.12)' },
  '1': { label: 'Running', color: '#3b82f6', bg: 'rgba(59,130,246,0.12)'  },
  '2': { label: 'Paused',  color: '#f59e0b', bg: 'rgba(245,158,11,0.12)'  },
  '3': { label: 'Done',    color: '#10b981', bg: 'rgba(16,185,129,0.12)'  },
}

function formatDate(iso: string) {
  if (!iso) return '—'
  const d = new Date(iso)
  const date = d.toLocaleDateString('en-CA').replace(/-/g, '.')   // → 2026.03.01
  const time = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) // → 14:00
  return `${date} ${time}`
}

// fallback for unknown status values from the backend
function getStatus(status: string) {
  console.log(status)
  return statusConfig[status] ?? { label: status, color: '#8a9bb0', bg: 'rgba(138,155,176,0.1)' }
}
</script>

<template>
  <div class="orders-widget">
    <table class="data-table">
      <thead>
        <tr>
          <th>Order</th>
          <th>Status</th>
          <th>Start</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in orders" :key="order.id" class="data-row">
          <td class="order-name">
            {{ order.name }}
            <span class="order-number">#{{ order.order_number }}</span>
          </td>
          <td>
            <span class="status-badge" :style="{ color: getStatus(order.status).color, background: getStatus(order.status).bg }">
              {{ getStatus(order.status).label }}
            </span>
          </td>
          <td class="date-cell">{{ formatDate(order.start_date) }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="orders.length === 0" class="empty">No orders</div>
  </div>
</template>

<style scoped>
.order-number {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 1px;
}

.orders-widget { height: 100%; overflow: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
}
thead tr {
  border-bottom: 1px solid #1e2430;
}
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
.order-name { color: #c8d3e0; font-weight: 500; }

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.date-cell { color: #5a6a80; }
.empty { color: #4a5568; text-align: center; padding: 20px; font-size: 12px; }
</style>
