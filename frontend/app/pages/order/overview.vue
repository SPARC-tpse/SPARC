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

const { theme, getBadgeColor } = useAppTheme();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const sortColumn = ref('id');
const sortDirection = ref('asc');
const isDeleteMode = ref(false);
const deleteConfirmId = ref(null);
const orders = ref([]);
const warningList = ref([]);
const priorityMap = { 0: 'Low', 1: 'Medium', 2: 'High' };
const statusMap = { 0: 'Planned', 1: 'Running', 2: 'Paused', 3: 'Done' };
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
});
const hasWarning = (orderId) => {
  return warningList.value.includes(Number(orderId));
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
const { connected } = useOrderWebSocket(handleOrderUpdate);

/**
 * Maps the status index of order to a status
 * @param {int} val - index of the status
 * @returns {String}
 */
function getStatusText(val) {
  return statusMap[val] || val;
}

/**
 * Maps the priority index of order to a priority
 * @param {int} val - index of priority
 * @returns {string}
 */
function getPriorityText(val) {
  return priorityMap[val] || val;
}

/**
 * formates the date in a standard format
 * @param dateString
 * @returns {string}
 */
function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('de-DE')
}

/**
 * Sorts the list of orders asc or desc for a given column
 * @param {string} column - the name of the column
 */
function sortBy(column) {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column; sortDirection.value = 'asc';
  }
}

/**
 * Gives icon depending on which column is sorted by and if it sorted asc or desc
 * @param {string} column - the name of the column
 * @returns {string|string}
 */
function getSortIcon(column) {
  if (sortColumn.value !== column) return '↕'
  return sortDirection.value === 'asc' ? '↑' : '↓'
}

/**
 * toggles the delete mode which makes the edit button to a delete button
 */
function toggleDeleteMode() {
  isDeleteMode.value = !isDeleteMode.value
  deleteConfirmId.value = null
}

/**
 * Redirects to the edit page or starts deletion of an order if delete mode is toggled
 * @param {int} id - the index of the order in the order list
 */
function handleRowAction(id) {
  if (!isDeleteMode.value) navigateTo(`/order/edit/${id}`)
  else deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
}

/**
 * Deletes an order by calling backend api with the order-id
 * @param {int} id - the index
 * @returns {Promise<void>}
 */
async function executeDelete(id) {
  try {
    await $fetch(`${API_BASE_URL}/api/order/delete/${id}/`, { method: 'DELETE' })
    orders.value = orders.value.filter(o => o.id !== id)
    deleteConfirmId.value = null
  } catch (error) {
    alert('Failed to delete order')
  }
}

/**
 * Loads all orders from the backend api
 * @returns {Promise<void>}
 */
async function loadOrders() {
  try {
    const response = await $fetch(`${API_BASE_URL}/api/order/get`, { method: 'GET' });
    orders.value = response || [];
  } catch (error) {
    console.error('API Error:', error);
  }
}

/**
 * Checks if any resources are missing(`null`) or not available and not in use
 * and adds the order number to the `warningList`
 * @returns {Promise<void>}
 */
async function loadWarnings() {
  try {
    const response = await $fetch(`${API_BASE_URL}/api/process/get`, { method: 'GET' });
    const processes = response.processes;
    console.log(processes)
    for (let i = 0; i < processes.length; i++) {
      if (processes[i].resource === null || (processes[i].resource.status !== 3 && processes[i].resource.status !== 2)) {
        console.log(processes[i]);
        warningList.value.push(processes[i].order.id);
      }
    }
  } catch (error) {
    console.error('API Error:', error);
  }
}

onMounted(() => {
  loadOrders();
  loadWarnings();
})
</script>

<template>
  <div :class="theme.pageWrapper" class="h-full min-h-0 flex flex-col">
    <!-- <Topbar title="Orders · Overview" :show-reset="false" :show-create="false" /> -->

    <main :class="theme.container">
      <section :class="theme.card">
        <!-- title, num of orders, delete toggle -->
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

        <!-- table of orders -->
        <div class="grid gap-2 overflow-x-auto">
          <!-- column names, sort buttons -->
          <div :class="theme.tableHeaderOrders">
            <button @click="sortBy('name')" :class="[theme.headerBtn, 'justify-start']">Name <span class="opacity-50 ml-1">{{ getSortIcon('name') }}</span></button>
            <button @click="sortBy('id')" :class="[theme.headerBtn, 'justify-start']">ID <span class="opacity-50 ml-1">{{ getSortIcon('id') }}</span></button>
            <button @click="sortBy('status')" :class="[theme.headerBtn, 'justify-start']">Status <span class="opacity-50 ml-1">{{ getSortIcon('status') }}</span></button>
            <button @click="sortBy('start_date')" :class="[theme.headerBtn, 'justify-start']">Start <span class="opacity-50 ml-1">{{ getSortIcon('start_date') }}</span></button>
            <button @click="sortBy('end_date')" :class="[theme.headerBtn, 'justify-start']">End <span class="opacity-50 ml-1">{{ getSortIcon('end_date') }}</span></button>
            <button @click="sortBy('priority')" :class="[theme.headerBtn, 'justify-start']">Priority <span class="opacity-50 ml-1">{{ getSortIcon('priority') }}</span></button>
            <span class="text-center cursor-default block w-full">Action</span>
          </div>

          <!-- filler -->
          <div v-if="sortedOrders.length === 0" class="py-10 text-center text-sm opacity-50">No orders found. Create one to get started.</div>

          <!-- rows -->
          <div v-for="order in sortedOrders"
            :key="order.id"
            :class="[
              theme.tableRowOrders,
              deleteConfirmId === order.id ? '!border-red-500 !bg-red-500/10' : ''
            ]"
          >
            <div class="font-medium flex items-center gap-2 overflow-hidden min-w-0">
              <span class="font-mono text-xs truncate opacity-50" v-if="hasWarning(order.id)">⚠️</span>
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