<script setup lang="js">
import { ref, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const orders = ref([])

function normalizePriority(value) {
  if (typeof value === 'number') {
    if (value === 3) return 'High'
    if (value === 2) return 'Medium'
    if (value === 1) return 'Low'
  }
  if (typeof value === 'string') return value
  return 'Unknown'
}

function mapOrder(order) {
  return {
    id: order.id,
    name: order.name,
    start: order.start_date ?? order.start,
    end: order.end_date ?? order.end,
    target: order.target_amount ?? order.target,
    product: order.product_name ?? order.product,
    status: order.status,
    priority: normalizePriority(order.priority),
    comments: order.comments ?? '',
    process: order.process ?? []
  }
}

function badgeTone(kind, value) {
  const statusTone = {
    Running: 'bg-emerald-600 text-emerald-100',
    Planned: 'bg-blue-600 text-blue-100',
    Paused: 'bg-amber-600 text-amber-100',
    Done: 'bg-slate-600 text-slate-100',
    default: 'bg-slate-600 text-slate-100'
  }
  const priorityTone = {
    High: 'bg-pink-600 text-pink-100',
    Medium: 'bg-indigo-600 text-indigo-100',
    Low: 'bg-slate-600 text-slate-100',
    default: 'bg-slate-600 text-slate-100'
  }
  return kind === 'status' ? (statusTone[value] || statusTone.default) : (priorityTone[value] || priorityTone.default)
}

function editOrder(orderId) {
  navigateTo(`/order/edit/${orderId}`)
}

async function fetchOrders() {
  try {
    const response = await $fetch(`${API_BASE_URL}/orders/get_orders`)
    orders.value = Array.isArray(response) ? response.map(mapOrder) : []
  } catch (error) {
    console.error('API Error:', error)
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Orders · Overview"
      :show-reset="false"
      :show-create="false"
    />

    <main class="max-w-5xl mx-auto p-6">
      <section
        class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold">Orders overview</h3>
            <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">{{ orders.length }} total</span>
          </div>
          <NuxtLink
            to="/order/new"
            class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg"
          >
            + New Order
          </NuxtLink>
        </div>
        <div class="grid gap-2">
          <div class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,80px] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <span>Name</span><span>ID</span><span>Status</span><span>Start</span><span>End</span><span>Priority</span><span>Action</span>
          </div>
          <div
            v-for="order in orders"
            :key="order.id"
            class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,80px] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
            :class="isDarkMode
              ? 'border-gray-700 bg-gray-700'
              : 'border-slate-200 bg-slate-50 hover:bg-slate-100'"
          >
            <span class="font-medium">{{ order.name }}</span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ order.id }}</span>
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('status', order.status)">
                {{ order.status }}
              </span>
            </span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ order.start }}</span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ order.end }}</span>
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('priority', order.priority)">
                {{ order.priority }}
              </span>
            </span>
            <button
              @click="editOrder(order.id)"
              class="px-2 py-1 text-xs rounded border transition-colors"
              :class="isDarkMode
                ? 'border-gray-600 hover:bg-gray-600 text-slate-200'
                : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
            >
              Edit
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dark-mode {
  @apply bg-slate-950 text-slate-100;
}
.light-mode {
  @apply bg-slate-50 text-slate-900;
}
</style>
