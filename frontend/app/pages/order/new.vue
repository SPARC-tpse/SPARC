<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import MultiSelect from '~/components/MultiSelect.vue'

definePageMeta({ layout: 'custom' })

const { theme } = useAppTheme();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const newOrder = ref({
  name: null,
  target_amount: null,
  start_date: null,
  end_date: null,
  product_name: null,
  priority: 1,
  status: 0,
  comments: ''
});
const processSteps = ref([]);
const workerList = ref([]);
const resourceList = ref([]);
const canSubmit = computed(() => {
  const o = newOrder.value
  return Boolean(o.name && o.start_date && o.end_date && o.target_amount && o.product_name)
});

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
  newOrder.value = { name: '', start_date: '', end_date: '', target_amount: '', product_name: '', status: 1, priority: 1, comments: '' }
  processSteps.value = []
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
    await $fetch(`${API_BASE_URL}/api/order/post/`, {
      method: 'POST',
      body: {
        ...newOrder.value,
        target_amount: Number(newOrder.value.target_amount),
        process: processPayload
      }
    });
    navigateTo('/order/overview');
  } catch (error) {
    alert(error.data?.error || error.message)
  }
}

onMounted(loadDependencies)
</script>

<template>
  <div :class="theme.pageWrapper">
    <Topbar title="Orders · New" :can-submit="canSubmit" :show-reset="true" create-label="Create" @reset="resetForm" @submit="submitOrder" />

    <main :class="theme.container" class="space-y-6">
      <!-- order form -->
      <section :class="theme.card">
        <h3 class="font-semibold text-lg mb-2">Order Information</h3>
        <div :class="theme.formGrid">
          <label :class="theme.label">Name <input v-model="newOrder.name" :class="theme.input" /></label>
          <label :class="theme.label">Target amount <input v-model="newOrder.target_amount" type="number" :class="theme.input" /></label>
          <label :class="theme.label">Product name <input v-model="newOrder.product_name" :class="theme.input" /></label>
          <label :class="theme.label">Start date <input v-model="newOrder.start_date" type="datetime-local" :class="theme.input" /></label>
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