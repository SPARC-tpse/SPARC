Um eine „Reset“-Funktionalität zu bauen, die die ursprünglichen Daten wiederherstellt, müssen wir die vom Server geladenen Daten in einer separaten Variable (einem „Snapshot“) speichern.

Hier ist das angepasste Script und Template:

1. Das Script mit Snapshot-Logik
Wir fügen eine originalData-Variable hinzu, die wir befüllen, sobald die Daten erfolgreich vom Server geladen wurden.

JavaScript
<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRoute } from 'vue-router'

definePageMeta({ layout: 'custom' })

const { isDarkMode } = useTheme()
const route = useRoute()
const disruptionId = route.params.id

const { fetchResources, fetchDisruptionTypes, fetchDisruptions, saveDisruption } = useApi()

const disruption = ref({
  id: disruptionId,
  name: '',
  start: '',
  end: '',
  resource: '',
  type: ''
})

const originalData = ref(null)

const resourceOptions = ref([])
const typeOptions = ref([])
const canSubmit = computed(() => !!(disruption.value.name && disruption.value.resource))

function setNow(field) {
  const now = new Date()
  disruption.value[field] = now.toISOString().slice(0, 16)
}

function resetToOriginal() {
  if (originalData.value) {
    disruption.value = JSON.parse(JSON.stringify(originalData.value))
  }
}

async function submitForm() {
  if (!canSubmit.value) return
  try {
    await saveDisruption(disruption.value, disruptionId)
    await navigateTo('/disruption/overview')
  } catch (err) {
    console.error("API Error:", err.response?._data || err)
  }
}

onMounted(async () => {
  try {
    const [resData, typeData, allDisruptions] = await Promise.all([
      fetchResources(),
      fetchDisruptionTypes(),
      fetchDisruptions()
    ])
    
    resourceOptions.value = resData
    typeOptions.value = typeData
    
    const found = allDisruptions.find(d => String(d.id) === String(disruptionId))
    if (found) {
      const formattedData = {
        ...found,
        start: found.start ? found.start.slice(0, 16) : '',
        end: found.end ? found.end.slice(0, 16) : ''
      }
      disruption.value = { ...formattedData }
      originalData.value = { ...formattedData }
    }
  } catch (err) {
    console.error("API Error beim Laden der Disruption:", err)
  }
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar title="Disruptions · Edit" :can-submit="canSubmit" :show-reset="true" :show-create="true"
      create-label="Update" @reset="resetToOriginal" @submit="updateDisruption" />

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
            <input v-model="disruption.end" type="datetime-local" class="input" />
            <button type="button" @click="setNow('end')"
              class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">
              Now
            </button>
          </div>
        </div>

        <select v-model="disruption.resource" class="input">
          <option disabled value="">-- choose --</option>
          <option v-for="opt in resourceOptions" :key="opt.id" :value="opt.id">
            {{ opt.name }}
          </option>
        </select>

        <select v-model="disruption.type" class="input">
          <option disabled value="">-- choose --</option>
          <option v-for="opt in typeOptions" :key="opt.id" :value="opt.id">
            {{ opt.name }}
          </option>
        </select>
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