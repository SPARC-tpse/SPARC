<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useDisruptionTimer } from '~/composables/useDisruptionTimer';
import {useDisruptionDraft} from "~/composables/useDisruptionDraft.ts";

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()

const {
  isRunning,
  isPaused,
  formatted,
  start: timerStart,
  pause: timerPause,
  resume: timerResume,
  stopAndMaybeApply,
  reset: timerReset,
  popoutVisible,
} = useDisruptionTimer()

const { draft: newDisruption, resetDraft } = useDisruptionDraft()

// Label für den Start/Pause/Weiter-Button
const primaryLabel = computed(() => {
  if (!isRunning.value && !isPaused.value) return 'Start'
  if (isPaused.value) return 'Weiter'
  return 'Pause'
})

// Click-Handler für Start/Pause/Weiter
function onPrimaryClick() {
  if (!isRunning.value && !isPaused.value) {
    timerStart()
    return
  }
  if (isPaused.value) {
    timerResume()
    return
  }
  timerPause()
}

const resources = ref([
  { id: 1, name: 'Machine A' },
  { id: 2, name: 'Conveyor' }
])

const types = ref([
  { id: 1, name: 'Error' },
  { id: 2, name: 'Maintenance' }
])

const formId = ref(`DIS-${Math.floor(Math.random() * 10000)}`)

/**
const newDisruption = useState('disruption:newForm', () => ({
  name: '',
  start: '',
  end: '',
  resource: '',
  type: ''
}))
 */

const canSubmit = computed(() =>
  newDisruption.value.name && newDisruption.value.resource
)

/**
 * Abfrage, ob ein Feld überschrieben werden darf
 * Nutzt natives Browser-Confirm als einfaches Popup
 */
function confirmOverwrite(message) {
  return window.confirm(message)
}

function setNow(field) {
  const current = (newDisruption.value?.[field] ?? '').toString().trim()

  if (current) {
    const ok = confirmOverwrite(
      `Das Feld \`${field}\` ist bereits gesetzt.\nMöchtest du den vorhandenen Wert überschreiben\?`
    )
    if (!ok) return
  }

  const now = new Date()
  newDisruption.value[field] = now.toISOString().slice(0, 16) // yyyy-MM-ddTHH:mm
}

/**
 * Timer-Stop mit Overwrite-Confirm, falls Start/Ende bereits befüllt sind

function stopTimerAndMaybeApply() {
  timerStop()

  // Falls Timer noch keine Zeiten hat, nichts tun
  if (!startMs.value || !endMs.value) return

  const hasExistingStart = !!newDisruption.value.start?.toString().trim()
  const hasExistingEnd = !!newDisruption.value.end?.toString().trim()

  if (hasExistingStart || hasExistingEnd) {
    const ok = confirmOverwrite(
      `Start und/oder Endzeit sind bereits eingetragen.\nMöchtest du diese durch die Timer-Zeiten überschreiben\?`
    )
    if (!ok) return
  }

  newDisruption.value.start = toDateTimeLocal(startMs.value)
  newDisruption.value.end = toDateTimeLocal(endMs.value)
}
*/

function resetForm() {
  newDisruption.value = {
    name: '',
    start: '',
    end: '',
    resource: '',
    type: ''
  }
  timerReset()
}

async function submitDisruption() {
    if (!canSubmit.value) return

    const disruption = {
    id: formId.value,
    ...newDisruption.value
    }

    const baseURL = config.public.apiBase || 'http://localhost:8000/api'
    const endpoint = '/disruptions/new_disruption'

    console.log('Submitting disruption:', disruption)

    try {
    const response = await $fetch(`${baseURL}${endpoint}`, {
      method: 'POST',
      body: newDisruption.value,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    })

    // Nach erfolgreichem Submit Draft löschen, damit er nicht wieder auftaucht
    resetDraft()
    timerReset()

    await navigateTo('/disruption/overview')
    return response
    } catch (error) {
    console.error('API Error:', error)
    throw error
    }
}
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

      <div
        class="rounded-lg border p-4"
        :class="isDarkMode ? 'border-gray-700' : 'border-slate-300'"
      >
        <div class="flex flex-wrap items-center gap-3 justify-between">
          <div class="text-sm font-semibold">Timer</div>

          <div class="font-mono text-lg">
            {{ formatted }}
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="px-3 py-2 rounded-lg text-sm border transition-colors"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'"
              @click="onPrimaryClick"
            >
              {{ primaryLabel }}
            </button>

            <button
              type="button"
              class="px-3 py-2 rounded-lg text-sm border transition-colors"
              :class="isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-slate-300 hover:bg-slate-100'"
              @click="stopAndMaybeApply(newDisruption)"
              :disabled="!isRunning && !isPaused"
            >
              Stopp
            </button>
          </div>
        </div>
      </div>



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
            <input v-model="newDisruption.start" type="datetime-local" step="1" class="input" />
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
            <input v-model="newDisruption.end" type="datetime-local" step="1" class="input" />
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