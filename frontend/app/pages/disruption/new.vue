<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()

const resourceOptions = ref([])
const typeOptions = ref([])


const formId = ref(`DIS-${Math.floor(Math.random() * 10000)}`)

const newDisruption = ref({
  name: '',
  start: '',
  end: '',
  resource: '',
  type: ''
})

const canSubmit = computed(() =>
  !!(newDisruption.value.name &&
    newDisruption.value.resource &&
    newDisruption.value.type)
)

function setNow(field) {
  const now = new Date()
  newDisruption.value[field] = now.toISOString().slice(0, 16)
}

function resetForm() {
  newDisruption.value = {
    name: '',
    start: '',
    end: '',
    resource: '',
    type: ''
  }
}

async function submitDisruption() {
  if (!canSubmit.value) return

  // 1. Prepare the data object properly
  const disruptionData = {
    ...newDisruption.value
  }

  // 2. Access runtime config properly if using Nuxt
  const config = useRuntimeConfig()
  const baseURL = config.public?.apiBase || 'http://localhost:8000/api'
  const endpoint = '/disruptions/create_disruption'

  console.log('Submitting disruption:', disruptionData)

  try {
    await $fetch(`${baseURL}${endpoint}`, {
      method: 'POST',
      body: disruptionData,
      headers: {
        'Content-Type': 'application/json',
      }
    })

    console.log('Success!')

  } catch (error) {
    console.error('API Error:', error)
    alert('Failed to create disruption. Check console.')
    return
  }

  resetForm()
  await navigateTo('/disruption/overview')
}

// Fetch options on mount
onMounted(async () => {
  const [resData, typeData] = await Promise.all([
    $fetch('http://localhost:8000/api/resources/get_resources'),
    $fetch('http://localhost:8000/api/disruptionTypes/get_disruptionTypes')
  ])
  resourceOptions.value = resData
  typeOptions.value = typeData
})

</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar title="Disruptions · New" :can-submit="canSubmit" :show-reset="true" :show-create="true"
      create-label="Create" @reset="resetForm" @submit="submitDisruption" />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name
          <input v-model="newDisruption.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID (auto)
          <input :value="formId" class="input disabled-input" disabled />
        </label>

        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">Start</label>
          <div class="flex gap-2">
            <input v-model="newDisruption.start" type="datetime-local" class="input" />
            <button type="button" @click="setNow('start')"
              class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">
              Now
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">End</label>
          <div class="flex gap-2">
            <input v-model="newDisruption.end" type="datetime-local" class="input" />
            <button type="button" @click="setNow('end')"
              class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">
              Now
            </button>
          </div>
        </div>

        <label class="flex flex-col gap-1 text-sm label-text">
          Resource
          <select v-model="newDisruption.resource" class="input">
            <option disabled value="">-- choose --</option>
            <option v-for="opt in resourceOptions" :key="opt.id" :value="opt.id">
              {{ opt.name }}
            </option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="newDisruption.type" class="input">
            <option disabled value="">-- choose --</option>
            <option v-for="opt in typeOptions" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
          </select>
        </label>
      </div>
    </main>
  </div>
</template>

<style scoped>
.input {
  @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors;
}

.dark-mode .input {
  @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500;
}

.light-mode .input {
  @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500;
}

.dark-mode .disabled-input {
  @apply bg-gray-900 text-slate-500;
}

.light-mode .disabled-input {
  @apply bg-slate-100 text-slate-500;
}

.dark-mode .label-text {
  @apply text-slate-300;
}

.light-mode .label-text {
  @apply text-slate-600;
}
</style>