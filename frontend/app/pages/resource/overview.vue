<script setup lang="js">
import { ref, onMounted } from 'vue'
import { useRouter } from '#app'
import { useTheme } from '~/composables/useTheme'

definePageMeta({ layout: 'custom' })

const { isDarkMode } = useTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const resources = ref([])
const isDeleteMode = ref(false)
const deleteConfirmId = ref(null)

const statusMap = { 1: 'Offline', 2: 'In Use', 3: 'Available', 4: 'Maintenance' }

function getStatusText(val) { return statusMap[val] || 'Unknown' }

async function fetchResources() {
    try {
        resources.value = await $fetch(`${API_BASE_URL}/api/resource/list`)
    } catch (e) { console.error(e) }
}

function toggleDeleteMode() {
    isDeleteMode.value = !isDeleteMode.value
    deleteConfirmId.value = null
}

function handleRowAction(id) {
    if (!isDeleteMode.value) router.push(`/resource/edit/${id}`)
    else deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
}

async function executeDelete(id) {
    try {
        await $fetch(`${API_BASE_URL}/api/resource/delete/${id}`, { method: 'DELETE' })
        resources.value = resources.value.filter(r => r.id !== id)
        deleteConfirmId.value = null
    } catch (e) { alert('Delete failed') }
}

onMounted(fetchResources)
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'" class="min-h-screen">
    <Topbar title="Resources · Overview" :show-reset="false" :show-create="false" />

    <main class="max-w-5xl mx-auto p-6">
      <section
        class="rounded-xl border p-4 space-y-3 shadow-lg transition-all duration-300"
        :class="isDarkMode
          ? 'border-gray-700 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold text-lg">Resources Overview</h3>
            <span class="text-xs px-2 py-1 rounded-md bg-slate-500/10 text-slate-500">
              {{ resources.length }} total
            </span>
          </div>
          <div class="flex gap-2">
            <button
              @click="toggleDeleteMode"
              class="px-3 py-2 rounded-lg text-sm font-semibold border transition-all"
              :class="isDeleteMode
                ? 'bg-slate-700 text-white border-slate-600'
                : (isDarkMode ? 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50')"
            >
              {{ isDeleteMode ? 'Done' : 'Delete Mode' }}
            </button>
            <NuxtLink
              to="/resource/new"
              class="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg active:scale-95"
            >
              + New Resource
            </NuxtLink>
          </div>
        </div>

        <div class="grid gap-2">
          <div
            class="grid grid-cols-[1.5fr,1fr,1fr,1fr,100px] gap-2 text-[10px] font-bold uppercase tracking-wider px-3"
            :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'"
          >
            <span>Name</span><span>ID</span><span>Type</span><span>Status</span><span class="text-right">Action</span>
          </div>

          <div
            v-for="res in resources"
            :key="res.id"
            class="grid grid-cols-[1.5fr,1fr,1fr,1fr,100px] gap-2 items-center rounded-lg border p-3 text-sm transition-all duration-200" 
            :class="[
                isDarkMode ? 'border-gray-700 bg-slate-800/40 hover:bg-slate-800/60' : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100/50',
                deleteConfirmId === res.id ? '!border-red-500 !bg-red-500/10' : ''
            ]"
          >
            <div class="flex items-center gap-2 overflow-hidden">
               <button
                v-if="deleteConfirmId === res.id"
                @click.stop="executeDelete(res.id)"
                class="bg-red-600 text-white text-[10px] font-bold uppercase px-2 py-1 rounded animate-pulse"
               >
                 Confirm
               </button>
               <span class="truncate font-medium">{{ res.name }}</span>
            </div>

            <span class="text-xs font-mono opacity-50">#{{ res.id }}</span>

            <span class="text-xs capitalize">{{ res.type }}</span>

            <div>
              <span
                class="px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-tight inline-block shadow-sm"
                :class="{
                  'bg-emerald-600 text-white': res.status==3,
                  'bg-indigo-600 text-white': res.status==2,
                  'bg-amber-500 text-white': res.status==4,
                  'bg-red-600 text-white': res.status==1
                }"
              >
                {{ getStatusText(res.status) }}
              </span>
            </div>

            <div class="text-right">
              <button
                @click="handleRowAction(res.id)"
                class="px-3 py-1 text-xs rounded border transition-colors font-medium"
                :class="isDeleteMode
                  ? 'border-red-500 text-red-500 hover:bg-red-500 hover:text-white'
                  : 'border-indigo-500/50 text-indigo-500 hover:bg-indigo-500 hover:text-white'"
              >
                {{ !isDeleteMode ? 'Edit' : (deleteConfirmId === res.id ? 'Cancel' : 'Delete') }}
              </button>
            </div>
          </div>

          <div v-if="resources.length === 0" class="text-center py-12 opacity-40 text-sm italic">
            No resources found. Click "+ New" to create one.
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