<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
    layout: 'custom'
})


const { isDarkMode } = useTheme()

const newResource = ref({
    name: "",
    type: "",
    status: ""
})

const formId = ref(`DIS-${Math.floor(Math.random() * 10000)}`)
const canSubmit = computed(() => newResource.value.name && newResource.value.type)

const types = ref([])

function resetForm() {
    newResource.value = {
        name: '',
        type: '',
        status: ''
    }
}
async function submitResource() {
    if (!canSubmit.value) return

    const resource = {
        id: formId.value,
        ...newResource.value
    }

    // TODO: Send to backend
    console.log('Submitting resource:', resource)

    resetForm()

    // Navigate to overview
    await navigateTo('/resource/overview')
}

</script>


<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Resources · New"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Create"
      @reset="resetForm"
      @submit="submitResource"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource Name
          <input v-model="newResource.name" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          ID (auto)
          <input :value="formId" class="input disabled-input" disabled />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="newResource.type" class="input">
            <option disabled value="">-- choose type --</option>
            <option value="machinery">Machinery</option>
            <option value="worker">Worker</option>
            <option value="tool">Tool</option>
            <option value="vehicle">Vehicle</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="newResource.status" class="input">
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