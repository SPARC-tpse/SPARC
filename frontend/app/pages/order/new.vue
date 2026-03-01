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

const { theme } = useAppTheme();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const { draft: newOrder, resetDraft } = useOrderDraft()

const targetError = ref('')

const steps = ref([{ _id: Date.now(), workers: [], resource: '', name: '' }])
const workerList = ref([]);
const resourceList = ref([]);
  
const canSubmit = computed(() => {
  const o = newOrder.value
  const targetNum = Number(o.target)
  return Boolean(
    o.name && o.start && o.end && o.target
    && o.product && targetNum >= 0 && !targetError.value
  )
})

watchEffect(() => {
  if (registerTopbarActions) {
    registerTopbarActions({
      reset: resetForm,
      submit: submitOrder,
      canSubmit,
    })
  }
})

/**
 * Numeric input validation
 */
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

/**
 * Does not allow to copy and past into the target amount field
 */
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

/**
 * Adds a process to the processSteps list
 */
function addStep() {
  processSteps.value.push({ _id: Date.now() + Math.random(), name: '', workers: [], resource: null, approximated_time: { h: 0, m: 0, s: 0 } })
}
  
/**
 * Removes a process from the processSteps list
 * @param {int} index - the index of the element that should be removed
 */
function removeStep(index) {
  processSteps.value.splice(index, 1);
}

/**
 * Resets the order form and deletes all processes
 */
function resetForm() {
  resetDraft();
  steps.value = [{ _id: Date.now(), workers: [], resource: '', name: '' }]
}

/**
 * Loads the list of resources and workers from the backend api
 * @returns {Promise<void>}
 */
async function loadDependencies() {
  try {
    const [w, r] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/worker/get/`),
      $fetch(`${API_BASE_URL}/api/resource/get/`)
    ])
    workerList.value = w || [];
    resourceList.value = r || [];
  } catch (e) {
    console.error(e)
  }
}

/**
 * Calls the backend api to create order and processes
 * @returns {Promise<void>}
 */
async function submitOrder() {
  if (!canSubmit.value) return

  const processPayload = processSteps.value.map(s => ({
    name: s.name,
    resource: s.resource.id,
    workers: s.workers.map(w => w.id),
    approximated_time: s.approximated_time
  }));

  try {
    await $fetch(`${API_BASE_URL}/api/order/post`, {
      method: 'POST',
      body: {
        ...newOrder.value,
        target: Number(newOrder.value.target),
        process: processPayload
      }
    });
    resetDraft();
    navigateTo('/order/overview');
  } catch (error) { alert('Error creating order') }
}

onMounted(loadDependencies)
</script>

<template>
  <div :class="theme.pageWrapper">
    <main :class="theme.container" class="space-y-6">
      <!-- order form -->
      <section :class="theme.card">
        <h3 class="font-semibold text-lg mb-2">Order Information</h3>
        <div :class="theme.formGrid">
          <label :class="theme.label">Name <input v-model="newOrder.name" :class="theme.input" /></label>
          <label :class="theme.label">
            Target amount
            <input
              :value="newOrder.target_amount"
              type="number"
              min="0"
              :class="[theme.input, targetError ? 'border-red-500 ring-1 ring-red-500' : '']"
              @input="onTargetInput"
              @keydown="onTargetKeydown"
            />
            <span v-if="targetError" class="text-red-500 text-xs mt-1">{{ targetError }}</span>
          </label>
          <label :class="theme.label">Product name <input v-model="newOrder.product_name" :class="theme.input" /></label>
          <label :class="theme.label">Start date <input v-model="newOrder.start_date" type="date" :class="theme.input" /></label>
          <label :class="theme.label">End date <input v-model="newOrder.end_date" type="date" :class="theme.input" /></label>
          <label :class="theme.label">Status
            <select v-model="newOrder.status" :class="theme.input">
              <option
                v-for="(s, i) in ['Planned', 'Running', 'Paused', 'Done']"
                :key="s"
                :value="i"
              >
                {{ s }}
              </option>
            </select>
          </label>
          <label :class="theme.label">Priority
            <select v-model="newOrder.priority" :class="theme.input">
              <option
                v-for="(p, i) in ['High', 'Medium', 'Low']"
                :key="p"
                :value="i"
              >
                {{ p }}
              </option>
            </select>
          </label>
          <label :class="theme.label" class="sm:col-span-2">Comments <textarea v-model="newOrder.comments" rows="2" :class="theme.input" /></label>
        </div>
      </section>

      <!-- process editor -->
      <section :class="theme.card">
        <!-- title and add button -->
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-semibold text-lg">Process Steps</h3>
          <button :class="theme.linkAction" @click="addStep">+ Add step</button>
        </div>

        <!-- table -->
        <div class="space-y-3">
          <!-- column names -->
          <div
            v-if="processSteps.length > 0"
            :class="['px-1 opacity-70', theme.processStepGrid.replace('items-start', '')]"
          >
            <span></span>
            <span class="text-center font-bold">#</span>
            <span :class="theme.label">Process Name</span>
            <span :class="theme.label">Worker</span>
            <span :class="theme.label">Resource</span>
            <span :class="theme.label">Time (Approx.)</span>
          </div>

          <!-- rows -->
          <div
            v-for="(step, i) in processSteps"
            :key="step._id"
            :class="[theme.processStepGrid, theme.row]"
          >
            <button @click="removeStep(i)" class="mt-2 text-slate-400 hover:text-red-500 transition-colors">✕</button>
            <span class="mt-2 text-center text-xs opacity-50">{{ i + 1 }}</span>
            <input v-model="step.name" :class="theme.input" class="mt-0 h-[38px]" placeholder="Choose a name..." />
            <MultiSelect v-model="step.workers" :model-list="workerList" />
            <MultiSelect
                :model-value="step.resource ? [step.resource] : []"
                :model-list="resourceList"
                single
                @update:model-value="step.resource = $event[0] ?? null"
            />
            <div class="flex items-center gap-1">
              <input v-model.number="step.approximated_time.h" type="number" min="0" :class="theme.input" class="w-16 text-center no-arrows" placeholder="hh" />
              <span class="opacity-50">:</span>
              <input v-model.number="step.approximated_time.m" type="number" min="0" max="59" :class="theme.input" class="w-16 text-center no-arrows" placeholder="mm" />
              <span class="opacity-50">:</span>
              <input v-model.number="step.approximated_time.s" type="number" min="0" max="59" :class="theme.input" class="w-16 text-center no-arrows" placeholder="ss" />
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* hide the arrow buttons for number fields with class no-arrows */
input.no-arrows::-webkit-outer-spin-button,
input.no-arrows::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input.no-arrows {
  -moz-appearance: textfield;
}
</style>
