<script setup lang="js">
import { ref, onMounted, computed } from 'vue'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Workers · Overview',
    showReset: false,
    showCreate: false,
  },
})

const { theme } = useAppTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const workers = ref([])
const isDeleteMode = ref(false)
const deleteConfirmId = ref(null)

// --- SORTIER LOGIK ---
const sortColumn = ref('id')
const sortDirection = ref('asc')

const sortedWorkers = computed(() => {
    const copy = [...workers.value]
    return copy.sort((a, b) => {
        let aVal = a[sortColumn.value], bVal = b[sortColumn.value]
        if (typeof aVal === 'string') { aVal = aVal.toLowerCase(); bVal = bVal.toLowerCase(); }
        if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
        return sortDirection.value === 'asc' ? 1 : -1
    })
})

function sortBy(col) {
    if (sortColumn.value === col) sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    else { sortColumn.value = col; sortDirection.value = 'asc'; }
}
function getSortIcon(col) { return sortColumn.value !== col ? '↕' : (sortDirection.value === 'asc' ? '↑' : '↓') }
// --------------------

async function loadWorkers() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/worker/get/`)
        workers.value = response || []
    } catch (error) { console.error('API Error:', error) }
}

function toggleDeleteMode() { isDeleteMode.value = !isDeleteMode.value; deleteConfirmId.value = null; }

function handleRowAction(id) {
    if (!isDeleteMode.value) navigateTo(`/worker/edit/${id}`)
    else deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
}

async function executeDelete(id) {
    try {
        await $fetch(`${API_BASE_URL}/api/worker/delete/${id}/`, { method: 'DELETE' })
        workers.value = workers.value.filter(o => o.id !== id)
        deleteConfirmId.value = null
    } catch (error) { alert('Failed to delete worker') }
}

onMounted(loadWorkers)
</script>

<template>
  <div :class="theme.pageWrapper">
    <!-- <Topbar title="Workers · Overview" :show-reset="false" :show-create="false" /> -->

    <main :class="theme.container">
      <section :class="theme.card">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold text-lg">Workers overview</h3>
            <span :class="theme.totalBadge">{{ workers.length }} total</span>
          </div>
          <div class="flex gap-2">
            <button @click="toggleDeleteMode" :class="isDeleteMode ? 'bg-slate-700 text-white border-slate-600 px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm' : theme.btnDeleteMode">
              {{ isDeleteMode ? 'Done' : 'Delete Mode' }}
            </button>
            <NuxtLink to="/worker/new" class="px-3 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-pink-500 shadow-md transition-all hover:shadow-lg">+ New Worker</NuxtLink>
          </div>
        </div>

        <div class="grid gap-2 overflow-x-auto">
          <div :class="theme.tableHeaderWorkers">
            <button @click="sortBy('name')" :class="[theme.headerBtn, 'justify-start']">Name <span class="opacity-50 ml-1">{{ getSortIcon('name') }}</span></button>
            <button @click="sortBy('id')" :class="[theme.headerBtn, 'justify-start']">ID <span class="opacity-50 ml-1">{{ getSortIcon('id') }}</span></button>
            <span class="text-center cursor-default block w-full">Action</span>
          </div>

          <div v-if="sortedWorkers.length === 0" class="py-10 text-center text-sm opacity-50">No workers found.</div>

          <div v-for="worker in sortedWorkers" :key="worker.id"
               :class="[theme.tableRowWorkers, deleteConfirmId === worker.id ? '!border-red-500 !bg-red-500/10' : '']">
            <div class="font-medium flex items-center gap-2 overflow-hidden">
               <button v-if="deleteConfirmId === worker.id" @click.stop="executeDelete(worker.id)" class="bg-red-600 text-white text-[10px] uppercase font-bold px-2 py-1 rounded animate-pulse shadow-sm">Confirm</button>
               <span class="truncate">{{ worker.name }}</span>
            </div>
            <span class="font-mono text-xs opacity-50">#{{ worker.id }}</span>
            <div class="text-right">
              <button @click="handleRowAction(worker.id)" :class="isDeleteMode ? 'border-red-200 text-red-500 hover:bg-red-50 w-full px-2 py-1.5 text-xs font-medium rounded border transition-colors text-center' : theme.btnAction">
                {{ !isDeleteMode ? 'Edit' : (deleteConfirmId === worker.id ? 'Cancel' : 'Delete') }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>