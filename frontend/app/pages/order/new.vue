<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import WorkerMultiSelect from '~/components/WorkerMultiSelect.vue'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const newOrder = ref({
  name: '',
  start: '',
  end: '',
  target: '',
  product: '',
  status: 'Planned',
  priority: 'Medium',
  comments: ''
})

const steps = ref([{ _id: Date.now(), workers: [], resource: '', name: '' }])
const allWorkers = ref([])

const canSubmit = computed(() => {
  const o = newOrder.value
  return Boolean(o.name && o.start && o.end && o.target && o.product)
})

function addStep() {
  steps.value.push({ _id: Date.now() + Math.random(), workers: [], resource: '', name: '' })
}

function removeStep(index) {
  steps.value.splice(index, 1)
}

function resetForm() {
  newOrder.value = {
    name: '', start: '', end: '', target: '', product: '',
    status: 'Planned', priority: 'Medium', comments: ''
  }
  steps.value = [{ _id: Date.now(), workers: [], resource: '', name: '' }]
}

async function loadAllWorkers() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/worker/list`, { method: 'GET' })
        allWorkers.value = response || []
    } catch (e) {
        console.error(e)
    }
}

async function submitOrder() {
  if (!canSubmit.value) return

  const activeSteps = steps.value.filter(step =>
    (step.workers && step.workers.length > 0) || step.resource || step.name
  )

  const processPayload = activeSteps.map(step => ({
      name: step.name,
      resource: step.resource,
      workers: step.workers.map(w => w.name)
  }))

  const order = {
    ...newOrder.value,
    target: Number(newOrder.value.target),
    process: processPayload
  }

  try {
    await $fetch(`${API_BASE_URL}/api/order/post`, {
      method: 'POST',
      body: order
    })
    resetForm()
    //alert('Order created successfully')
  } catch (error) {
    console.error('API Error:', error);
    alert('Error creating order')
  }
}

onMounted(() => {
    loadAllWorkers()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Orders · New"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Create"
      @reset="resetForm"
      @submit="submitOrder"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name <input v-model="newOrder.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Target amount <input v-model="newOrder.target" type="number" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Product name <input v-model="newOrder.product" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Start date <input v-model="newOrder.start" type="date" inputmode="numeric" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          End date <input v-model="newOrder.end" type="date" inputmode="numeric" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="newOrder.status" class="input">
            <option value="Planned">Planned</option>
            <option value="Running">Running</option>
            <option value="Paused">Paused</option>
            <option value="Done">Done</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Priority
          <select v-model="newOrder.priority" class="input">
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
          Comments <textarea v-model="newOrder.comments" rows="3" class="input" />
        </label>
      </div>

      <div
        class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
        :class="isDarkMode ? 'border-gray-900 bg-slate-900 shadow-black' : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex items-center justify-between">
          <h3 class="font-semibold">Process steps</h3>
          <button
            class="text-sm hover:underline"
            :class="isDarkMode ? 'text-pink-200 hover:text-pink-100' : 'text-pink-600 hover:text-pink-800'"
            @click="addStep"
          >+ Add step</button>
        </div>

        <div class="space-y-2">
          <div
            v-if="steps.length > 0"
            class="grid grid-cols-[30px_30px_1fr_1fr_1fr] gap-2 text-xs px-1"
            :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'"
          >
            <span></span> <span>#</span>
            <span>Worker</span>
            <span>Resource</span>
            <span>Process-step Name</span>
          </div>

          <div
            v-for="(step, i) in steps"
            :key="step._id"
            class="grid grid-cols-[30px_30px_1fr_1fr_1fr] gap-2 items-start rounded-lg border p-2 transition-colors"
            :class="isDarkMode ? 'border-gray-700 bg-gray-700' : 'border-slate-200 bg-slate-50'"
          >
            <button
              @click="removeStep(i)"
              class="flex items-center justify-center w-6 h-6 mt-1.5 rounded text-slate-400 hover:text-red-500 hover:bg-red-500/10 transition-colors"
              title="Remove step"
            >
              ✕
            </button>

            <span class="text-xs text-center mt-2" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ i + 1 }}</span>

            <div class="w-full">
                <WorkerMultiSelect v-model="step.workers" :all-workers="allWorkers" />
            </div>

            <input v-model="step.resource" class="input h-10" placeholder="Resource" />
            <input v-model="step.name" class="input h-10" placeholder="Step Name" />
          </div>

          <div v-if="steps.length === 0" class="text-center py-4 text-sm opacity-50">
             No steps defined. Add a step to begin.
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.input { @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors; }
.dark-mode .input { @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500; }
.light-mode .input { @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500; }
.dark-mode .disabled-input { @apply bg-gray-900 text-slate-500; }
.light-mode .disabled-input { @apply bg-slate-100 text-slate-500; }
.dark-mode .label-text { @apply text-slate-300; }
.light-mode .label-text { @apply text-slate-600; }
</style>