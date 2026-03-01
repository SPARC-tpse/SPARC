<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useOrderWebSocket } from '~/composables/useOrderWebSocket'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Orders · Overview',
    showReset: false,
    showCreate: false,
  },
})

// Theme einbinden
const { theme, getBadgeColor } = useAppTheme()

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
            aValue = new Date(aValue); bValue = new Date(bValue);
        } else if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase(); bValue = bValue.toLowerCase();
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
        sortColumn.value = column; sortDirection.value = 'asc';
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

function toggleDeleteMode() {
  isDeleteMode.value = !isDeleteMode.value
  deleteConfirmId.value = null
}

function handleRowAction(id) {
  if (!isDeleteMode.value) navigateTo(`/order/edit/${id}`)
  else deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
}

async function executeDelete(id) {
    try {
        await $fetch(`${API_BASE_URL}/api/order/delete/${id}`, { method: 'DELETE' })
        orders.value = orders.value.filter(o => o.id !== id)
        deleteConfirmId.value = null
    } catch (error) { alert('Failed to delete order') }
}

async function fetchOrders() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/order/get`, { method: 'GET' });
        orders.value = response || [];
    } catch (error) { console.error('API Error:', error); }
}

onMounted(() => { fetchOrders() })
</script>

<template>
  <div :class="theme.pageWrapper" class="h-full min-h-0 flex flex-col">
    <!-- <Topbar title="Orders · Overview" :show-reset="false" :show-create="false" /> -->

    <main :class="theme.container">
      <section :class="theme.card">

        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold text-lg">Orders overview</h3>
            <span :class="theme.totalBadge">
                {{ orders.length }} total
            </span>
          </div>

          <div class="flex gap-2">
            <button @click="toggleDeleteMode"
              :class="isDeleteMode
                ? 'px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm bg-slate-700 text-white border-slate-600' 
                : theme.btnDeleteMode"
            >
              {{ isDeleteMode ? 'Done' : 'Delete mode' }}
            </button>
            <NuxtLink to="/order/new" class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg hover:brightness-110">+ New Order</NuxtLink>
          </div>
        </div>

        <div class="grid gap-2 overflow-x-auto">
          <div :class="theme.tableHeaderOrders">
            <button @click="sortBy('name')" :class="[theme.headerBtn, 'justify-start']">Name <span class="opacity-50 ml-1">{{ getSortIcon('name') }}</span></button>
            <button @click="sortBy('id')" :class="[theme.headerBtn, 'justify-start']">ID <span class="opacity-50 ml-1">{{ getSortIcon('id') }}</span></button>
            <button @click="sortBy('status')" :class="[theme.headerBtn, 'justify-start']">Status <span class="opacity-50 ml-1">{{ getSortIcon('status') }}</span></button>
            <button @click="sortBy('start_date')" :class="[theme.headerBtn, 'justify-start']">Start <span class="opacity-50 ml-1">{{ getSortIcon('start_date') }}</span></button>
            <button @click="sortBy('end_date')" :class="[theme.headerBtn, 'justify-start']">End <span class="opacity-50 ml-1">{{ getSortIcon('end_date') }}</span></button>
            <button @click="sortBy('priority')" :class="[theme.headerBtn, 'justify-start']">Priority <span class="opacity-50 ml-1">{{ getSortIcon('priority') }}</span></button>
            <span class="text-center cursor-default block w-full">Action</span>
          </div>

          <div v-if="sortedOrders.length === 0" class="py-10 text-center text-sm opacity-50">No orders found. Create one to get started.</div>

          <div v-for="order in sortedOrders" :key="order.id"
            :class="[
                theme.tableRowOrders,
                deleteConfirmId === order.id ? '!border-red-500 !bg-red-500/10' : ''
            ]"
          >
            <div class="font-medium flex items-center gap-2 overflow-hidden min-w-0">
               <button v-if="deleteConfirmId === order.id" @click.stop="executeDelete(order.id)" class="bg-red-600 text-white text-[10px] uppercase font-bold px-2 py-1 rounded animate-pulse shadow-sm">Confirm</button>
               <span class="truncate" :title="order.name">{{ order.name }}</span>
            </div>

            <span class="font-mono text-xs truncate opacity-50">#{{ order.id }}</span>

            <div>
                <span :class="[theme.badge, getBadgeColor('status', getStatusText(order.status))]">
                    {{ getStatusText(order.status) }}
                </span>
            </div>

            <span class="text-xs truncate opacity-80">{{ formatDate(order.start_date) }}</span>
            <span class="text-xs truncate opacity-80">{{ formatDate(order.end_date) }}</span>

            <div>
                <span :class="[theme.badge, getBadgeColor('priority', getPriorityText(order.priority))]">
                    {{ getPriorityText(order.priority) }}
                </span>
            </div>

            <div class="text-right">
                <button @click.stop="handleRowAction(order.id)"
                  :class="isDeleteMode
                    ? 'px-2 py-1.5 text-xs font-medium rounded border transition-colors w-full text-center border-red-200 text-red-500 hover:bg-red-50 hover:border-red-300 dark:border-slate-400 dark:text-slate-500 dark:hover:bg-slate-200' 
                    : theme.btnAction"
                >
                  {{ !isDeleteMode ? 'Edit' : (deleteConfirmId === order.id ? 'Cancel' : 'Delete') }}
                </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>