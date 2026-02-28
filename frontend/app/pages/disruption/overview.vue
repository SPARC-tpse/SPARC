<script setup lang="js">
import { ref, onMounted, computed } from 'vue'
definePageMeta({ layout: 'custom' })

const { theme, getBadgeColor } = useAppTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const disruptions = ref([])
const isDeleteMode = ref(false), deleteConfirmId = ref(null)
const sortColumn = ref('id'), sortDirection = ref('desc')

const sortedDisruptions = computed(() => {
    const copy = [...disruptions.value]
    return copy.sort((a, b) => {
        let aVal = a[sortColumn.value], bVal = b[sortColumn.value]
        if (sortColumn.value === 'start' || sortColumn.value === 'end') { aVal = new Date(aVal || 0); bVal = new Date(bVal || 0); }
        else if (typeof aVal === 'string') { aVal = aVal.toLowerCase(); bVal = bVal.toLowerCase(); }
        if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
        return sortDirection.value === 'asc' ? 1 : -1
    })
})

function sortBy(col) {
    if (sortColumn.value === col) sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    else { sortColumn.value = col; sortDirection.value = 'asc'; }
}
function getSortIcon(col) { return sortColumn.value !== col ? '↕' : (sortDirection.value === 'asc' ? '↑' : '↓') }
const formatDate = (d) => d ? new Date(d).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'

async function fetchDisruptions() { try { disruptions.value = await $fetch(`${API_BASE_URL}/api/disruption/list`) } catch (e) {} }
function toggleDeleteMode() { isDeleteMode.value = !isDeleteMode.value; deleteConfirmId.value = null; }
function handleAction(id) {
    if (!isDeleteMode.value) navigateTo(`/disruption/edit/${id}`)
    else deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
}
async function executeDelete(id) {
    try { await $fetch(`${API_BASE_URL}/api/disruption/delete/${id}`, { method: 'DELETE' })
    disruptions.value = disruptions.value.filter(d => d.id !== id); deleteConfirmId.value = null;
    } catch (e) { alert('Failed to delete') }
}
onMounted(fetchDisruptions)
</script>

<template>
  <div :class="theme.pageWrapper">
    <Topbar title="Disruptions · Overview" :show-reset="false" :show-create="false" />
    <main :class="theme.container">
      <section :class="theme.card">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold text-lg">Disruptions overview</h3>
            <span :class="theme.totalBadge">{{ disruptions.length }} total</span>
          </div>
          <div class="flex gap-2">
            <button @click="toggleDeleteMode" :class="isDeleteMode ? 'bg-slate-700 text-white border-slate-600 px-3 py-2 rounded-lg text-sm font-semibold border' : theme.btnDeleteMode">{{ isDeleteMode ? 'Done' : 'Delete Mode' }}</button>
            <NuxtLink to="/disruption/new" class="px-3 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-pink-500 shadow-md">+ New Disruption</NuxtLink>
          </div>
        </div>

        <div class="grid gap-2 overflow-x-auto">
          <div :class="theme.tableHeaderDisruptions">
            <button @click="sortBy('name')" :class="[theme.headerBtn, 'justify-start']">Name <span class="opacity-50 ml-1">{{ getSortIcon('name') }}</span></button>
            <button @click="sortBy('id')" :class="[theme.headerBtn, 'justify-start']">ID <span class="opacity-50 ml-1">{{ getSortIcon('id') }}</span></button>
            <button @click="sortBy('start')" :class="[theme.headerBtn, 'justify-start']">Start <span class="opacity-50 ml-1">{{ getSortIcon('start') }}</span></button>
            <button @click="sortBy('end')" :class="[theme.headerBtn, 'justify-start']">End <span class="opacity-50 ml-1">{{ getSortIcon('end') }}</span></button>
            <button @click="sortBy('resource')" :class="[theme.headerBtn, 'justify-start']">Resource <span class="opacity-50 ml-1">{{ getSortIcon('resource') }}</span></button>
            <button @click="sortBy('type')" :class="[theme.headerBtn, 'justify-start']">Type <span class="opacity-50 ml-1">{{ getSortIcon('type') }}</span></button>
            <span class="text-right block w-full">Action</span>
          </div>

          <div v-for="d in sortedDisruptions" :key="d.id" :class="[theme.tableRowDisruptions, deleteConfirmId === d.id ? '!border-red-500 !bg-red-500/10' : '']">
            <div class="font-medium flex items-center gap-2 overflow-hidden">
               <button v-if="deleteConfirmId === d.id" @click.stop="executeDelete(d.id)" class="bg-red-600 text-white text-[10px] font-bold uppercase px-2 py-1 rounded shadow-sm">Confirm</button>
               <span class="truncate">{{ d.name }}</span>
            </div>
            <span class="font-mono text-xs opacity-50">#{{ d.id }}</span>
            <span class="text-xs opacity-80">{{ formatDate(d.start) }}</span>
            <span class="text-xs opacity-80">{{ formatDate(d.end) }}</span>
            <span class="text-xs truncate">{{ d.resource }}</span>
            <div><span :class="[theme.badge, getBadgeColor('disruption', d.type)]">{{ d.type }}</span></div>
            <div class="text-right">
              <button @click="handleAction(d.id)" :class="isDeleteMode ? 'border-red-200 text-red-500 hover:bg-red-50 w-full px-2 py-1.5 text-xs font-medium rounded border transition-colors' : theme.btnAction">
                {{ isDeleteMode ? (deleteConfirmId === d.id ? 'Cancel' : 'Delete') : 'Edit' }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>