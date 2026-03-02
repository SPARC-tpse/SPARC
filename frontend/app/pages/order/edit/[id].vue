<script setup lang="js">
import { ref, computed, watch, onMounted, inject, watchEffect } from 'vue'
import MultiSelect from '~/components/MultiSelect.vue'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Orders · Edit',
    showReset: true,
    showCreate: true,
    createLabel: 'Update',
  },
})

const registerTopbarActions = inject('registerTopbarActions')

const { theme } = useAppTheme();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const route = useRoute();
const orderId = Number(route.params.id);

const order = ref({
  id: orderId,
  name: null,
  target_amount: null,
  start_date: null,
  end_date: null,
  product_name: null,
  priority: 1,
  status: 0,
  comments: '',
});
const selectedProcessStep = ref(null);
const processSteps = ref([]);
const workerList = ref([]);
const resourceList = ref([]);
const canSubmit = computed(() => {
  const o = order.value
  return Boolean(o.name && o.start_date && o.end_date && o.target_amount && o.product_name)
})

const hasWarning = (field) => !order.value[field]
const hasProcessWarning = (step) => {
  const hasWorkers = step.workers && step.workers.length > 0
  const hasResource = step.resource && (step.resource.status === 2 || step.resource.status === 3)
  return !hasWorkers || !hasResource
}

/**
 * Adds a process to the processSteps list
 */
function addStep() {
  processSteps.value.push({ _id: Date.now() + Math.random(), name: '', workers: [], resource: null, approximated_time: { h: 0, m: 0, s: 0 } })
}

/**
 * Removes a process from the processSteps list, if the process was selected it gets unselected
 * @param {int} index - the index of the element that should be removed
 */
async function removeStep(index) {
  if (selectedProcessStep.value === processSteps.value[index]) {
    selectedProcessStep.value = null;
  }
  // TODO: That the remove button is a direct change might be unintuitive behavior because for most changes you need to press the "update" button. Considering the consequence of such a mistake this should change.
  try {
    await $fetch(`${API_BASE_URL}/api/process/delete/${processSteps.value[index].id}/`, {
      method: 'DELETE',
    });
  } catch (error) {
    alert(error.data?.error || error.message)
  }
  processSteps.value.splice(index, 1);
}

/**
 * Loads the selected order from the backend api
 * @returns {Promise<void>}
 */
