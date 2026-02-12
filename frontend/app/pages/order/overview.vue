<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useOrderWebSocket } from '~/composables/useOrderWebSocket'

definePageMeta({ layout: 'custom' })

const { isDarkMode } = useTheme()
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const sortColumn = ref('id')
const sortDirection = ref('desc')
const isDeleteMode = ref(false)
const deleteConfirmId = ref(null)
const orders = ref([])

const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High' };
const statusMap = { 1: 'Planned', 2: 'Running', 3: 'Paused', 4: 'Done' };

function getStatusText(val) { return statusMap[val] || val }
function getPriorityText(val) { return priorityMap[val] || val }

function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('de-DE')
}

const sortedOrders = computed(() => {
    const ordersCopy = [...orders.value]
    return ordersCopy.sort((a, b) => {
        let aValue = a[sortColumn.value]
        let bValue = b[sortColumn.value]

        if (sortColumn.value === 'start_date' || sortColumn.value === 'end_date') {
            aValue = new Date(aValue)
            bValue = new Date(bValue)
        } else if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase()
            bValue = bValue.toLowerCase()
        }

        if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1
        if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1
        return 0
    })
})

function sortBy(column) {
    if (sortColumn.value === column) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortColumn.value = column
        sortDirection.value = 'asc'
    }
}

function getSortIcon(column) {
    if (sortColumn.value !== column) return '↕'
    return sortDirection.value === 'asc' ? '↑' : '↓'
}

const handleOrderUpdate = async (data) => {
  if (data.action === 'created') orders.value.push(data.data)
  else if (data.action === 'updated') {
    const index = orders.value.findIndex(o => o.id === data.data.id)
    if (index !== -1) orders.value[index] = data.data
  } else if (data.action === 'deleted') {
    orders.value = orders.value.filter(o => o.id !== data.data.id)
  }
}

const { connected } = useOrderWebSocket(handleOrderUpdate)

function badgeTone(kind, valueStr) {
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
  return kind === 'status' ? (statusTone[valueStr] || statusTone.default) : (priorityTone[valueStr] || priorityTone.default)
}

function toggleDeleteMode() {
  isDeleteMode.value = !isDeleteMode.value
  deleteConfirmId.value = null
}

function handleRowAction(id) {
  if (!isDeleteMode.value) {
    navigateTo(`/order/edit/${id}`)
  } else {
    if (deleteConfirmId.value === id) deleteConfirmId.value = null
    else deleteConfirmId.value = id
  }
}

async function executeDelete(id) {
    try {
        await $fetch(`${API_BASE_URL}/api/order/delete/${id}`, { method: 'DELETE' })
        orders.value = orders.value.filter(o => o.id !== id)
        deleteConfirmId.value = null
    } catch (error) {
        console.error('API Error:', error)
        alert('Failed to delete order')
    }
}

