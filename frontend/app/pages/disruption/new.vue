<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useDisruptionTimer } from '~/composables/useDisruptionTimer';
import { useDisruptionDraft } from "~/composables/useDisruptionDraft.ts";

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const { isRunning, isPaused, formatted, start: timerStart, pause: timerPause, resume: timerResume, stopAndMaybeApply, reset: timerReset } = useDisruptionTimer()
const { draft: newDisruption, resetDraft } = useDisruptionDraft()

const resources = ref([])
const types = ref([])
const formId = ref(`DIS-${Math.floor(Math.random() * 10000)}`)

const primaryLabel = computed(() => {
  if (!isRunning.value && !isPaused.value) return 'Start'
  if (isPaused.value) return 'Weiter'
  return 'Pause'
})

function onPrimaryClick() {
  if (!isRunning.value && !isPaused.value) { timerStart(); return }
  if (isPaused.value) { timerResume(); return }
  timerPause()
}

async function loadFormData() {
  try {
    const [resData, typeData] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/resource/list`),
      $fetch(`${API_BASE_URL}/api/disruption-type/list`)
    ])
    resources.value = resData
    types.value = typeData
  } catch (e) {
    console.error('Error loading form data:', e)
  }
}

const canSubmit = computed(() => newDisruption.value.name && newDisruption.value.resource)

function confirmOverwrite(message) { return window.confirm(message) }

function setNow(field) {
  const current = (newDisruption.value?.[field] ?? '').toString().trim()
  if (current && !confirmOverwrite(`Das Feld \`${field}\` ist bereits gesetzt. Überschreiben?`)) return
  newDisruption.value[field] = new Date().toISOString().slice(0, 16)
}

function resetForm() {
  newDisruption.value = { name: '', start: '', end: '', resource: '', type: '' }
  timerReset()
}

async function submitDisruption() {
    if (!canSubmit.value) return
    try {
      await $fetch(`${API_BASE_URL}/api/disruption/post`, {
        method: 'POST',
        body: newDisruption.value
      })
      resetDraft()
      timerReset()
      await navigateTo('/disruption/overview')
    } catch (error) {
      console.error('API Error:', error)
    }
}

onMounted(() => {
  loadFormData()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Disruptions · New"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Create"
      @reset="resetForm"
      @submit="submitDisruption"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="rounded-lg border p-4" :class="isDarkMode ? 'border-gray-700' : 'border-slate-300'">
        <div class="flex flex-wrap items-center gap-3 justify-between">
          <div class="text-sm font-semibold">Timer</div>
          <div class="font-mono text-lg">{{ formatted }}</div>
          <div class="flex flex-wrap gap-2">
            <button type="button" class="px-3 py-2 rounded-lg text-sm border transition-colors" :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'" @click="onPrimaryClick">{{ primaryLabel }}</button>
            <button type="button" class="px-3 py-2 rounded-lg text-sm border transition-colors" :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'" @click="stopAndMaybeApply(newDisruption)" :disabled="!isRunning && !isPaused">Stopp</button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name <input v-model="newDisruption.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID (auto) <input :value="formId" class="input disabled-input" disabled />
        </label>
        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">Start</label>
          <div class="flex gap-2">
            <input v-model="newDisruption.start" type="datetime-local" step="1" class="input" />
            <button type="button" @click="setNow('start')" class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap" :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">Now</button>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm label-text">End</label>
          <div class="flex gap-2">
            <input v-model="newDisruption.end" type="datetime-local" step="1" class="input" />
            <button type="button" @click="setNow('end')" class="px-3 rounded-lg text-sm border transition-colors whitespace-nowrap" :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'">Now</button>
          </div>
        </div>
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource
          <select v-model="newDisruption.resource" class="input">
            <option disabled value="">-- choose --</option>
            <option v-for="r in resources" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="newDisruption.type" class="input">
            <option disabled value="">-- choose --</option>
            <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </label>
      </div>
    </main>
  </div>
</template>