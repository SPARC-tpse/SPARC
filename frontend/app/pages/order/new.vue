<script setup lang="js">
import { ref, computed, onMounted, inject, watchEffect } from 'vue'
import { useOrderDraft} from "~/composables/useOrderDraft.ts";

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Orders · New',
    showReset: true,
    showCreate: true,
    createLabel: 'Create',
  },
})

const registerTopbarActions = inject('registerTopbarActions')

const { theme } = useAppTheme()
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const { draft: newOrder, resetDraft } = useOrderDraft()

const targetError = ref('')

function onTargetInput(e) {
  const raw = e.target.value
  // Prüfe ob nicht-numerische Zeichen enthalten sind (außer leer)
  if (raw !== '' && !/^\d+$/.test(raw)) {
    targetError.value = 'Only digits (0–9) are allowed.'
    // Alle Nicht-Ziffern entfernen
    const cleaned = raw.replace(/\D/g, '')
    newOrder.value.target = cleaned
    e.target.value = cleaned
    return
  }
  targetError.value = ''
  // Negativwerte abfangen (z. B. durch Pfeiltasten)
  const num = Number(raw)
  if (num < 0) {
    newOrder.value.target = '0'
    e.target.value = '0'
    return
  }
  newOrder.value.target = raw
}

function onTargetKeydown(e) {
  // Erlaube: Backspace, Delete, Tab, Escape, Enter, Pfeiltasten, Home, End
  const allowed = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
    'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End']
  if (allowed.includes(e.key)) return
  // Verbiete Ctrl/Cmd+C/V/X/A
  if ((e.ctrlKey || e.metaKey) && ['a', 'c', 'v', 'x'].includes(e.key.toLowerCase())) {
    e.preventDefault()
    targetError.value = 'Shortcuts Ctrl/Cmd + A/C/V/X are disabled for this field.'
    return
  }
  // Nur Ziffern erlauben
  if (!/^\d$/.test(e.key)) {
    e.preventDefault()
    targetError.value = 'Only digits (0–9) are allowed.'
  }
}

const steps = ref([{ _id: Date.now(), workers: [], resource: '', name: '' }])
const allWorkers = ref([]), allResources = ref([])

const canSubmit = computed(() => {
  const o = newOrder.value
  const targetNum = Number(o.target)
  return Boolean(
    o.name && o.start && o.end && o.target
    && o.product && targetNum >= 0 && !targetError.value
  )
})

function addStep() { steps.value.push({ _id: Date.now() + Math.random(), workers: [], resource: '', name: '' }) }
function removeStep(index) { steps.value.splice(index, 1) }

function resetForm() {
  resetDraft()
  steps.value = [{ _id: Date.now(), workers: [], resource: '', name: '' }]
}

// Worker/Resource Listen beim Öffnen der Seite laden
onMounted(async () => {
  try {
    const [w, r] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/worker/list`),
      $fetch(`${API_BASE_URL}/api/resource/list`),
    ])
    allWorkers.value = w
    allResources.value = r
  } catch (e) {
    console.error(e)
  }
})

async function submitOrder() {
  if (!canSubmit.value) return
  const processPayload = steps.value.map(s => ({ name: s.name, resource: s.resource, workers: s.workers.map(w => w.name) }))
  try {
    await $fetch(`${API_BASE_URL}/api/order/post`, { method: 'POST', body: { ...newOrder.value, target: Number(newOrder.value.target), process: processPayload } })
    resetDraft()
    navigateTo('/order/overview')
  } catch (error) { alert('Error creating order') }
}

watchEffect(() => {
  if (registerTopbarActions) {
    registerTopbarActions({
      reset: resetForm,
      submit: submitOrder,
      canSubmit,
    })
  }
})

</script>

<template>
  <div :class="theme.pageWrapper">
    <main :class="theme.container" class="space-y-6">
      <section :class="theme.card">
        <h3 class="font-semibold text-lg mb-2">Order Information</h3>
        <div :class="theme.formGrid">
          <label :class="theme.label">Name <input v-model="newOrder.name" :class="theme.input" /></label>
          <label :class="theme.label">
            Target amount
            <input
              :value="newOrder.target"
              type="number"
              min="0"
              :class="[theme.input, targetError ? 'border-red-500 ring-1 ring-red-500' : '']"
              @input="onTargetInput"
              @keydown="onTargetKeydown"
            />
            <span v-if="targetError" class="text-red-500 text-xs mt-1">{{ targetError }}</span>
          </label>
          <label :class="theme.label">Product name <input v-model="newOrder.product" :class="theme.input" /></label>
          <label :class="theme.label">Start date <input v-model="newOrder.start" type="date" :class="theme.input" /></label>
          <label :class="theme.label">End date <input v-model="newOrder.end" type="date" :class="theme.input" /></label>
          <label :class="theme.label">Status
            <select v-model="newOrder.status" :class="theme.input">
              <option v-for="s in ['Planned', 'Running', 'Paused', 'Done']" :key="s">{{ s }}</option>
            </select>
          </label>
          <label :class="theme.label">Priority
            <select v-model="newOrder.priority" :class="theme.input">
              <option v-for="p in ['High', 'Medium', 'Low']" :key="p">{{ p }}</option>
            </select>
          </label>
          <label :class="theme.label" class="sm:col-span-2">Comments <textarea v-model="newOrder.comments" rows="2" :class="theme.input" /></label>
        </div>
      </section>

      <section :class="theme.card">
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-semibold text-lg">Process steps</h3>
          <button :class="theme.linkAction" @click="addStep">+ Add step</button>
        </div>

        <div class="space-y-3">
          <div v-if="steps.length > 0" :class="['px-1 opacity-70', theme.processStepGrid.replace('items-start', '')]">
            <span></span><span class="text-center font-bold">#</span><span :class="theme.label">Worker</span><span :class="theme.label">Resource</span><span :class="theme.label">Step Name</span>
          </div>

          <div v-for="(step, i) in steps" :key="step._id" :class="[theme.processStepGrid, theme.row]">
            <button @click="removeStep(i)" class="mt-2 text-slate-400 hover:text-red-500 transition-colors">✕</button>
            <span class="mt-2 text-center text-xs opacity-50">{{ i + 1 }}</span>
            <WorkerMultiSelect v-model="step.workers" :all-workers="allWorkers" />
            <select v-model="step.resource" :class="theme.input" class="mt-0 h-[38px]">
              <option value="" disabled>-- Resource --</option>
              <option v-for="res in allResources" :key="res.id" :value="res.name">{{ res.name }}</option>
            </select>
            <input v-model="step.name" :class="theme.input" class="mt-0 h-[38px]" placeholder="Choose a name..." />
          </div>
        </div>
      </section>
    </main>
  </div>
</template>