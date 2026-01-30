<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const { createResource, fetchResourceTypes } = useApi()

const typeOptions = ref([])
const resource = ref({
  name: '',
  type: '',
  status: 'available'
})

const canSubmit = computed(() => !!(resource.value.name && resource.value.type))

onMounted(async () => {
  try {
    typeOptions.value = await fetchResourceTypes()
  } catch (err) {
    console.error("Fehler beim Laden der Resource-Typen:", err)
  }
})

async function submitForm() {
  if (!canSubmit.value) return
  try {
    await createResource(resource.value)
    await navigateTo('/resource/overview')
  } catch (err) {
    console.error("Fehler beim Erstellen:", err.response?._data || err)
  }
}

function cancel() {
  navigateTo('/resource/overview')
}
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar :title="isEdit ? 'Resources · Edit' : 'Resources · New'" :can-submit="canSubmit" :show-reset="true"
      :show-create="true" :create-label="isEdit ? 'Update' : 'Create'" @reset="cancel" @submit="submitForm" />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource Name
          <input v-model="resource.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="resource.id || 'Auto-generated'" class="input disabled-input" disabled />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="resource.type" class="input">
            <option disabled value="">-- choose type --</option>
            <option v-for="t in typeOptions" :key="t.id" :value="t.id">
              {{ t.name }}
            </option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="resource.status" class="input">
              <option disabled value="">-- choose type --</option>
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

.dark-mode {
  @apply min-h-screen bg-slate-950 text-slate-100;
}

.light-mode {
  @apply min-h-screen bg-slate-50 text-slate-900;
}
</style>