<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useDisruptionTimer } from '~/composables/useDisruptionTimer';
import { useDisruptionDraft } from "~/composables/useDisruptionDraft.ts";

definePageMeta({ layout: 'custom' })

const { theme } = useAppTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const { isRunning, isPaused, formatted, start: timerStart, pause: timerPause, resume: timerResume, stopAndMaybeApply, reset: timerReset } = useDisruptionTimer()
const { draft: newDisruption, resetDraft } = useDisruptionDraft()

const resources = ref([])
const types = ref([])
const formId = ref(`DIS-${Math.floor(Math.random() * 10000)}`)

const primaryLabel = computed(() => {
  if (!isRunning.value && !isPaused.value) return 'Start'
  if (isPaused.value) return 'Resume'
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
  } catch (e) { console.error(e) }
}

const canSubmit = computed(() => newDisruption.value.name && newDisruption.value.resource)

function setNow(field) {
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
      resetDraft(); timerReset()
      await navigateTo('/disruption/overview')
    } catch (error) { console.error(error) }
}

onMounted(loadFormData)
</script>

<template>
  <div :class="theme.pageWrapper">
    <Topbar
      title="Disruptions · New"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Create"
      @reset="resetForm"
      @submit="submitDisruption"
    />

    <main :class="theme.container">
      <div class="space-y-6">

        <section :class="theme.card">
          <div class="flex flex-wrap items-center gap-6 justify-between">
            <div class="flex items-center gap-3">
               <div class="w-3 h-3 rounded-full bg-red-500 animate-pulse" v-if="isRunning"></div>
               <div :class="theme.label" class="mt-0">Live Timer</div>
            </div>
            <div class="font-mono text-3xl font-bold tracking-tighter">{{ formatted }}</div>
            <div class="flex gap-2">
              <button type="button" :class="theme.btnDeleteMode" class="px-6 py-2" @click="onPrimaryClick">
                {{ primaryLabel }}
              </button>
              <button type="button" :class="theme.btnDeleteMode" class="px-6 py-2 border-red-500/50 text-red-500" @click="stopAndMaybeApply(newDisruption)" :disabled="!isRunning && !isPaused">
                Stop & Apply
              </button>
            </div>
          </div>
        </section>

        <section :class="theme.card">
          <h3 class="font-semibold text-lg mb-2">Disruption Details</h3>

          <div :class="theme.formGrid">
            <label :class="theme.label">
              Name <input v-model="newDisruption.name" :class="theme.input" placeholder="Describe the issue..." />
            </label>

            <label :class="theme.label">
              Draft ID <input :value="formId" :class="[theme.input, 'opacity-50']" disabled />
            </label>

            <div class="flex flex-col">
              <label :class="theme.label">Start</label>
              <div class="flex gap-2 items-end">
                <input v-model="newDisruption.start" type="datetime-local" step="1" :class="theme.input" />
                <button type="button" @click="setNow('start')" :class="theme.btnDeleteMode" class="h-[42px] px-4">Now</button>
              </div>
            </div>

            <div class="flex flex-col">
              <label :class="theme.label">End</label>
              <div class="flex gap-2 items-end">
                <input v-model="newDisruption.end" type="datetime-local" step="1" :class="theme.input" />
                <button type="button" @click="setNow('end')" :class="theme.btnDeleteMode" class="h-[42px] px-4">Now</button>
              </div>
            </div>

            <label :class="theme.label">
              Resource
              <select v-model="newDisruption.resource" :class="theme.input">
                <option disabled value="">-- choose --</option>
                <option v-for="r in resources" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
            </label>

            <label :class="theme.label">
              Type
              <select v-model="newDisruption.type" :class="theme.input">
                <option disabled value="">-- choose --</option>
                <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </label>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>