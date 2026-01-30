<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const route = useRoute()
const orderId = route.params.id

const order = ref({
  id: orderId,
  name: '',
  start: '',
  end: '',
  target: '',
  product: '',
  status: 'Planned',
  priority: 'Medium',
  comments: ''
})

const steps = ref([{ name: '', resource: '', setupTime: '', status: 'Planned' }])

const canSubmit = computed(() => {
  const o = order.value
  return Boolean(o.name && o.start && o.end && o.target && o.product)
})

function normalizePriority(value) {
  if (typeof value === 'number') {
    if (value === 3) return 'High'
    if (value === 2) return 'Medium'
    if (value === 1) return 'Low'
  }
  if (typeof value === 'string') return value
  return 'Unknown'
}

function mapOrder(apiOrder) {
  return {
    id: apiOrder.id,
    name: apiOrder.name,
    start: apiOrder.start_date ?? apiOrder.start,
    end: apiOrder.end_date ?? apiOrder.end,
    target: apiOrder.target_amount ?? apiOrder.target ?? '',
    product: apiOrder.product_name ?? apiOrder.product,
    status: apiOrder.status,
    priority: normalizePriority(apiOrder.priority),
    comments: apiOrder.comments ?? '',
    process: apiOrder.process ?? [],
    process_steps: apiOrder.process_steps ?? []
  }
}

function addStep() {
  steps.value.push({ name: '', resource: '', setupTime: '', status: 'Planned' })
}

function removeStep(index) {
  steps.value.splice(index, 1)
}

async function loadOrder() {
  try {
    const response = await $fetch(`${API_BASE_URL}/orders/get_orders`)
    const list = Array.isArray(response) ? response.map(mapOrder) : []
    const found = list.find((item) => String(item.id) === String(orderId))
    if (found) {
      order.value = { ...order.value, ...found }
      const existingSteps = (found.process_steps && found.process_steps.length)
        ? found.process_steps
        : (found.process || [])
      steps.value = existingSteps.length
        ? existingSteps.map((step, idx) => ({
            name: step.name ?? '',
            resource: step.resource ?? '',
            setupTime: step.setup_time ?? '',
            status: step.status ?? 'Planned',
            nr: step.number ?? step.nr ?? idx + 1
          }))
        : [{ name: '', resource: '', setupTime: '', status: 'Planned' }]
      return
    }
  } catch (error) {
    console.error('API Error:', error)
  }

  order.value = {
    id: orderId,
    name: 'Test Order',
    start: '2025-11-27',
    end: '2025-11-28',
    target: 1200,
    product: 'Ventil platinen',
    status: 'Running',
    priority: 'High',
    comments: 'set-up phase done.'
  }
  steps.value = [
    { name: 'Assembly', resource: 'Machine A', setupTime: '00:30', status: 'Running' },
    { name: 'Quality Check', resource: 'Station 2', setupTime: '00:10', status: 'Planned' }
  ]
}

function editProcessStep(stepIndex) {
  const stepId = `${orderId}-${stepIndex + 1}`
  navigateTo(`/order/process-steps/${stepId}`)
}

async function updateOrder() {
  if (!canSubmit.value) return

  const processSteps = steps.value
    .map((step, index) => ({
      nr: index + 1,
      name: step.name,
      resource: step.resource,
      setup_time: step.setupTime,
      status: step.status
    }))
    .filter((step) => step.name || step.resource || step.setup_time || step.status)
  const updatedOrder = {
    id: order.value.id,
    name: order.value.name,
    start: order.value.start,
    end: order.value.end,
    target: Number(order.value.target),
    product: order.value.product,
    status: order.value.status,
    priority: order.value.priority,
    comments: order.value.comments,
    process_steps: processSteps
  }

  try {
    await $fetch(`${API_BASE_URL}/orders/update_order`, {
      method: 'PUT',
      body: updatedOrder
    })
    await navigateTo('/order/overview')
  } catch (error) {
    console.error('API Error:', error)
  }
}

function cancelEdit() {
  navigateTo('/order/overview')
}

onMounted(() => {
  loadOrder()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Orders · Edit"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Update"
      @reset="cancelEdit"
      @submit="updateOrder"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name
          <input v-model="order.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="order.id" class="input disabled-input" disabled />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Target amount
          <input v-model="order.target" type="number" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Product name
          <input v-model="order.product" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Start date
          <input v-model="order.start" type="date" inputmode="numeric" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          End date
          <input v-model="order.end" type="date" inputmode="numeric" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="order.status" class="input">
            <option>Planned</option>
            <option>Running</option>
            <option>Paused</option>
            <option>Done</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Priority
          <select v-model="order.priority" class="input">
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
          Comments
          <textarea v-model="order.comments" rows="3" class="input" />
        </label>
      </div>

      <div
        class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-900 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
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
          <div class="grid grid-cols-[40px,1.2fr,1.2fr,0.8fr,0.8fr,150px] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <span>Nr</span><span>Name</span><span>Resource</span><span>Setup</span><span>Status</span><span>Action</span>
          </div>
          <div
            v-for="(step, i) in steps"
            :key="i"
            class="grid grid-cols-[40px,1.2fr,1.2fr,0.8fr,0.8fr,150px] gap-2 items-center rounded-lg border p-2 transition-colors"
            :class="isDarkMode
              ? 'border-gray-700 bg-gray-700'
              : 'border-slate-200 bg-slate-50'"
          >
            <span class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ i + 1 }}</span>
            <input v-model="step.name" class="input h-10" />
            <input v-model="step.resource" class="input h-10" />
            <input v-model="step.setupTime" type="time" class="input h-10" />
            <select v-model="step.status" class="input h-10">
              <option>Planned</option>
              <option>Running</option>
              <option>Paused</option>
              <option>Done</option>
            </select>
            <div class="flex gap-2">
              <button
                class="px-2 py-1 text-xs rounded border transition-colors"
                :class="isDarkMode
                  ? 'border-gray-600 hover:bg-gray-600 text-slate-200'
                  : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
                @click="editProcessStep(i)"
              >
                Edit
              </button>
              <button
                class="px-2 py-1 text-xs rounded border transition-colors"
                :class="isDarkMode
                  ? 'border-rose-500/70 text-rose-200 hover:bg-rose-500/10'
                  : 'border-rose-200 text-rose-600 hover:bg-rose-50'"
                @click="removeStep(i)"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
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