async function loadOrder() {
  try {
    // get order
    const response_order = await $fetch(`${API_BASE_URL}/api/order/get/${orderId}/`)
    order.value = response_order;
    order.value.start_date = order.value.start_date.slice(0, 16);

    // get processes for order
    const response_processes = await $fetch(`${API_BASE_URL}/api/order/get_processes/${orderId}/`)
    processSteps.value = response_processes.map(p => ({
      ...p,
      approximated_time: {
        h: Math.floor(p.approximated_time / 3600),
        m: Math.floor((p.approximated_time % 3600) / 60),
        s: p.approximated_time % 60,
      }
    }));
  } catch (error) {
    alert(error.data?.error || error.message)
  }
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
 * Updates the selected order with the changes made to the order form and process editor
 * @returns {Promise<void>}
 */
async function updateOrder() {
  if (!canSubmit.value) return

  const processPayload = processSteps.value.map(s => ({
    id: s.id ?? null,
    name: s.name,
    resource: s.resource.id,
    workers: s.workers.map(w => w.id),
    approximated_time: s.approximated_time
  }));

  try {
    await $fetch(`${API_BASE_URL}/api/order/put/${orderId}/`, {
      method: 'PUT',
      body: {
        ...order.value,
        target_amount: Number(order.value.target_amount),
        process: processPayload
      }
    })
  } catch (error) {
    alert(error.data?.error || error.message)
  }
}

function resetForm() {
  navigateTo('/order/overview')
}

watchEffect(() => {
  registerTopbarActions?.({ reset: resetForm, submit: updateOrder, canSubmit })
})

onMounted(() => {
  loadOrder()
  loadDependencies()
})
</script>

<template>
  <main :class="theme.container" class="space-y-6">
    <!-- order form -->
    <section :class="theme.card">
      <div :class="theme.formGrid">
        <label :class="theme.label">
            <div class="flex items-center gap-2"><span>Order Name</span><span v-if="hasWarning('name')" class="text-amber-500">⚠️</span></div>
            <input v-model="order.name" :class="[theme.input, hasWarning('name') ? 'border-amber-500' : '']" />
        </label>
        <label :class="theme.label">ID <input :value="order.id" :class="theme.inputDisabled" disabled /></label>
        <label :class="theme.label">Target Amount <input v-model="order.target_amount" type="number" :class="theme.input" /></label>
        <label :class="theme.label">Product Name <input v-model="order.product_name" :class="theme.input" /></label>
        <label :class="theme.label">Start date <input v-model="order.start_date" type="datetime-local" :class="theme.input" /></label>
        <label :class="theme.label">End Date <input v-model="order.end_date" type="date" :class="theme.input" /></label>
        <label :class="theme.label">Status
          <select v-model="order.status" :class="theme.input">
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
          <select v-model="order.priority" :class="theme.input">
            <option
              v-for="(p, i) in ['High', 'Medium', 'Low']"
              :key="p"
              :value="i"
            >
              {{ p }}
            </option>
          </select>
        </label>
        <label :class="theme.label" class="sm:col-span-2">Comments <textarea v-model="order.comments" rows="2" :class="theme.input" /></label>
      </div>
    </section>

    <!-- file upload -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div :class="theme.card"><FileUpload file-type="bom" label="Bill of Materials" :order-id="orderId" /></div>
      <div :class="theme.card"><FileUpload file-type="general" label="Additional Files" :order-id="orderId" /></div>
    </div>

    <!-- process selection -->
    <section v-if="processSteps.length > 0" :class="theme.card">
      <h3 class="font-semibold text-lg">Live Step Management</h3>
      <label :class="theme.label">Select Step to edit times
        <select v-model="selectedProcessStep" :class="theme.input">
          <option :value="null">-- Choose a step --</option>
          <option v-for="(step, index) in processSteps" :key="step._id" :value="step">
            {{ hasProcessWarning(step) ? '⚠️ ' : '' }} Step {{ index + 1 }}: {{ step.name || 'Unnamed' }}
          </option>
        </select>
      </label>

      <div v-if="selectedProcessStep" class="pt-4 border-t border-slate-700/30 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ProcessTimer label="Setup" :initial-seconds="selectedProcessStep.setup_time_seconds" :process-id="selectedProcessStep.id" timer-type="setup_time" />
          <ProcessTimer label="Waiting" :initial-seconds="selectedProcessStep.waiting_time_seconds" :process-id="selectedProcessStep.id" timer-type="waiting_time" />
          <ProcessTimer label="Process" :initial-seconds="selectedProcessStep.process_time_seconds" :process-id="selectedProcessStep.id" timer-type="process_time" />
        </div>
        <button @click="navigateTo(`/disruption/new?process=${selectedProcessStep.id}`)" :class="theme.btnWarning">⚠️ Create Disruption</button>
      </div>
    </section>

    <!-- process editor -->
    <section :class="theme.card">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-semibold text-lg">Process Steps Editor</h3>
        <button :class="theme.linkAction" @click="addStep">+ Add step</button>
      </div>

      <div class="space-y-3">
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

        <div v-if="processSteps.length === 0" class="py-10 text-center opacity-50 italic">No steps defined. Add one to begin.</div>

        <div
          v-for="(step, i) in processSteps"
          :key="step._id"
          :class="[theme.processStepGrid, theme.row, hasProcessWarning(step) ? 'border-amber-500/50' : '']"
        >
          <button @click="removeStep(i)" class="mt-2 text-slate-400 hover:text-red-500 transition-colors">✕</button>
          <span class="mt-2 text-center text-xs opacity-50">{{  i + 1 }}</span>
          <input v-model="step.name" :class="theme.input" class="mt-0 h-[38px]" placeholder="Step Name" />
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