async function fetchOrders() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/order/get`, { method: 'GET' });
        orders.value = response || [];
    } catch (error) {
        console.error('API Error:', error);
    }
}

onMounted(() => { fetchOrders() })
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar title="Orders · Overview" :show-reset="false" :show-create="false" />

    <main class="max-w-6xl mx-auto p-6">
      <section class="rounded-xl border p-4 space-y-4 shadow-lg transition-colors" :class="isDarkMode ? 'border-gray-700 bg-slate-900 shadow-black' : 'border-slate-200 bg-white shadow-slate-200'">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold text-lg">Orders overview</h3>
            <span class="px-2 py-0.5 rounded text-xs font-medium border" :class="isDarkMode ? 'border-slate-700 text-slate-400 bg-slate-800' : 'border-slate-200 text-slate-500 bg-slate-50'">
                {{ orders.length }} total
            </span>
          </div>

          <div class="flex gap-2">
            <button @click="toggleDeleteMode" class="px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm" :class="[isDeleteMode ? 'bg-slate-200 text-slate-800 border-slate-300' : 'bg-white text-slate-700 border-slate-200 hover:border-red-400 hover:text-red-600', isDarkMode && isDeleteMode ? '!bg-slate-700 !text-white !border-slate-600' : '', isDarkMode && !isDeleteMode ? '!bg-slate-800 !text-slate-200 !border-slate-700 hover:!border-red-500 hover:!text-red-400' : '']">
              {{ isDeleteMode ? 'Done deleting' : 'Delete mode' }}
            </button>
            <NuxtLink to="/order/new" class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg hover:brightness-110">+ New Order</NuxtLink>
          </div>
        </div>

        <div class="grid gap-2 overflow-x-auto">
          <div class="grid grid-cols-[1.5fr,0.8fr,0.8fr,1fr,1fr,0.8fr,100px] gap-3 px-3 py-2 text-xs font-medium uppercase tracking-wider border-b" :class="isDarkMode ? 'text-slate-400 border-gray-700' : 'text-slate-500 border-slate-100'">
            <button @click="sortBy('name')" class="text-left hover:text-pink-500 transition-colors flex items-center gap-1">Name <span class="opacity-50">{{ getSortIcon('name') }}</span></button>
            <button @click="sortBy('id')" class="text-left hover:text-pink-500 transition-colors flex items-center gap-1">ID <span class="opacity-50">{{ getSortIcon('id') }}</span></button>
            <button @click="sortBy('status')" class="text-left hover:text-pink-500 transition-colors flex items-center gap-1">Status <span class="opacity-50">{{ getSortIcon('status') }}</span></button>
            <button @click="sortBy('start_date')" class="text-left hover:text-pink-500 transition-colors flex items-center gap-1">Start <span class="opacity-50">{{ getSortIcon('start_date') }}</span></button>
            <button @click="sortBy('end_date')" class="text-left hover:text-pink-500 transition-colors flex items-center gap-1">End <span class="opacity-50">{{ getSortIcon('end_date') }}</span></button>
            <button @click="sortBy('priority')" class="text-left hover:text-pink-500 transition-colors flex items-center gap-1">Priority <span class="opacity-50">{{ getSortIcon('priority') }}</span></button>
            <span class="text-center">Action</span>
          </div>

          <div v-if="sortedOrders.length === 0" class="py-10 text-center text-sm opacity-50">No orders found. Create one to get started.</div>

          <div v-for="order in sortedOrders" :key="order.id" class="grid grid-cols-[1.5fr,0.8fr,0.8fr,1fr,1fr,0.8fr,100px] gap-3 items-center rounded-lg border p-3 text-sm transition-all" :class="[isDarkMode ? 'border-gray-700 bg-slate-800/50 hover:bg-slate-800' : 'border-slate-200 bg-slate-50 hover:bg-white hover:shadow-sm', deleteConfirmId === order.id ? (isDarkMode ? '!bg-red-900/10 !border-red-900/30' : '!bg-red-50 !border-red-100') : '']">
            <div class="font-medium flex items-center gap-2 overflow-hidden min-w-0">
               <button v-if="deleteConfirmId === order.id" @click.stop="executeDelete(order.id)" class="bg-red-600 text-white text-[10px] uppercase font-bold px-2 py-1 rounded animate-pulse hover:bg-red-700 shrink-0 shadow-sm transition-colors">Confirm</button>
               <span class="truncate" :title="order.name">{{ order.name }}</span>
            </div>
            <span class="font-mono text-xs truncate" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">#{{ order.id }}</span>
            <span><span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border border-transparent" :class="badgeTone('status', getStatusText(order.status))">{{ getStatusText(order.status) }}</span></span>
            <span class="text-xs truncate" :class="isDarkMode ? 'text-slate-300' : 'text-slate-600'">{{ formatDate(order.start_date) }}</span>
            <span class="text-xs truncate" :class="isDarkMode ? 'text-slate-300' : 'text-slate-600'">{{ formatDate(order.end_date) }}</span>
            <span><span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide" :class="badgeTone('priority', getPriorityText(order.priority))">{{ getPriorityText(order.priority) }}</span></span>
            <button @click.stop="handleRowAction(order.id)" class="px-2 py-1.5 text-xs font-medium rounded border transition-colors w-full text-center" :class="[!isDeleteMode && isDarkMode ? 'border-gray-600 text-slate-300 hover:bg-indigo-900/30 hover:text-indigo-300 hover:border-indigo-800' : '', !isDeleteMode && !isDarkMode ? 'border-slate-300 text-slate-600 hover:bg-white hover:text-indigo-600 hover:border-indigo-300' : '', isDeleteMode && deleteConfirmId === order.id ? 'border-slate-400 text-slate-500 hover:bg-slate-200' : '', isDeleteMode && deleteConfirmId !== order.id ? 'border-red-200 text-red-500 hover:bg-red-50 hover:border-red-300' : '']">
              {{ !isDeleteMode ? 'Edit' : (deleteConfirmId === order.id ? 'Cancel' : 'Delete') }}
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dark-mode { @apply bg-slate-950 text-slate-100; }
.light-mode { @apply bg-slate-50 text-slate-900; }
</style>