<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const disruptionId = route.params.id

const resources = ref([
  { id: 1, name: 'Machine A' },
  { id: 2, name: 'Conveyor' }
])

const types = ref([
  { id: 1, name: 'Error' },
  { id: 2, name: 'Maintenance' }
])

const disruption = ref({
  id: disruptionId,
  name: '',
  start: '',
  end: '',
  resource: '',
  type: ''
})

const canSubmit = computed(() =>
  disruption.value.name && disruption.value.resource
)

function setNow(field) {
  const now = new Date()
  disruption.value[field] = now.toISOString().slice(0, 16)
}

async function loadDisruption() {
  // TODO: Fetch from backend
  // const response = await $fetch(`/api/disruptions/${disruptionId}`)
  // disruption.value = response.data

  // Mock data for now
  disruption.value = {
    id: disruptionId,
    name: 'Machine Malfunction',
    start: '2025-12-27T10:00',
    end: '2025-12-27T12:30',
    resource: 1,
    type: 1
  }
}

async function updateDisruption() {
  if (!canSubmit.value) return

  // TODO: Send to backend
  console.log('Updating disruption:', disruption.value)

  // Navigate back to overview
  await navigateTo('/disruption/overview')
}

function cancelEdit() {
  navigateTo('/disruption/overview')
}

onMounted(() => {
  loadDisruption()
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
          Name
          <input v-model="disruption.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="disruption.id" class="input disabled-input" disabled />
        </label>

        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">Start</label>
          <div class="flex gap-2">
            <input v-model="disruption.start" type="datetime-local" class="input" />
            <button
              type="button"
              @click="setNow('start')"
              class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'"
            >
              Now
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">End</label>
          <div class="flex gap-2">
            <input v-model="disruption.end" type="datetime-local" class="input" />
            <button
              type="button"
              @click="setNow('end')"
              class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'"
            >
              Now
            </button>
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