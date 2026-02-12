<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const disruptionId = route.params.id

const resources = ref([])
const types = ref([])

const disruption = ref({
  id: disruptionId,
  name: '',
  start: '',
  end: '',
  resource: '',
  type: ''
})

const canSubmit = computed(() => disruption.value.name && disruption.value.resource)

function setNow(field) {
  disruption.value[field] = new Date().toISOString().slice(0, 16)
}

async function loadData() {
  try {
    const [resData, typeData, dispData] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/resource/list`),
      $fetch(`${API_BASE_URL}/api/disruption-type/list`),
      $fetch(`${API_BASE_URL}/api/disruption/get/${disruptionId}`)
    ])

    resources.value = resData
    types.value = typeData

    const toInputFormat = (dateStr) => {
      if (!dateStr) return ''
      return dateStr.slice(0, 16)
    }

    disruption.value = {
      ...dispData,
      start: toInputFormat(dispData.start),
      end: toInputFormat(dispData.end),
      resource: dispData.resource,
      type: dispData.type
    }
  } catch (e) {
    console.error('Fehler beim Laden:', e)
  }
}

async function updateDisruption() {
  if (!canSubmit.value) return
  try {
    await $fetch(`${API_BASE_URL}/api/disruption/put/${disruptionId}`, {
      method: 'PUT',
      body: disruption.value
    })
    await navigateTo('/disruption/overview')
  } catch (e) {
    console.error('Update failed:', e)
  }
}

function cancelEdit() { navigateTo('/disruption/overview') }

onMounted(() => {
  loadData()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Disruptions · Edit"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Update"
      @reset="cancelEdit"
      @submit="updateDisruption"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name <input v-model="disruption.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID <input :value="disruption.id" class="input disabled-input" disabled />
        </label>
        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">Start</label>
          <div class="flex gap-2">
            <input v-model="disruption.start" type="datetime-local" class="input" />
            <button type="button" @click="setNow('start')" class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap" :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">Now</button>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">End</label>
          <div class="flex gap-2">
            <input v-model="disruption.end" type="datetime-local" class="input" />
            <button type="button" @click="setNow('end')" class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap" :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">Now</button>
          </div>
        </div>
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource
          <select v-model="disruption.resource" class="input">
            <option disabled value="">-- choose --</option>
            <option v-for="r in resources" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="disruption.type" class="input">
            <option disabled value="">-- choose --</option>
            <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </label>
      </div>
    </main>
  </div>
</template>