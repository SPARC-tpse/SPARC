<script setup lang="js">
import { ref, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const disruptions = ref([])
const isDeleteMode = ref(false)
const deleteConfirmId = ref(null)

async function fetchDisruptions() {
  try {

    const response = await $fetch(`${API_BASE_URL}/api/disruption/list`)
    disruptions.value = response || []
    console.log('Backend Data:', disruptions.value)
  } catch (error) {
    console.error('Failed to fetch disruptions:', error)
  }
}

onMounted(() => {
  fetchDisruptions()
})

function toggleDeleteMode() {
  isDeleteMode.value = !isDeleteMode.value
  deleteConfirmId.value = null
}

function handleAction(id) {
  if (!isDeleteMode.value) {
    navigateTo(`/disruption/edit/${id}`)
  } else {
    deleteConfirmId.value = (deleteConfirmId.value === id) ? null : id
  }
}

async function executeDelete(id) {
  try {
    await $fetch(`${API_BASE_URL}/api/disruption/delete/${id}`, { method: 'DELETE' })
    disruptions.value = disruptions.value.filter(d => d.id !== id)
    deleteConfirmId.value = null
  } catch (e) {
    alert('Failed to delete disruption')
  }
}

onMounted(() => {
  fetchDisruptions()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Disruptions · Overview"
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
            <h3 class="font-semibold">Disruptions overview</h3>
            <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
              {{ disruptions.length }} total
            </span>
          </div>
          <div class="flex gap-2">
            <button
              @click="toggleDeleteMode"
              class="px-3 py-2 rounded-lg text-sm font-semibold border transition-all"
              :class="isDeleteMode
                ? 'bg-slate-700 text-white border-slate-600'
                : (isDarkMode ? 'bg-slate-800 text-slate-200 border-slate-700' : 'bg-white text-slate-700 border-slate-200')"
            >
              {{ isDeleteMode ? 'Done' : 'Delete Mode' }}
            </button>
            <NuxtLink
              to="/disruption/new"
              class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg"
            >
              + New Disruption
            </NuxtLink>
          </div>
        </div>

        <div class="grid gap-2">
          <div class="grid grid-cols-[1.2fr,1fr,1fr,1fr,1fr,0.8fr,80px] gap-2 text-xs"
               :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <span>Name</span>
            <span>ID</span>
            <span>Start</span>
            <span>End</span>
            <span>Resource</span>
            <span>Type</span>
            <span>Action</span>
          </div>

          <div
            v-for="disruption in disruptions"
            :key="disruption.id"
            class="grid grid-cols-[1.2fr,1fr,1fr,1fr,1fr,0.8fr,80px] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
            :class="[
              isDarkMode ? 'border-gray-700 bg-gray-700' : 'border-slate-200 bg-slate-50 hover:bg-slate-100',
              deleteConfirmId === disruption.id ? '!border-red-500 !bg-red-500/10' : ''
            ]"
          >
            <div class="font-medium flex items-center gap-2 overflow-hidden">
               <button v-if="deleteConfirmId === disruption.id" @click.stop="executeDelete(disruption.id)" class="bg-red-600 text-white text-[10px] uppercase font-bold px-2 py-1 rounded">Confirm</button>
               <span class="truncate">{{ disruption.name }}</span>
            </div>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">#{{ disruption.id }}</span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">
              {{ new Date(disruption.start).toLocaleString('en-GB', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) }}
            </span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">
              {{ disruption.end ? new Date(disruption.end).toLocaleString('en-GB', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—' }}
            </span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ disruption.resource }}</span>
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold bg-amber-600 text-amber-100">
                {{ disruption.type }}
              </span>
            </span>
            <button
              @click="handleAction(disruption.id)"
              class="px-2 py-1 text-xs rounded border transition-colors"
              :class="isDeleteMode
                ? 'border-red-500 text-red-500 hover:bg-red-500/10'
                : (isDarkMode ? 'border-gray-600 hover:bg-gray-600 text-slate-200' : 'border-slate-300 hover:bg-slate-200 text-slate-700')"
            >
              {{ isDeleteMode ? (deleteConfirmId === disruption.id ? 'Cancel' : 'Delete') : 'Edit' }}
            </button>
          </div>
          <div v-if="disruptions.length === 0" class="text-center py-8 opacity-50 text-sm">No disruptions found.</div>
        </div>
      </section>
    </main>
  </div>
</template>