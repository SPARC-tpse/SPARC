<script setup lang="ts">
import type { Order } from '~/composables/useDashboardData'

defineProps<{ orders: Order[] }>()

const statusConfig: Record<string, { label: string; color: string; bg: string }> = {
  '0': { label: 'Planned', color: '#8b5cf6', bg: 'rgba(139,92,246,0.12)' },
  '1': { label: 'Running', color: '#3b82f6', bg: 'rgba(59,130,246,0.12)'  },
  '2': { label: 'Paused',  color: '#f59e0b', bg: 'rgba(245,158,11,0.12)'  },
  '3': { label: 'Done',    color: '#10b981', bg: 'rgba(16,185,129,0.12)'  },
}

function formatDate(iso: string) {
  if (!iso) return '-'

  const date = new Date(iso)
  const datePart = date.toLocaleDateString('en-CA').replace(/-/g, '.')
  const timePart = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })

  return `${datePart} ${timePart}`
}

function getStatus(status: number) {
  return statusConfig[String(status)] ?? {
    label: String(status),
    color: '#8a9bb0',
    bg: 'rgba(138, 155, 176, 0.12)',
  }
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
.orders-widget {
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

.order-name {
  color: var(--dashboard-text-strong);
  font-weight: 500;
}

.order-number,
.date-cell {
  color: var(--text-muted);
}

.order-number {
  display: block;
  margin-top: 1px;
  font-size: 10px;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.empty {
  padding: 20px;
  color: var(--dashboard-text-muted);
  font-size: 12px;
  text-align: center;
}
</style>
