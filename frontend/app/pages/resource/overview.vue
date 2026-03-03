<script setup lang="js">
import { ref, onMounted, computed } from 'vue'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Resources · Overview',
    showReset: false,
    showCreate: false,
  },
})

const { theme, getBadgeColor } = useAppTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const resources = ref([])
const isDeleteMode = ref(false)
const deleteConfirmId = ref(null)
const sortColumn = ref('id'), sortDirection = ref('asc')

const sortedResources = computed(() => {
    const copy = [...resources.value]
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

const statusMap = { 1: 'Offline', 2: 'In Use', 3: 'Available', 4: 'Maintenance' }
const getStatusText = (val) => statusMap[val] || 'Unknown'

async function fetchResources() { try { resources.value = await $fetch(`${API_BASE_URL}/api/resource/get/`) } catch (e) {} }
function toggleDeleteMode() { isDeleteMode.value = !isDeleteMode.value; deleteConfirmId.value = null; }
function handleRowAction(id) {
    if (!isDeleteMode.value) navigateTo(`/resource/edit/${id}`)
    else deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
}
async function executeDelete(id) {
    try { await $fetch(`${API_BASE_URL}/api/resource/delete/${id}/`, { method: 'DELETE' })
    resources.value = resources.value.filter(r => r.id !== id); deleteConfirmId.value = null;
    } catch (e) { alert('Delete failed') }
}
onMounted(fetchResources)
</script>

<template>
  <main :class="theme.container">
    <section :class="theme.card">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <h3 class="font-semibold text-lg">Resources Overview</h3>
          <span :class="theme.totalBadge">{{ resources.length }} total</span>
        </div>
        <div class="flex gap-2">
          <button @click="toggleDeleteMode" :class="isDeleteMode ? theme.btnDeleteModeActive : theme.btnDeleteMode">
            {{ isDeleteMode ? 'Done' : 'Delete Mode' }}
          </button>
          <NuxtLink to="/resource/new" :class="theme.btnNewEntity">+ New Resource</NuxtLink>
        </div>
      </div>

      <div class="grid gap-2 overflow-x-auto">
        <div :class="theme.tableHeaderRes">
          <button @click="sortBy('name')" :class="[theme.headerBtn, 'justify-start']">Name <span class="opacity-50 ml-1">{{ getSortIcon('name') }}</span></button>
          <button @click="sortBy('id')" :class="[theme.headerBtn, 'justify-start']">ID <span class="opacity-50 ml-1">{{ getSortIcon('id') }}</span></button>
          <button @click="sortBy('type')" :class="[theme.headerBtn, 'justify-start']">Type <span class="opacity-50 ml-1">{{ getSortIcon('type') }}</span></button>
          <button @click="sortBy('status')" :class="[theme.headerBtn, 'justify-start']">Status <span class="opacity-50 ml-1">{{ getSortIcon('status') }}</span></button>
          <span class="text-right cursor-default block w-full">Action</span>
        </div>

        <div v-for="res in sortedResources" :key="res.id" :class="[theme.tableRowRes, deleteConfirmId === res.id ? '!border-red-500 !bg-red-500/10' : '']">
          <div class="flex items-center gap-2 overflow-hidden">
             <button v-if="deleteConfirmId === res.id" @click.stop="executeDelete(res.id)" :class="theme.btnConfirmDelete">Confirm</button>
             <span class="truncate font-medium">{{ res.name }}</span>
          </div>
          <span class="font-mono text-xs opacity-50">{{ res.id }}</span>
          <span class="text-xs capitalize">{{ res.type }}</span>
          <div><span :class="[theme.badge, getBadgeColor('status', getStatusText(res.status))]">{{ getStatusText(res.status) }}</span></div>
          <div class="text-right">
            <button @click="handleRowAction(res.id)" :class="isDeleteMode ? theme.btnActionDelete : theme.btnAction">
              {{ !isDeleteMode ? 'Edit' : (deleteConfirmId === res.id ? 'Cancel' : 'Delete') }}
            </button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>