<script setup lang="js">
    import { ref, onMounted } from 'vue'
    import { useTheme } from '~/composables/useTheme'
    import { useOrderWebSocket } from '~/composables/useOrderWebSocket'

    definePageMeta({
      layout: 'custom'
    })

    const { isDarkMode } = useTheme()
    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;

    // Sorting state
    const sortColumn = ref('id') // Default sort by ID
    const sortDirection = ref('asc') // 'asc' or 'desc'

    // Delete state
    const isDeleteMode = ref(false) // Default is false (so Edit Mode is default)
    const deleteConfirmId = ref(null)

    const orders = ref([
      {
        id: 'ORD-1042',
        name: 'Test Order',
        start_date: '2025-11-27',
        end_date: '2025-11-28',
        target: 1200,
        product: 'Ventil platinen',
        status: 'Running',
        priority: 'High',
        comments: 'set-up phase done.',
        process: [
          { worker: 'Lena', resource: 'test resource', notes: 'test note' },
          { worker: 'Max', resource: 'test resource', notes: 'test note2' }
        ]
      }
    ])

    // Computed sorted orders
    const sortedOrders = computed(() => {
        const ordersCopy = [...orders.value]

        return ordersCopy.sort((a, b) => {
            let aValue = a[sortColumn.value]
            let bValue = b[sortColumn.value]

            // Handle different data types
            if (sortColumn.value === 'priority') {
                // Convert priority to number for sorting
                const priorityMap = { 'High': 3, 'Medium': 2, 'Low': 1 }
                aValue = priorityMap[aValue] || 0
                bValue = priorityMap[bValue] || 0
            } else if (sortColumn.value === 'start_date' || sortColumn.value === 'end_date') {
                // Convert dates for comparison
                aValue = new Date(aValue)
                bValue = new Date(bValue)
            } else if (typeof aValue === 'string') {
                // Case-insensitive string comparison
                aValue = aValue.toLowerCase()
                bValue = bValue.toLowerCase()
            }

            // Compare values
            if (aValue < bValue) {
                return sortDirection.value === 'asc' ? -1 : 1
            }
            if (aValue > bValue) {
                return sortDirection.value === 'asc' ? 1 : -1
            }
            return 0
        })
    })

    function sortBy(column) {
        if (sortColumn.value === column) {
            // Toggle direction if same column
            sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
        } else {
            // New column, default to ascending
            sortColumn.value = column
            sortDirection.value = 'asc'
        }
    }

    // Get sort indicator icon
    function getSortIcon(column) {
        if (sortColumn.value !== column) return '↕'
        return sortDirection.value === 'asc' ? '↑' : '↓'
    }

    // Handle real-time updates
    const handleOrderUpdate = async (data) => {
      console.log('Order update received:', data)

      if (data.action === 'created') {
        // Add new order to the list
        orders.value.push(data.data)
      } else if (data.action === 'updated') {
        // Update existing order
        const index = orders.value.findIndex(o => o.id === data.data.id)
        if (index !== -1) {
          orders.value[index] = data.data
        }
      } else if (data.action === 'deleted') {
        // Remove order from list
        orders.value = orders.value.filter(o => o.id !== data.data.id)
      }
    }

    // Connect to WebSocket
    const { connected } = useOrderWebSocket(handleOrderUpdate)

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

    // 1. Delete Mode Toggle (Top)
    function toggleDeleteMode() {
      isDeleteMode.value = !isDeleteMode.value
      // Close all open confirmations when toggling
      deleteConfirmId.value = null
    }

    // 2. Row Button Logic
    function handleRowAction(id) {
      if (!isDeleteMode.value) {
        // STANDARD: Edit Mode (Delete Mode is OFF)
        console.log(`Edit Order ${id}`)
        navigateTo(`/order/edit/${id}`)
      } else {
        // DELETE MODE (Delete Mode is ON)
        if (deleteConfirmId.value === id) {
          // Was already in Confirm status -> Cancel
          deleteConfirmId.value = null
        } else {
          // Starts the deletion process for this row
          deleteConfirmId.value = id
        }
      }
    }

    // 3. Actual deletion (Confirm button next to name)
    async function executeDelete(id) {
        console.log(`Deleting Order ${id}`)
        try {
            const response = await $fetch(`${API_BASE_URL}/api/order/delete/${id}`, {
                method: 'DELETE'
            })
            return response
        } catch (error) {
            console.error('API Error:', error)
            alert('Failed to delete order')
        }

        // TODO: refresh does not work for some reason
        orders.value = orders.value.filter(o => o.id !== id)
        deleteConfirmId.value = null
    }

    async function fetchOrders() {
        console.log("Test fetch order");
        try {
            const response = await $fetch(`${API_BASE_URL}/api/order/get`, {
                method: 'GET'
            });
            console.log("response data:");
            console.log(response);
            orders.value = response;
        } catch (error) {
            console.error('API Error:', error);
            alert('Error: Failed to load Orders.');
            throw error;
        }
    }

    onMounted(() => {
      fetchOrders();
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

          <div class="flex gap-2">
            <button
              @click="toggleDeleteMode"
              class="px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm"
              :class="[
                // If Delete Mode is ON -> Button looks 'pressed' or active
                isDeleteMode
                  ? 'bg-slate-200 text-slate-800 border-slate-300'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-red-400 hover:text-red-600',

                // Dark Mode variants
                isDarkMode && isDeleteMode ? 'bg-slate-700 text-white border-slate-600' : '',
                isDarkMode && !isDeleteMode ? 'bg-slate-800 text-slate-200 border-slate-700 hover:border-red-500 hover:text-red-400' : ''
              ]"
            >
              {{ isDeleteMode ? 'Done deleting' : 'Delete mode' }}
            </button>

            <NuxtLink
              to="/order/new"
              class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg"
            >
              + New Order
            </NuxtLink>
          </div>
        </div>

        <div class="grid gap-2">
          <div class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,120px] gap-2 text-xs"
               :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <button
              @click="sortBy('name')"
              class="text-left hover:text-pink-500 transition-colors flex items-center gap-1"
            >
              Name {{ getSortIcon('name') }}
            </button>
            <button
              @click="sortBy('id')"
              class="text-left hover:text-pink-500 transition-colors flex items-center gap-1"
            >
              ID {{ getSortIcon('id') }}
            </button>
            <button
              @click="sortBy('status')"
              class="text-left hover:text-pink-500 transition-colors flex items-center gap-1"
            >
              Status {{ getSortIcon('status') }}
            </button>
            <button
              @click="sortBy('start_date')"
              class="text-left hover:text-pink-500 transition-colors flex items-center gap-1"
            >
              Start {{ getSortIcon('start_date') }}
            </button>
            <button
              @click="sortBy('end_date')"
              class="text-left hover:text-pink-500 transition-colors flex items-center gap-1"
            >
              End {{ getSortIcon('end_date') }}
            </button>
            <button
              @click="sortBy('priority')"
              class="text-left hover:text-pink-500 transition-colors flex items-center gap-1"
            >
              Priority {{ getSortIcon('priority') }}
            </button>
            <span>Action</span>
          </div>

          <!--
          <div class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,120px] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <span>Name</span><span>ID</span><span>Status</span><span>Start</span><span>End</span><span>Priority</span><span>Action</span>
          </div>
          -->

          <div
            v-for="order in sortedOrders"
            :key="order.id"
            class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,120px] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
            :class="[
              isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-slate-50 hover:bg-slate-100',
              // Highlight row red if deletion needs confirmation
              deleteConfirmId === order.id && !isDarkMode ? 'bg-red-50 border-red-100' : '',
              deleteConfirmId === order.id && isDarkMode ? 'bg-red-900/10 border-red-900/30' : ''
            ]"
          >
            <!-- name + delete confirm button -->
            <span class="font-medium flex items-center gap-2 overflow-hidden">
               <button
                  v-if="deleteConfirmId === order.id"
                  @click="executeDelete(order.id)"
                  class="bg-red-600 text-white text-[10px] px-2 py-1 rounded animate-pulse hover:bg-red-700 shrink-0 shadow-sm"
               >
                 Confirm
               </button>
               <span class="truncate">{{ order.name }}</span>
            </span>

            <!-- id -->
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ order.id }}</span>

            <!-- status -->
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('status', order.status)">
                {{ order.status }}
              </span>
            </span>

            <!-- start_date -->
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ order.start_date }}</span>

            <!-- end_date -->
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ order.end_date }}</span>

            <!-- priority -->
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('priority', order.priority)">
                {{ order.priority }}
              </span>
            </span>

            <button
              @click="handleRowAction(order.id)"
              class="px-2 py-1 text-xs rounded border transition-colors w-full text-center"
              :class="[
                // 1. STANDARD: Edit Mode (Indigo/Blue) - If Delete Mode is OFF
                !isDeleteMode && isDarkMode ? 'border-indigo-800 text-indigo-200 hover:bg-indigo-900' : '',
                !isDeleteMode && !isDarkMode ? 'border-indigo-300 text-indigo-700 hover:bg-indigo-50' : '',

                // 2. DELETE MODE: Cancel State (Gray) - If Delete Mode is ON AND row is currently being confirmed
                isDeleteMode && deleteConfirmId === order.id && isDarkMode ? 'border-slate-500 text-slate-400 hover:bg-slate-800' : '',
                isDeleteMode && deleteConfirmId === order.id && !isDarkMode ? 'border-slate-400 text-slate-600 hover:bg-slate-200' : '',

                // 3. DELETE MODE: Init State (Red) - If Delete Mode is ON but row is still normal
                isDeleteMode && deleteConfirmId !== order.id && isDarkMode ? 'border-red-900 text-red-400 hover:bg-red-900/30' : '',
                isDeleteMode && deleteConfirmId !== order.id && !isDarkMode ? 'border-red-200 text-red-600 hover:bg-red-50' : ''
              ]"
            >
              {{
                !isDeleteMode
                  ? 'Edit'
                  : (deleteConfirmId === order.id ? 'Cancel deletion' : 'Delete')
              }}
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