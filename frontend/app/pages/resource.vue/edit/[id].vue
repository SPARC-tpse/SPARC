<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRoute } from 'vue-router'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const resourceId = route.params.id

// Form Object
const resource = ref({
  id: resourceId,
  name: '',
  type: '',
  status: ''
})

// Validation: Require name, type, and status to enable update
const canSubmit = computed(() =>
  resource.value.name && resource.value.type && resource.value.status
)

async function loadResource() {
  // TODO: Fetch from backend
  // const response = await $fetch(`/api/resources/${resourceId}`)
  // resource.value = response.data

  // Mock data for initial load
  resource.value = {
    id: resourceId,
    name: 'Excavator 01',
    type: 'machinery',
    status: 'available'
  }
}

async function updateResource() {
  if (!canSubmit.value) return

  // TODO: Send update to backend
  console.log('Updating resource:', resource.value)

  // Navigate back to overview
  await navigateTo('/resource/overview')
}

function cancelEdit() {
  navigateTo('/resource/overview')
}

onMounted(() => {
  loadResource()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Resources · Edit"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Update"
      @reset="cancelEdit"
      @submit="updateResource"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource Name
          <input v-model="resource.name" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="resource.id" class="input disabled-input" disabled />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="resource.type" class="input">
            <option disabled value="">-- choose type --</option>
            <option value="machinery">Machinery</option>
            <option value="worker">Worker</option>
            <option value="tool">Tool</option>
            <option value="vehicle">Vehicle</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="resource.status" class="input">
            <option disabled value="">-- choose status --</option>
            <option value="available">Available / Ready</option>
            <option value="in-use">In Use / Active</option>
            <option value="maintenance">Under Maintenance</option>
            <option value="offline">Offline / Unavailable</option>
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